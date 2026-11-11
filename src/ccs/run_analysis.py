"""Read-only, evidence-bounded analysis of completed CCS run artifacts.

The analysis intentionally has a narrower read boundary than reporting.  It
projects selected fields from the manifest, summary, episode result and oracle,
uses the monitor's redacted activity stream for observed tool calls, and asks
``network_view`` for the final operational state.  It never re-creates a
scenario or reads model transcripts, restricted scenarios, configuration XML,
or the oracle's ground-truth details.
"""

from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping

from ccs.monitor import read_activity
from ccs.network_view import read_network
from ccs.scenario_catalog import SCENARIOS


_EPISODE_ID = re.compile(r"^episode-[0-9]{4,8}$")
_ACTIVE_STATUSES = {"STARTING", "LAUNCHING", "RUNNING", "STOPPING"}
_READY_STATUSES = {
    "COMPLETED", "FAILED", "ABORTED", "CANCELLED", "CANCELED",
    "INVALID_ARTIFACT", "INTERRUPTED",
}
_COMPLETE_STATUSES = {"COMPLETED", "FAILED", "INVALID_ARTIFACT"}
_MAX_EPISODES = 500
_MAX_ACTIVITY_BYTES = 16 * 1024 * 1024
_MAX_ACTIVITY_FILES = 256
_MAX_JSON_BYTES = {
    "manifest.json": 8 * 1024 * 1024,
    "summary.json": 4 * 1024 * 1024,
    "integrity.json": 2 * 1024 * 1024,
    "result.json": 4 * 1024 * 1024,
    "oracle.json": 2 * 1024 * 1024,
}
_BLOCKED_KEYS = {
    "authorization", "credential", "credentials", "api_key", "apikey",
    "password", "secret", "token", "raw_response", "thinking",
    "encrypted_content", "encrypted_reasoning", "reasoning_content",
    "ground_truth", "registry",
}

_CAUSE_LABELS: dict[str, dict[str, str]] = {
    "intermediate_switch_failure": {"ko": "중간 스위치 장애", "en": "Intermediate switch failure"},
    "incorrect_default_gateway": {"ko": "기본 게이트웨이 설정 오류", "en": "Incorrect default gateway"},
    "packet_loss_misconfiguration": {"ko": "유선 구간 패킷 손실 설정 오류", "en": "Wired packet-loss misconfiguration"},
    "bandwidth_limit_misconfiguration": {"ko": "대역폭 제한 설정 오류", "en": "Bandwidth-limit misconfiguration"},
    "excessive_delay_misconfiguration": {"ko": "유선 구간 지연 설정 오류", "en": "Wired-delay misconfiguration"},
    "no_fault_detected": {"ko": "관측된 장애 없음", "en": "No fault detected"},
    "unknown": {"ko": "원인 미확인", "en": "Unknown root cause"},
}

_OUTCOME_TEXT: dict[str, dict[str, str]] = {
    "RECOVERED": {"ko": "변경 적용 후 검증을 통과해 서비스가 복구되었습니다.", "en": "The applied change passed verification and service recovered."},
    "NO_CHANGE": {"ko": "정상 상태로 검증되어 구성 변경 없이 종료했습니다.", "en": "Verification found normal service, so the episode finished without a configuration change."},
    "ESCALATED": {"ko": "변경 근거가 없고 검증도 통과하지 못해 에스컬레이션했습니다.", "en": "No justified change was selected and verification did not pass, so the episode was escalated."},
    "ROLLED_BACK": {"ko": "적용한 변경이 검증을 통과하지 못해 롤백했습니다.", "en": "The applied change failed verification and was rolled back."},
    "DECLINED": {"ko": "제안된 변경의 승인이 거부되어 적용하지 않았습니다.", "en": "The proposed change was not applied because approval was declined."},
    "FAILED": {"ko": "실행 오류로 episode가 실패했습니다.", "en": "The episode failed because of an execution error."},
    "ABORTED": {"ko": "실행이 중단되어 부분 결과만 남았습니다.", "en": "The run was aborted and only partial results are available."},
    "UNKNOWN": {"ko": "실행 결과를 확인할 수 없습니다.", "en": "The execution outcome is unavailable."},
}
_OUTCOME_LABEL_KO = {
    "RECOVERED": "복구 완료",
    "NO_CHANGE": "정상 확인·변경 없음",
    "ESCALATED": "추가 조치 필요",
    "ROLLED_BACK": "변경 취소",
    "DECLINED": "변경 승인 거부",
    "FAILED": "처리 실패",
    "ABORTED": "실행 중단",
    "UNKNOWN": "확인 불가",
}

