"""Stable, display-only routing for curated activity events.

This module never changes the recorded activity JSONL.  It derives a small
presentation envelope from fields already admitted by the monitor so the UI can
connect a timeline row to the corresponding topology route and node stage.
"""

from __future__ import annotations

from typing import Any


ROUTES = {
    "request",
    "rag",
    "memory",
    "delegate",
    "return",
    "op_mcp",
    "diag_mcp",
    "report",
    "internal",
}

NODES = {"human", "operation", "diagnosis", "runbook", "memory", "tools"}

SUBMODULES = {
    "human": {"request", "report"},
    "operation": {"context", "action", "approval", "report"},
    "diagnosis": {"inspect", "evidence", "conclusion"},
    "runbook": {"search", "result"},
    "memory": {"read", "draft", "write"},
    "tools": {"read", "preview", "apply", "verify", "rollback"},
}

_STATUS_KO = {
    "started": "시작",
    "waiting": "대기",
    "succeeded": "완료",
    "failed": "실패",
    "skipped": "생략",
    "info": "기록",
}
_STATUS_EN = {
    "started": "started",
    "waiting": "waiting",
    "succeeded": "completed",
    "failed": "failed",
    "skipped": "skipped",
    "info": "recorded",
}


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _target(details: dict[str, Any]) -> str:
    arguments = _mapping(details.get("arguments"))
    request = _mapping(details.get("request"))
    incident = _mapping(details.get("incident"))
    change = _mapping(details.get("change"))
    diagnosis = _mapping(details.get("diagnosis"))
    proposed = _mapping(diagnosis.get("proposed_change"))
    result = _mapping(details.get("result"))
    return _first_string(
        arguments.get("target"),
        request.get("target"),
        incident.get("target"),
        change.get("target"),
        proposed.get("target"),
        result.get("target"),
        details.get("target"),
    )


def _result_count(details: dict[str, Any]) -> int | None:
    for key in ("results", "tools", "evidence", "alarms", "items", "nodes", "sessions"):
        value = details.get(key)
        if isinstance(value, list):
            return len(value)
    result = details.get("result")
    if isinstance(result, dict):
        for key in ("results", "tools", "evidence", "alarms", "items", "nodes", "sessions"):
            value = result.get(key)
            if isinstance(value, list):
                return len(value)
    return None


def _tool_stage(tool: str) -> str:
    if tool == "preview_change":
        return "preview"
    if tool in {"apply_change", "update_ticket"}:
        return "apply"
    if tool == "verify_service":
        return "verify"
    if tool == "rollback_change":
        return "rollback"
    return "read"


def _payload(
    *,
    route: str,
    node: str,
    submodule: str,
    actor: str,
    headline_ko: str,
    headline_en: str,
    detail_ko: str,
    detail_en: str,
    tool: str = "",
    target: str = "",
    result_count: int | None = None,
    generic: bool = False,
    track_active: bool = True,
) -> dict[str, Any]:
    if route not in ROUTES:
        raise ValueError(f"unsupported presentation route: {route}")
    if node not in NODES or submodule not in SUBMODULES[node]:
        raise ValueError(f"unsupported presentation stage: {node}/{submodule}")
    return {
        "route": route,
        "node": node,
        "submodule": submodule,
        "actor": actor,
        "headline": {"ko": headline_ko, "en": headline_en},
        "detail": {"ko": detail_ko, "en": detail_en},
        "tool": tool,
        "target": target,
        "result_count": result_count,
        "generic": generic,
        "track_active": track_active,
    }