_LIMITATION_TEXT: dict[str, dict[str, str]] = {
    "Synthetic SQLite backend; no real-network validation.": {
        "ko": "Synthetic wired SQLite backend 결과이며 실제 유선망 검증은 아닙니다.",
        "en": "This uses the synthetic wired SQLite backend and is not real wired-network validation.",
    },
    "No disclosure protection.": {
        "ko": "D0 baseline에는 disclosure protection이 적용되지 않았습니다.",
        "en": "The D0 baseline has no disclosure protection enabled.",
    },
    "Model cost estimates use the configured price table.": {
        "ko": "모델 비용은 설정된 가격표를 사용한 추정치입니다.",
        "en": "Model cost is estimated from the configured price table.",
    },
    "Process/path separation is not an OS sandbox.": {
        "ko": "프로세스 및 경로 분리는 OS sandbox가 아닙니다.",
        "en": "Process and path separation do not constitute an OS sandbox.",
    },
}


def _bilingual(ko: str, en: str) -> dict[str, str]:
    return {"ko": ko, "en": en}


def _scenario_projection(fault: str | None) -> dict[str, dict[str, str]] | None:
    source = SCENARIOS.get(fault or "")
    if not isinstance(source, dict):
        return None
    result: dict[str, dict[str, str]] = {}
    for key in ("title", "impact", "goal", "technical"):
        value = source.get(key)
        if not isinstance(value, dict):
            continue
        ko, en = _text(value.get("ko"), 500), _text(value.get("en"), 500)
        if ko and en:
            result[key] = _bilingual(ko, en)
    return result or None


def _finite_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(float(value)) else None


def _text(value: Any, limit: int = 2_000) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.replace("\x00", "").strip()
    if not value:
        return None
    return value if len(value) <= limit else value[:limit] + "…"


def _blocked_key(key: Any) -> bool:
    lowered = str(key).casefold()
    return lowered in _BLOCKED_KEYS or lowered.endswith("_token") or any(
        marker in lowered
        for marker in (
            "authorization", "credential", "password", "api_key", "secret",
            "encrypted_content", "encrypted_reasoning", "raw_response",
            "ground_truth", "registry",
        )
    )


def _compact_json(value: Any, *, depth: int = 0) -> Any:
    """Bound untrusted provider text and suppress secret/truth-bearing keys."""

    if depth > 6:
        return "[detail depth limit]"
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:50]:
            if _blocked_key(key):
                continue
            result[str(key)[:120]] = _compact_json(item, depth=depth + 1)
        if len(value) > 50:
            result["detail_truncated"] = True
        return result
    if isinstance(value, (list, tuple)):
        result = [_compact_json(item, depth=depth + 1) for item in list(value)[:50]]
        if len(value) > 50:
            result.append("[list truncated]")
        return result
    if isinstance(value, str):
        return value if len(value) <= 2_000 else value[:2_000] + "…"
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return _finite_number(value)
    return str(value)[:2_000]


def _safe_json_object(path: Path, *, limit: int) -> tuple[dict[str, Any], str | None]:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            return {}, "missing_or_oversized"
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError):
        return {}, "malformed"
    return (value, None) if isinstance(value, dict) else ({}, "malformed")


def _activity_snapshot(run_dir: Path, run_id: str) -> tuple[list[dict[str, Any]], str | None]:
    directory = run_dir / "activity"
    if directory.is_symlink():
        return [], "unsafe_activity_directory"
    if not directory.is_dir():
        return [], "activity_unavailable"
    try:
        files = [
            path for path in directory.iterdir()
            if path.suffix.casefold() == ".jsonl" and path.is_file() and not path.is_symlink()
        ]
        if len(files) > _MAX_ACTIVITY_FILES or sum(path.stat().st_size for path in files) > _MAX_ACTIVITY_BYTES:
            return [], "activity_limit_exceeded"
        events = read_activity(run_dir)
    except (OSError, RuntimeError, ValueError):
        return [], "activity_unavailable"
    return [
        event for event in events[-20_000:]
        if isinstance(event, dict) and event.get("run_id") in {"", run_id}
    ], None


def _manifest_episode(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    episode_id = value.get("episode_id")
    if not isinstance(episode_id, str) or _EPISODE_ID.fullmatch(episode_id) is None:
        return None
    return value


def _episode_events(events: list[dict[str, Any]], episode_id: str) -> list[dict[str, Any]]:
    return [event for event in events if event.get("episode_id") == episode_id]


def _request_and_target(events: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    for event in events:
        if event.get("action") not in {"episode", "request_received"}:
            continue
        details = event.get("details")
        request = details.get("request") if isinstance(details, dict) else None
        if not isinstance(request, dict):
            continue
        return _text(request.get("summary")), _text(request.get("target"), 160)
    return None, None


def _change_projection(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    target, param = _text(value.get("target"), 160), _text(value.get("param"), 160)
    if not target or not param:
        return None
    result = {"target": target, "param": param, "value": _compact_json(value.get("value"))}
    reason = _text(value.get("reason"))
    if reason is not None:
        result["reason"] = reason
    return result


def _diagnosis_projection(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    root_cause = _text(source.get("root_cause"), 200) or "unknown"
    label = _CAUSE_LABELS.get(root_cause)
    if label is None:
        readable = root_cause.replace("_", " ").strip().capitalize() or "Unknown root cause"
        label = {"ko": f"보고된 원인: {readable}", "en": readable}
    confidence = _finite_number(source.get("confidence"))
    return {
        "root_cause": root_cause,
        "root_cause_label": dict(label),
        "evidence": _compact_json(source.get("evidence", [])),
        "confidence": confidence,
        "confidence_kind": "provider_reported_uncalibrated" if confidence is not None else None,
        "proposed_change": _change_projection(source.get("proposed_change")),
        "notes": _text(source.get("notes")) or "",
    }


def _verify_projection(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    checks = []
    for raw in value.get("checks", []) if isinstance(value.get("checks"), list) else []:
        if not isinstance(raw, dict):
            continue
        item = {}
        for key in (
            "name", "passed", "value", "observed", "expected", "threshold",
            "path", "intermediate_switch",
            "admin_state", "default_gateway", "throughput_mbps", "latency_ms",
            "packet_loss_pct", "reachability_pct",
        ):
            if key in raw:
                item[key] = _compact_json(raw[key])
        if item:
            checks.append(item)
    result: dict[str, Any] = {
        "target": _text(value.get("target"), 160),
        "passed": value.get("passed") if type(value.get("passed")) is bool else None,
        "checks": checks,
    }
    state_version = _finite_number(value.get("state_version"))
    if state_version is not None:
        result["state_version"] = state_version
    return result


def _report_projection(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    result = {}
    for key in ("summary", "root_cause", "action", "outcome"):
        text = _text(value.get(key))
        if text is not None:
            result[key] = text
    if isinstance(value.get("evidence"), list):
        result["evidence"] = _compact_json(value["evidence"])
    return result or None


def _oracle_projection(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    utility = _finite_number(value.get("utility"))
    verified = value.get("verified") if type(value.get("verified")) is bool else None
    forbidden = value.get("forbidden_changes")
    result = {
        "utility": utility,
        "verified": verified,
        "forbidden_change_count": len(forbidden) if isinstance(forbidden, list) else None,
    }
    if isinstance(forbidden, list):
        result["forbidden_changes"] = _compact_json(forbidden)
    return result


def _actual_configuration_changes(network: Mapping[str, Any]) -> list[dict[str, Any]]:
    changes = []
    raw_changes = network.get("changes", [])
    if not isinstance(raw_changes, list):
        return changes
    for raw in raw_changes[:100]:
        if not isinstance(raw, dict):
            continue
        target, param = _text(raw.get("target"), 160), _text(raw.get("param"), 160)
        if not target or not param:
            continue
        changes.append(
            {
                "target": target,
                "param": param,
                "before": _compact_json(raw.get("before")),
                "after": _compact_json(raw.get("after")),
                "status": _text(raw.get("status"), 80) or "unknown",
            }
        )
    return changes


def _is_client_tool_event(event: Mapping[str, Any], status: str | None = None) -> bool:
    details = event.get("details")
    return (
        event.get("component") == "mcp"
        and event.get("action") == "call"
        and (status is None or event.get("status") == status)
        and isinstance(details, dict)
        and details.get("role") in {"operation", "diagnosis"}
    )


def _before_kpis(events: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    first_change = len(events)
    for index, event in enumerate(events):
        details = event.get("details")
        if (
            _is_client_tool_event(event, "started")
            and isinstance(details, dict)
            and details.get("tool") in {"apply_change", "rollback_change"}
        ):
            first_change = index
            break
    samples: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events[:first_change]:
        if not _is_client_tool_event(event, "succeeded"):
            continue
        details = event["details"]
        if details.get("tool") != "get_kpi" or not isinstance(details.get("result"), dict):
            continue
        result = details["result"]
        target = _text(result.get("target"), 160)
        if not target or not isinstance(result.get("samples"), list):
            continue
        for sample in result["samples"]:
            if not isinstance(sample, dict):
                continue
            metric = _text(sample.get("metric"), 160)
            value = _finite_number(sample.get("value"))
            if metric and value is not None:
                samples[(target, metric)] = {
                    "value": value,
                    "unit": _text(sample.get("unit"), 80),
                    "status": _text(sample.get("status"), 80),
                }
    return samples


def _final_kpis_for_targets(
    episode_dir: Path, targets: set[str]
) -> dict[tuple[str, str], dict[str, Any]]:
    """Read final KPI values for exact pre-change targets without mutating SQLite."""

    database = episode_dir / "network.sqlite"
    final_state = episode_dir / "final-state.restricted.json"
    if (
        not targets
        or episode_dir.is_symlink()
        or database.is_symlink()
        or final_state.is_symlink()
        or not database.is_file()
        or not final_state.is_file()
    ):
        return {}
    from ccs.network_view import _ReadOnlyBackend, _kpis

    backend = None
    samples: dict[tuple[str, str], dict[str, Any]] = {}
    try:
        backend = _ReadOnlyBackend(database)
        for target in sorted(targets):
            raw = backend.call("get_kpi", {"target": target})
            for sample in _kpis(raw):
                metric = _text(sample.get("metric"), 160)
                value = _finite_number(sample.get("value"))
                observed_target = _text(sample.get("target"), 160)
                if observed_target == target and metric and value is not None:
                    samples[(target, metric)] = {
                        "value": value,
                        "unit": _text(sample.get("unit"), 80),
                        "status": _text(sample.get("status"), 80),
                        "source": "final_state_read",
                    }
    except Exception:
        return {}
    finally:
        if backend is not None:
            backend.close()
    return samples


def _after_kpis(
    network: Mapping[str, Any], verify: Mapping[str, Any] | None,
    exact_final: Mapping[tuple[str, str], dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    samples: dict[tuple[str, str], dict[str, Any]] = {}
    raw = network.get("kpis", [])
    if isinstance(raw, list):
        for sample in raw:
            if not isinstance(sample, dict):
                continue
            target = _text(sample.get("target"), 160)
            metric = _text(sample.get("metric"), 160)
            value = _finite_number(sample.get("value"))
            if target and metric and value is not None:
                samples[(target, metric)] = {
                    "value": value,
                    "unit": _text(sample.get("unit"), 80),
                    "status": _text(sample.get("status"), 80),
                    "source": "final_state_read",
                }
    if isinstance(verify, Mapping):
        target = _text(verify.get("target"), 160)
        checks = verify.get("checks", [])
        if target and isinstance(checks, list):
            for check in checks:
                if not isinstance(check, dict):
                    continue
                name = check.get("name")
                metric = {
                    "throughput": ("throughput_mbps", "Mbps"),
                    "latency": ("latency_ms", "ms"),
                    "packet_loss": ("packet_loss_pct", "percent"),
                    "reachability": ("reachability_pct", "percent"),
                }.get(name)
                value = _finite_number(check.get("value"))
                if metric is not None and value is not None:
                    samples.setdefault(
                        (target, metric[0]),
                        {"value": value, "unit": metric[1], "status": None, "source": "actual_verify_check"},
                    )
                for field, metric, unit in (
                    ("throughput_mbps", "throughput_mbps", "Mbps"),
                    ("latency_ms", "latency_ms", "ms"),
                    ("packet_loss_pct", "packet_loss_pct", "percent"),
                    ("reachability_pct", "reachability_pct", "percent"),
                ):
                    value = _finite_number(check.get(field))
                    if value is not None:
                        samples.setdefault(
                            (target, metric),
                            {"value": value, "unit": unit, "status": None, "source": "actual_verify_check"},
                        )
    samples.update(exact_final)
    return samples


def _kpi_changes(
    events: list[dict[str, Any]], network: Mapping[str, Any], verify: Mapping[str, Any] | None,
    episode_dir: Path, *, final_state_ready: bool,
) -> list[dict[str, Any]]:
    before = _before_kpis(events)
    exact_final = (
        _final_kpis_for_targets(episode_dir, {target for target, _ in before})
        if final_state_ready
        else {}
    )
    after = _after_kpis(network, verify, exact_final)
    changes = []
    for (target, metric), initial in sorted(before.items()):
        final = after.get((target, metric))
        changes.append(
            {
                "target": target,
                "metric": metric,
                "before": initial["value"],
                "after": final["value"] if final is not None else None,
                "unit": initial.get("unit") or (final or {}).get("unit"),
                "before_status": initial.get("status"),
                "after_status": (final or {}).get("status"),
                "before_source": "observed_get_kpi",
                "after_source": final.get("source") if final is not None else None,
            }
        )
    return changes


def _activity_counts(events: list[dict[str, Any]]) -> dict[str, Any]:
    components = Counter(str(event.get("component", "runner")) for event in events)
    statuses = Counter(str(event.get("status", "info")) for event in events)
    retrieval = {
        "runbook_queries": 0,
        "runbook_hits": 0,
        "runbook_disabled": 0,
        "memory_queries": 0,
        "memory_hits": 0,
        "memory_disabled": 0,
    }
    tool_roles = Counter()
    a2a_handoffs = 0
    for event in events:
        component, action, status = event.get("component"), event.get("action"), event.get("status")
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        if component in {"runbook", "memory"} and action == "search" and status in {"succeeded", "failed", "skipped"}:
            prefix = "runbook" if component == "runbook" else "memory"
            if details.get("disabled") is True or status == "skipped":
                retrieval[prefix + "_disabled"] += 1
            else:
                retrieval[prefix + "_queries"] += 1
                results = details.get("results")
                if isinstance(results, list):
                    retrieval[prefix + "_hits"] += len(results)
        if _is_client_tool_event(event, "started"):
            tool_roles[str(details["role"])] += 1
        if (
            component == "a2a" and action == "delegate_diagnosis" and status == "started"
            and details.get("from") == "operation" and details.get("to") == "diagnosis"
        ):
            a2a_handoffs += 1
    return {
        "events": len(events),
        "by_component": dict(sorted(components.items())),
        "by_status": dict(sorted(statuses.items())),
        **retrieval,
        "tool_calls": {
            "operation": tool_roles["operation"],
            "diagnosis": tool_roles["diagnosis"],
            "total": tool_roles["operation"] + tool_roles["diagnosis"],
        },
        "a2a_handoffs": a2a_handoffs,
    }


def _summary_projection(summary: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in (
        "episodes", "completed_episodes", "successful_episodes", "diagnoses_correct",
        "api_calls", "input_tokens", "output_tokens", "estimated_cost_usd", "mode", "models",
    ):
        if key in summary:
            result[key] = _compact_json(summary[key])
    return result


def _conditions_projection(
    manifest: Mapping[str, Any], summary: Mapping[str, Any], controller: Mapping[str, Any]
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    source = controller.get("conditions") if isinstance(controller.get("conditions"), dict) else {}
    input_conditions = summary.get("input_conditions") if isinstance(summary.get("input_conditions"), dict) else {}
    metadata = input_conditions.get("experiment_metadata") if isinstance(input_conditions.get("experiment_metadata"), dict) else {}
    web_console = metadata.get("web_console") if isinstance(metadata.get("web_console"), dict) else {}
    saved = web_console.get("conditions") if isinstance(web_console.get("conditions"), dict) else {}
    combined = dict(saved)
    combined.update(source)
    for key in (
        "mode", "profile", "faults", "seeds", "repeat", "difficulty", "approval",
        "rag_enabled", "memory_enabled", "runbook_k", "memory_k", "runbook_count",
        "memory_count", "delay_seconds", "diagnosis_tool_budget", "context_steps",
        "max_agent_steps",
    ):
        value = combined.get(key)
        if value is not None:
            result[key] = _compact_json(value)
    for key in ("mode", "faults", "seeds", "repeat"):
        if key not in result and key in manifest:
            result[key] = _compact_json(manifest[key])
    if "runbook_count" not in result and isinstance(input_conditions.get("runbooks"), dict):
        result["runbook_count"] = _finite_number(input_conditions["runbooks"].get("count"))
    if "memory_count" not in result and isinstance(input_conditions.get("initial_memory"), dict):
        result["memory_count"] = _finite_number(input_conditions["initial_memory"].get("count"))
    if "rag_enabled" not in result and type(input_conditions.get("rag_enabled")) is bool:
        result["rag_enabled"] = input_conditions["rag_enabled"]
    if "memory_enabled" not in result and type(input_conditions.get("memory_enabled")) is bool:
        result["memory_enabled"] = input_conditions["memory_enabled"]
    pacing = input_conditions.get("pacing") if isinstance(input_conditions.get("pacing"), dict) else {}
    if "delay_seconds" not in result:
        delay = _finite_number(pacing.get("initial_delay_seconds"))
        if delay is not None:
            result["delay_seconds"] = delay
    return result


def _timing_projection(summary: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    timing = summary.get("timing") if isinstance(summary.get("timing"), dict) else manifest.get("timing")
    if not isinstance(timing, dict):
        return {}
    result = {}
    for key in (
        "elapsed_wall_seconds", "delay_union_seconds",
        "elapsed_minus_delay_union_seconds_estimate", "initial_delay_seconds",
        "final_delay_seconds", "delayed_event_count", "delay_change_history",
        "measurement_boundary",
    ):
        if key in timing:
            result[key] = _compact_json(timing[key])
    return result


def _episode_observations(
    outcome: str, diagnosis: Mapping[str, Any], changes: list[dict[str, Any]],
    kpis: list[dict[str, Any]], oracle: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    observations = [{"kind": "execution_outcome", "text": dict(_OUTCOME_TEXT.get(outcome, _OUTCOME_TEXT["UNKNOWN"]))}]
    if diagnosis.get("confidence") is not None:
        confidence = diagnosis["confidence"]
        observations.append(
            {
                "kind": "provider_confidence",
                "text": _bilingual(
                    f"모델이 스스로 표시한 확신 정도는 {confidence}입니다. 실제 정답률을 측정한 값은 아닙니다.",
                    f"The provider reported confidence {confidence}; this is not calibrated accuracy.",
                ),
            }
        )
    if outcome == "NO_CHANGE" and not changes:
        observations.append(
            {
                "kind": "normal_no_action",
                "text": _bilingual(
                    "망 상태가 정상임을 확인했고 설정을 바꾸지 않았습니다.",
                    "The N0 normal condition passed verification and has no actual configuration change record.",
                ),
            }
        )
    elif changes:
        observations.append(
            {
                "kind": "actual_changes",
                "text": _bilingual(
                    f"실제 시스템에 남은 설정 변경 기록은 {len(changes)}건입니다.",
                    f"The NetworkBackend recorded {len(changes)} actual configuration change(s).",
                ),
            }
        )
    known_after = sum(item.get("after") is not None for item in kpis)
    if kpis:
        observations.append(
            {
                "kind": "observed_kpis",
                "text": _bilingual(
                    f"같은 대상의 상태 지표 {len(kpis)}개를 변경 전후로 비교했으며, 최종 값을 확인한 지표는 {known_after}개입니다. 확인하지 못한 값은 비워 두었습니다.",
                    f"Of {len(kpis)} pre-change get_kpi observations, {known_after} have a post-change observation for the same target and metric; the rest remain unknown.",
                ),
            }
        )
    if isinstance(oracle, Mapping) and oracle.get("utility") is not None:
        observations.append(
            {
                "kind": "oracle_utility",
                "text": _bilingual(
                    f"에이전트의 보고와 별도로 최종 망 상태를 검사한 점수는 {oracle['utility']}입니다. 작업 완료 여부와는 별도로 봐야 합니다.",
                    f"Oracle utility is {oracle['utility']} and is separate from the execution outcome.",
                ),
            }
        )
    return observations


def _limitations(
    summary: Mapping[str, Any], *, activity_issue: str | None, artifact_issues: list[str],
    sealed: bool, status: str, confidence_present: bool,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(code: str, text: dict[str, str]) -> None:
        if code not in seen:
            result.append({"code": code, "text": text})
            seen.add(code)

    raw = summary.get("limitations")
    if isinstance(raw, list):
        for index, item in enumerate(raw[:20]):
            if not isinstance(item, str):
                continue
            translated = _LIMITATION_TEXT.get(item, _bilingual(item, item))
            add(f"summary_{index}", translated)
    timing = summary.get("timing")
    if isinstance(timing, dict) and timing.get("elapsed_minus_delay_union_seconds_estimate") is not None:
        add(
            "timing_estimate",
            _bilingual(
                "Delay 제외 시간은 관측된 delay union을 뺀 추정치이며 독립적인 No Delay benchmark가 아닙니다.",
                "Time excluding delay is an estimate from the observed delay union, not an independent No Delay benchmark.",
            ),
        )
    if confidence_present:
        add(
            "uncalibrated_confidence",
            _bilingual(
                "모델이 표시한 확신 정도는 실제 정답률을 측정한 값이 아닙니다.",
                "Diagnosis confidence is provider-reported and is not calibrated accuracy.",
            ),
        )
    if activity_issue:
        add(
            activity_issue,
            _bilingual(
                "Safe activity가 없거나 크기 제한을 넘어 tool/retrieval 집계를 확인할 수 없습니다.",
                "Safe activity was unavailable or exceeded the read limit, so tool and retrieval counts are unavailable.",
            ),
        )
    if artifact_issues:
        add(
            "partial_or_malformed_artifacts",
            _bilingual(
                "일부 허용 artifact가 없거나 손상되어 해당 값은 unknown으로 남겼습니다.",
                "One or more allowed artifacts were missing or malformed, so affected values remain unknown.",
            ),
        )
    if not sealed:
        add(
            "not_recorded_as_sealed",
            _bilingual(
                "저장된 결과 검사 기록과 결과 파일 해시를 모두 확인할 수 없어 완료된 보존 결과로 표시하지 않습니다.",
                "This result is not marked sealed because valid recorded integrity and artifact hashes were not both available.",
            ),
        )
    if status in {"ABORTED", "CANCELLED", "CANCELED", "INTERRUPTED"}:
        add(
            "partial_terminal_run",
            _bilingual(
                "중단된 실행의 부분 분석이며 누락 값은 성공 또는 실패로 추정하지 않습니다.",
                "This is a partial analysis of an interrupted run; missing values are not inferred as success or failure.",
            ),
        )
    add(
        "recorded_integrity_only",
        _bilingual(
            "실행이 끝날 때 저장된 결과 검사 기록을 표시합니다. 이 화면을 열 때 모든 결과 파일을 다시 검사한 것은 아닙니다.",
            "Integrity uses the run's recorded integrity.json; this endpoint does not revalidate every artifact.",
        ),
    )
    return result


def _insights(episodes: list[dict[str, Any]], sealed: bool) -> list[dict[str, Any]]:
    outcomes = Counter(str(item.get("outcome", "UNKNOWN")) for item in episodes)
    rendered = ", ".join(f"{key}={value}" for key, value in sorted(outcomes.items())) or "none"
    rendered_ko = ", ".join(
        f"{_OUTCOME_LABEL_KO.get(key, '확인 불가')} {value}건"
        for key, value in sorted(outcomes.items())
    ) or "결과 없음"
    changes = sum(len(item.get("configuration_changes", [])) for item in episodes)
    utilities = [
        item["oracle"]["utility"] for item in episodes
        if isinstance(item.get("oracle"), dict) and item["oracle"].get("utility") is not None
    ]
    insights = [
        {
            "kind": "outcome_distribution",
            "title": _bilingual("처리 결과", "Execution outcomes"),
            "text": _bilingual(f"처리 결과는 {rendered_ko}입니다.", f"Episode outcome counts: {rendered}"),
        },
        {
            "kind": "configuration_changes",
            "title": _bilingual("설정 변경 기록", "Actual configuration changes"),
            "text": _bilingual(
                f"실제 시스템에 남은 설정 변경 기록은 총 {changes}건입니다.",
                f"NetworkBackend contains {changes} actual change record(s).",
            ),
        },
    ]
    if utilities:
        mean = sum(float(value) for value in utilities) / len(utilities)
        insights.append(
            {
                "kind": "oracle_utility",
                "title": _bilingual("독립적인 망 상태 검증", "Oracle utility"),
                "text": _bilingual(
                    f"에이전트의 보고와 별도로 최종 망 상태를 검사한 {len(utilities)}건의 평균 점수는 {mean:.3f}입니다. 작업 완료 여부와는 별도로 봐야 합니다.",
                    f"Mean oracle utility is {mean:.3f} across {len(utilities)} episode(s); it is separate from execution completion.",
                ),
            }
        )
    insights.append(
        {
            "kind": "integrity",
            "title": _bilingual("저장된 결과 검사", "Artifact status"),
            "text": _bilingual(
                "실행이 끝날 때 저장된 검사 기록은 정상이고 결과 파일 해시가 포함되어 있습니다. 이 화면에서 다시 검사한 결과는 아닙니다."
                if sealed
                else "저장된 검사 기록과 결과 파일 해시를 모두 확인할 수 없습니다.",
                "Recorded integrity and artifact hashes are present." if sealed else "A complete recorded seal was not available.",
            ),
        }
    )
    return insights


def analyze_run(
    run_dir: Path,
    *,
    controller_status: str | None = None,
    controller_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a bounded, deterministic analysis without modifying ``run_dir``."""

    raw_root = Path(run_dir)
    if raw_root.is_symlink() or not raw_root.is_dir():
        raise ValueError("run_dir must be a regular directory")
    root = raw_root.resolve()
    controller = dict(controller_record or {})
    manifest, manifest_issue = _safe_json_object(
        root / "manifest.json", limit=_MAX_JSON_BYTES["manifest.json"]
    )
    summary, summary_issue = _safe_json_object(
        root / "summary.json", limit=_MAX_JSON_BYTES["summary.json"]
    )
    integrity, integrity_issue = _safe_json_object(
        root / "integrity.json", limit=_MAX_JSON_BYTES["integrity.json"]
    )
    run_id = manifest.get("run_id") if isinstance(manifest.get("run_id"), str) else root.name
    if run_id != root.name:
        run_id = root.name

    controller_state = str(controller_status or "").upper()
    artifact_state = str(manifest.get("status") or summary.get("status") or "UNKNOWN").upper()
    status = controller_state or artifact_state
    active = controller_state in _ACTIVE_STATUSES
    ready = False if active else status in _READY_STATUSES or (not controller_state and artifact_state in _READY_STATUSES)
    complete = ready and status in _COMPLETE_STATUSES
    recorded_valid = integrity.get("valid") if type(integrity.get("valid")) is bool else None
    artifact_hashes = manifest.get("artifact_hashes")
    sealed = bool(
        complete
        and recorded_valid is True
        and isinstance(artifact_hashes, dict)
        and artifact_hashes
    )

    # The manifest becomes terminal before reporting, snapshots and sealing are
    # done.  While the controller still owns the run (or a saved run is still
    # non-terminal), return only a stable readiness envelope and avoid racing
    # episode files or opening the live SQLite database.
    if not ready:
        return {
            "run_id": run_id,
            "status": status,
            "ready": False,
            "complete": False,
            "sealed": False,
            "integrity": {
                "valid": recorded_valid,
                "source": "recorded_integrity" if integrity else "unavailable",
                "live_verified": False,
                "event_count": integrity.get("event_count") if isinstance(integrity.get("event_count"), int) else None,
                "error_count": len(integrity.get("errors", [])) if isinstance(integrity.get("errors"), list) else None,
            },
            "summary": _summary_projection(summary),
            "conditions": _conditions_projection(manifest, summary, controller),
            "timing": _timing_projection(summary, manifest),
            "episodes": [],
            "insights": [],
            "limitations": [
                {
                    "code": "analysis_not_ready",
                    "text": _bilingual(
                        "Controller가 실행 종료와 artifact 정리를 완료한 뒤 분석할 수 있습니다.",
                        "Analysis becomes available after the controller finishes the run and artifact cleanup.",
                    ),
                }
            ],
            "activity_counts": _activity_counts([]),
        }

    events, activity_issue = _activity_snapshot(root, run_id)
    by_manifest: dict[str, dict[str, Any]] = {}
    for item in manifest.get("episodes", []) if isinstance(manifest.get("episodes"), list) else []:
        episode = _manifest_episode(item)
        if episode is not None and len(by_manifest) < _MAX_EPISODES:
            by_manifest[episode["episode_id"]] = episode
    episode_ids = list(by_manifest)
    for event in events:
        episode_id = event.get("episode_id")
        if (
            isinstance(episode_id, str) and _EPISODE_ID.fullmatch(episode_id)
            and episode_id not in episode_ids and len(episode_ids) < _MAX_EPISODES
        ):
            episode_ids.append(episode_id)

    artifact_issues = [
        item for item in (manifest_issue, summary_issue, integrity_issue) if item is not None
    ]
    episodes: list[dict[str, Any]] = []
    for episode_id in episode_ids:
        directory = root / "episodes" / episode_id
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            artifact_issues.append(f"unsafe:{episode_id}")
            continue
        result, result_issue = _safe_json_object(
            directory / "result.json", limit=_MAX_JSON_BYTES["result.json"]
        )
        oracle_raw, oracle_issue = _safe_json_object(
            directory / "oracle.json", limit=_MAX_JSON_BYTES["oracle.json"]
        )
        if result_issue:
            artifact_issues.append(f"{episode_id}:result:{result_issue}")
        if oracle_issue:
            artifact_issues.append(f"{episode_id}:oracle:{oracle_issue}")
        current_events = _episode_events(events, episode_id)
        request, target = _request_and_target(current_events)
        network: dict[str, Any] = {}
        if directory.is_dir() and not directory.is_symlink():
            try:
                candidate = read_network(root, episode_id=episode_id)
                if isinstance(candidate, dict) and candidate.get("run_id") == run_id:
                    network = candidate
            except (OSError, RuntimeError, TypeError, ValueError):
                network = {}
        if target is None:
            target = _text(network.get("target"), 160)
        manifest_episode = by_manifest.get(episode_id, {})
        outcome = str(result.get("outcome") or manifest_episode.get("outcome") or "UNKNOWN").upper()
        if outcome not in _OUTCOME_TEXT:
            outcome = "UNKNOWN"
        diagnosis = _diagnosis_projection(result.get("diagnosis"))
        selected_change = _change_projection(result.get("change"))
        verify = _verify_projection(result.get("verify"))
        oracle = _oracle_projection(oracle_raw) if oracle_raw else None
        changes = _actual_configuration_changes(network)
        kpis = _kpi_changes(
            current_events,
            network,
            verify,
            directory,
            final_state_ready=complete and network.get("available") is True,
        )
        fault = _text(manifest_episode.get("fault"), 80) or _text(network.get("fault"), 80)
        episode = {
            "episode_id": episode_id,
            "fault": fault,
            "scenario": _scenario_projection(fault),
            "seed": manifest_episode.get("seed") if isinstance(manifest_episode.get("seed"), int) else network.get("seed"),
            "outcome": outcome,
            "request": request,
            "target": target,
            "diagnosis": diagnosis,
            "change": selected_change,
            "verify": verify,
            "oracle": oracle,
            "report": _report_projection(result.get("report")),
            "memory_written": result.get("memory_written") if type(result.get("memory_written")) is bool else manifest_episode.get("memory_written"),
            "configuration_changes": changes,
            "kpi_changes": kpis,
        }
        episode["observations"] = _episode_observations(outcome, diagnosis, changes, kpis, oracle)
        episodes.append(episode)

    confidence_present = any(item["diagnosis"].get("confidence") is not None for item in episodes)
    return {
        "run_id": run_id,
        "status": status,
        "ready": ready,
        "complete": complete,
        "sealed": sealed,
        "integrity": {
            "valid": recorded_valid,
            "source": "recorded_integrity" if integrity else "unavailable",
            "live_verified": False,
            "event_count": integrity.get("event_count") if isinstance(integrity.get("event_count"), int) else None,
            "error_count": len(integrity.get("errors", [])) if isinstance(integrity.get("errors"), list) else None,
        },
        "summary": _summary_projection(summary),
        "conditions": _conditions_projection(manifest, summary, controller),
        "timing": _timing_projection(summary, manifest),
        "episodes": episodes,
        "insights": _insights(episodes, sealed),
        "limitations": _limitations(
            summary,
            activity_issue=activity_issue,
            artifact_issues=artifact_issues,
            sealed=sealed,
            status=status,
            confidence_present=confidence_present,
        ),
        "activity_counts": _activity_counts(events),
    }