def _presentation_for_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return bilingual topology and timeline metadata for one safe event."""

    component = _string(event.get("component")).casefold()
    action = _string(event.get("action")).casefold()
    status = _string(event.get("status")).casefold() or "info"
    details = _mapping(event.get("details"))
    target = _target(details)
    count = _result_count(details)
    ko_status = _STATUS_KO.get(status, "기록")
    en_status = _STATUS_EN.get(status, "recorded")

    if component == "operation":
        if action == "request_received":
            subject = f" · {target}" if target else ""
            return _payload(
                route="request", node="operation", submodule="context", actor="Human Operator → Operation Agent",
                headline_ko=f"운영 요청 접수{subject}", headline_en=f"Operator request received{subject}",
                detail_ko="Operation Agent가 운영 요청 정보를 기록했습니다.",
                detail_en="The Operation Agent recorded the operator request.", target=target,
            )
        if action in {"collect_context", "diagnosis_received"}:
            noun_ko = "진단 결과 수신" if action == "diagnosis_received" else "진단 컨텍스트 준비"
            noun_en = "Diagnosis received" if action == "diagnosis_received" else "Diagnosis context preparation"
            if action == "diagnosis_received":
                detail_ko = "Diagnosis Agent가 반환한 결론과 근거를 전달받았습니다."
                detail_en = "Received the conclusion and evidence returned by the Diagnosis Agent."
            elif status in {"started", "waiting"}:
                detail_ko = f"대상 {target}의 요청과 관측 정보를 정리하고 있습니다." if target else "요청과 관측 정보를 진단 컨텍스트로 정리하고 있습니다."
                detail_en = f"Preparing request and observation context for {target}." if target else "Preparing request and observation context for diagnosis."
            elif status == "succeeded":
                detail_ko = f"대상 {target}의 진단 컨텍스트를 준비했습니다." if target else "요청과 관측 정보로 진단 컨텍스트를 준비했습니다."
                detail_en = f"Prepared diagnosis context for {target}." if target else "Prepared diagnosis context from the request and observations."
            elif status == "failed":
                detail_ko = "진단 컨텍스트 준비에 실패했습니다."
                detail_en = "Diagnosis context preparation failed."
            else:
                detail_ko = "진단 컨텍스트 준비 상태를 기록했습니다."
                detail_en = "Recorded the diagnosis context preparation state."
            return _payload(
                route="return" if action == "diagnosis_received" else "internal",
                node="operation", submodule="context", actor="Operation Agent",
                headline_ko=f"{noun_ko} · {ko_status}", headline_en=f"{noun_en} · {en_status}",
                detail_ko=detail_ko,
                detail_en=detail_en,
                target=target,
            )
        if action in {"select_change", "action_selected"}:
            return _payload(
                route="internal", node="operation", submodule="action", actor="Operation Agent",
                headline_ko=f"조치 선택 · {ko_status}", headline_en=f"Action selection · {en_status}",
                detail_ko=(f"대상 {target}에 적용할 조치 후보를 검토했습니다." if target else "진단 근거에 따라 조치 후보를 검토했습니다."),
                detail_en=(f"Reviewed a candidate action for {target}." if target else "Reviewed a candidate action against the diagnosis evidence."),
                target=target,
            )
        if action == "approval":
            policy = _string(details.get("policy"))
            suffix = f" ({policy})" if policy else ""
            return _payload(
                route="internal", node="operation", submodule="approval", actor="Human Operator / Operation Agent",
                headline_ko=f"변경 승인{suffix} · {ko_status}", headline_en=f"Change approval{suffix} · {en_status}",
                detail_ko="기록된 승인 정책에 따라 변경 진행 여부를 확인했습니다.",
                detail_en="Checked whether the change may proceed under the recorded approval policy.",
            )
        if action in {"compose_report", "report_delivered"}:
            outcome = _first_string(details.get("verified_execution_outcome"), _mapping(details.get("report")).get("outcome"))
            concrete = f" · {outcome}" if outcome else ""
            return _payload(
                route="report" if action == "report_delivered" else "internal",
                node="operation", submodule="report", actor="Operation Agent → Human Operator" if action == "report_delivered" else "Operation Agent",
                headline_ko=f"운영 보고{concrete} · {ko_status}", headline_en=f"Incident report{concrete} · {en_status}",
                detail_ko=(f"검증된 실행 결과 {outcome}을 보고했습니다." if outcome else "관측된 실행 사실로 운영 보고서를 작성했습니다."),
                detail_en=(f"Reported the verified execution outcome {outcome}." if outcome else "Prepared the incident report from observed execution facts."),
            )

    if component == "diagnosis" and action == "investigate":
        if status in {"started", "waiting"}:
            submodule = "inspect"
            headline_ko, headline_en = "진단 조사", "Diagnosis inspection"
            detail_ko, detail_en = "Diagnosis Agent가 전달된 요청과 관측 정보를 확인하고 있습니다.", "The Diagnosis Agent is inspecting the delegated request and observations."
        elif status == "succeeded":
            submodule = "conclusion"
            headline_ko, headline_en = "근거 기반 진단 결론", "Evidence-based diagnosis conclusion"
            root_cause = _string(details.get("root_cause"))
            detail_ko = f"기록된 root cause: {root_cause}" if root_cause else "근거와 함께 진단 결론을 제출했습니다."
            detail_en = f"Recorded root cause: {root_cause}" if root_cause else "Submitted a diagnosis conclusion with evidence."
        else:
            submodule = "evidence"
            headline_ko, headline_en = "진단 근거 수집", "Diagnosis evidence collection"
            detail_ko, detail_en = "진단 단계의 기록된 상태를 확인하세요.", "Inspect the recorded status for the diagnosis stage."
        return _payload(
            route="internal", node="diagnosis", submodule=submodule, actor="Diagnosis Agent",
            headline_ko=f"{headline_ko} · {ko_status}", headline_en=f"{headline_en} · {en_status}",
            detail_ko=detail_ko, detail_en=detail_en, target=target, result_count=count,
        )

    if component == "runbook" and action == "search":
        submodule = "search" if status in {"started", "waiting"} else "result"
        if status in {"started", "waiting"}:
            detail_ko, detail_en = "Runbook에서 관련 운영 절차를 찾고 있습니다.", "Searching Runbooks for relevant operating procedures."
        elif status == "skipped":
            detail_ko, detail_en = "이 단계에서는 Runbook 검색을 사용하지 않았습니다.", "Runbook search was not used for this stage."
        elif status == "failed":
            detail_ko, detail_en = "Runbook 검색에 실패했습니다.", "Runbook search failed."
        elif count is not None:
            detail_ko, detail_en = f"검색 결과 {count}개를 기록했습니다.", f"Recorded {count} search result(s)."
        else:
            detail_ko, detail_en = "Runbook 검색이 끝났습니다.", "Runbook search finished."
        return _payload(
            route="rag", node="runbook", submodule=submodule, actor="Operation Agent ↔ Runbooks Search",
            headline_ko=f"Runbook 검색 · {ko_status}", headline_en=f"Runbook search · {en_status}",
            detail_ko=detail_ko, detail_en=detail_en, result_count=count,
        )

    if component == "memory" and action in {"search", "draft", "write", "import_reference"}:
        submodule = "read" if action in {"search", "import_reference"} else action
        noun_ko = {"search": "Incident Memory 조회", "draft": "Memory 초안", "write": "Incident Memory 저장", "import_reference": "Memory 참고자료 등록"}[action]
        noun_en = {"search": "Incident Memory read", "draft": "Memory draft", "write": "Incident Memory write", "import_reference": "Memory reference import"}[action]
        if count is not None:
            detail_ko, detail_en = f"관련 기록 {count}개를 확인했습니다.", f"Observed {count} related record(s)."
        elif target:
            detail_ko, detail_en = f"대상 {target}의 기록을 처리했습니다.", f"Processed the record for {target}."
        else:
            detail_ko, detail_en = f"{noun_ko} 상태를 기록했습니다.", f"Recorded the {noun_en.lower()} status."
        return _payload(
            route="memory", node="memory", submodule=submodule, actor="Operation Agent ↔ Incident Memory",
            headline_ko=f"{noun_ko} · {ko_status}", headline_en=f"{noun_en} · {en_status}",
            detail_ko=detail_ko, detail_en=detail_en, target=target, result_count=count,
        )

    if component == "a2a" and action in {"delegate_diagnosis", "request_received", "response"}:
        returning = action == "response" or (action == "delegate_diagnosis" and status == "succeeded")
        route = "return" if returning else "delegate"
        submodule = "conclusion" if returning else "inspect"
        headline_ko = "진단 결과 반환" if returning else "진단 작업 위임"
        headline_en = "Diagnosis result returned" if returning else "Diagnosis delegated"
        return _payload(
            route=route, node="diagnosis", submodule=submodule,
            actor="Diagnosis Agent → Operation Agent" if returning else "Operation Agent → Diagnosis Agent",
            headline_ko=f"{headline_ko} · {ko_status}", headline_en=f"{headline_en} · {en_status}",
            detail_ko="A2A로 전달된 진단 요청 또는 결과의 상태를 기록했습니다.",
            detail_en="Recorded the state of the diagnosis request or result transferred over A2A.",
            target=target,
        )

    if component == "mcp" and action in {"call", "execute", "list_tools"}:
        role = _first_string(details.get("role"), details.get("caller_role"))
        if not role:
            writer = _string(event.get("writer_id")).casefold()
            role = "diagnosis" if "diagnosis" in writer else "operation" if "operation" in writer else "unknown"
        tool = _first_string(details.get("tool"), "list_tools" if action == "list_tools" else "")
        route = "diag_mcp" if role == "diagnosis" else "op_mcp"
        actor = "Diagnosis Agent ↔ Network Tools" if role == "diagnosis" else "Operation Agent ↔ Network Tools"
        submodule = _tool_stage(tool)
        tool_label = f" ({tool})" if tool else ""
        if target:
            detail_ko, detail_en = f"대상: {target}", f"Target: {target}"
        elif count is not None:
            detail_ko, detail_en = f"결과 항목: {count}개", f"Result items: {count}"
        else:
            detail_ko, detail_en = f"{role} 역할의 MCP 호출 상태를 기록했습니다.", f"Recorded the MCP call state for the {role} role."
        return _payload(
            route=route, node="tools", submodule=submodule, actor=actor,
            headline_ko=f"Network Tool{tool_label} · {ko_status}", headline_en=f"Network tool{tool_label} · {en_status}",
            detail_ko=detail_ko, detail_en=detail_en, tool=tool, target=target, result_count=count,
        )

    if component == "model":
        role = _string(details.get("role")) or ("diagnosis" if "diagnosis" in _string(event.get("writer_id")).casefold() else "operation")
        node = "diagnosis" if role == "diagnosis" else "operation"
        submodule = "conclusion" if node == "diagnosis" else "action"
        selected_tool = _first_string(details.get("tool"), details.get("selected_tool"))
        concrete = f" ({selected_tool})" if selected_tool else ""
        return _payload(
            route="internal", node=node, submodule=submodule, actor=f"{role.title()} Agent model",
            headline_ko=f"모델 동작{concrete} · {ko_status}", headline_en=f"Model activity{concrete} · {en_status}",
            detail_ko="모델에 전달한 입력과 반환된 기능을 확인할 수 있습니다.",
            detail_en="Inspect the model input and the function returned by the model.", tool=selected_tool,
        )

    if component == "runner":
        if action in {"run", "episode", "services", "workflow", "episode_error", "oracle"}:
            noun_ko = {"run": "실행", "episode": "에피소드", "services": "서비스 준비", "workflow": "Workflow 전환", "episode_error": "에피소드 오류", "oracle": "독립 상태 평가"}[action]
            noun_en = {"run": "Run", "episode": "Episode", "services": "Service startup", "workflow": "Workflow transition", "episode_error": "Episode error", "oracle": "Independent state evaluation"}[action]
            outcome = _first_string(details.get("outcome"), _mapping(details.get("summary")).get("status"))
            concrete = f" · {outcome}" if outcome else ""
            return _payload(
                route="internal", node="operation", submodule="context", actor="Runner",
                headline_ko=f"{noun_ko}{concrete} · {ko_status}", headline_en=f"{noun_en}{concrete} · {en_status}",
                detail_ko="Runner가 기록한 실행 단계입니다.", detail_en="This execution stage was recorded by the runner.",
                target=target, track_active=False,
            )

    return _payload(
        route="internal", node="operation", submodule="context", actor="Activity stream",
        headline_ko=f"일반 activity 단계 · {ko_status}", headline_en=f"Generic activity stage · {en_status}",
        detail_ko="아직 전용 표시 규칙이 없는 event입니다. 원본 요약은 아래 상세에서 확인할 수 있습니다.",
        detail_en="This event has no dedicated presentation rule yet. Its original summary remains available in the raw detail below.",
        target=target, result_count=count, generic=True,
    )


def presentation_for_event(event: dict[str, Any]) -> dict[str, Any]:
    from ccs.event_communication import communication_for_event
    result = _presentation_for_event(event)
    result["communication"] = communication_for_event(event)
    details = _mapping(event.get("details"))
    if result["communication"]["protocol"] == "A2A" and result["communication"]["kind"] == "request":
        request = _mapping(details.get("request"))
        if request:
            context = _mapping(request.get("context"))
            counts = []
            for label, key in (("Runbook", "runbooks"), ("Memory", "history")):
                if isinstance(context.get(key), list):
                    counts.append(f"{label} {len(context[key])}")
            suffix = " · " + " / ".join(counts) if counts else ""
            budget = _mapping(request.get("constraints")).get("tool_budget")
            budget_ko = f" · 도구 조회 예산 {budget}회" if isinstance(budget, int) else ""
            budget_en = f" · tool budget {budget}" if isinstance(budget, int) else ""
            result["detail"] = {"ko": f"운영 요청과 선택한 참고자료를 전달합니다{suffix}{budget_ko}. 선택하면 실제 내용을 확인합니다.",
                                "en": f"Handing off the incident and selected references{suffix}{budget_en}. Select to inspect the actual content."}
    return result
