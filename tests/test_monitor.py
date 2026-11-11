from __future__ import annotations

from datetime import datetime, timezone
from http.client import HTTPConnection
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import urlopen
import json
from pathlib import Path

import pytest

from ccs.monitor import DashboardServer, _document, _normalize_event, read_activity, write_snapshot


def _event(
    event_id: str,
    *,
    ts: str,
    seq: int,
    status: str = "info",
    details: object | None = None,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "ts_utc": ts,
        "run_id": "D0_mock_monitor",
        "episode_id": "episode-0001",
        "writer_id": "operation",
        "local_seq": seq,
        "component": "operation",
        "action": "collect_context",
        "status": status,
        "summary": f"activity {event_id}",
        "details": details or {},
        "operation_id": "operation-context-1",
        "mode": "mock",
    }


def _write_manifest(run_dir: Path, *, status: str = "RUNNING") -> None:
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_schema": "netops-run@1",
                "run_id": "D0_mock_monitor",
                "condition": "D0-disclosure-off",
                "status": status,
                "mode": "mock",
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "models": {"operation": "scripted-mock", "diagnosis": "scripted-mock"},
                "episodes": [],
                "config_hash": "not-needed-in-monitor",
                "private_extension": "must-not-be-exposed",
            }
        ),
        encoding="utf-8",
    )


def _api_url(server: DashboardServer, cursor: str = "") -> str:
    parsed = urlsplit(server.url or "")
    query = parse_qs(parsed.query)
    values = {"token": query["token"][0]}
    if cursor:
        values["cursor"] = cursor
    return f"{parsed.scheme}://{parsed.netloc}/api/state?{urlencode(values)}"


def test_read_activity_sorts_complete_lines_and_redacts_prohibited_detail(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    activity = run_dir / "activity"
    activity.mkdir(parents=True)
    later = _event(
        "event-later",
        ts="2026-09-29T01:02:03+00:00",
        seq=2,
        details={
            "input": {"ticket": "T-1"},
            "raw_response": "PRIVATE MODEL TRANSCRIPT",
            "nested": {"api_key": "PRIVATE KEY", "evidence": ["KPI restored"]},
        },
    )
    earlier = _event("event-earlier", ts="2026-09-29T01:02:02Z", seq=1, status="started")
    partial = _event("event-partial", ts="2026-09-29T01:02:04Z", seq=3)
    shard = activity / "operation.jsonl"
    shard.write_bytes(
        (json.dumps(later) + "\n" + json.dumps(earlier) + "\n" + json.dumps(partial)[:25]).encode()
    )

    events = read_activity(run_dir)

    assert [event["event_id"] for event in events] == ["event-earlier", "event-later"]
    rendered = json.dumps(events)
    assert "PRIVATE MODEL TRANSCRIPT" not in rendered
    assert "PRIVATE KEY" not in rendered
    assert events[1]["details"]["raw_response"] == "[redacted by monitor]"
    assert events[1]["details"]["nested"]["evidence"] == ["KPI restored"]
    assert events[0]["presentation"]["node"] == "operation"
    assert events[0]["presentation"]["submodule"] == "context"


def test_dashboard_cursor_revisits_partial_line_and_rejects_other_paths(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    activity = run_dir / "activity"
    activity.mkdir(parents=True)
    _write_manifest(run_dir)
    first = _event("event-1", ts="2026-09-29T01:00:00Z", seq=1, status="started")
    second = _event("event-2", ts="2026-09-29T01:00:01Z", seq=2, status="succeeded")
    second_line = json.dumps(second)
    split = len(second_line) // 2
    shard = activity / "operation.jsonl"
    shard.write_text(json.dumps(first) + "\n" + second_line[:split], encoding="utf-8")

    with DashboardServer(run_dir).start() as server:
        parsed = urlsplit(server.url or "")
        assert parsed.hostname == "127.0.0.1"
        with urlopen(server.url, timeout=3) as response:
            html = response.read().decode()
            assert response.headers["Content-Security-Policy"]
            assert response.headers.get("Access-Control-Allow-Origin") is None
            assert "NetOps Agent Activity Monitor" in html

        with urlopen(_api_url(server), timeout=3) as response:
            initial = json.load(response)
        assert [event["event_id"] for event in initial["events"]] == ["event-1"]
        assert "private_extension" not in initial["meta"]["manifest"]

        with shard.open("a", encoding="utf-8") as stream:
            stream.write(second_line[split:] + "\n")
        diagnosis = _event("event-3", ts="2026-09-29T01:00:02Z", seq=1)
        diagnosis["writer_id"] = "diagnosis"
        diagnosis["component"] = "diagnosis"
        (activity / "diagnosis.jsonl").write_text(json.dumps(diagnosis) + "\n", encoding="utf-8")

        with urlopen(_api_url(server, initial["cursor"]), timeout=3) as response:
            update = json.load(response)
        assert {event["event_id"] for event in update["events"]} == {"event-2", "event-3"}

        with pytest.raises(HTTPError) as missing_token:
            urlopen(f"{parsed.scheme}://{parsed.netloc}/api/state", timeout=3)
        assert missing_token.value.code == 403

        token = parse_qs(parsed.query)["token"][0]
        with pytest.raises(HTTPError) as arbitrary_path:
            urlopen(f"{parsed.scheme}://{parsed.netloc}/configs/ai.local.xml?{urlencode({'token': token})}", timeout=3)
        assert arbitrary_path.value.code == 404


def test_dashboard_only_supports_read_methods(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_manifest(run_dir)
    with DashboardServer(run_dir).start() as server:
        parsed = urlsplit(server.url or "")
        connection = HTTPConnection(parsed.hostname, parsed.port, timeout=3)
        connection.request("POST", parsed.path + "?" + parsed.query)
        response = connection.getresponse()
        response.read()
        connection.close()
        assert response.status == 501


def test_snapshot_is_standalone_and_script_payload_is_escaped(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    activity = run_dir / "activity"
    activity.mkdir(parents=True)
    _write_manifest(run_dir, status="COMPLETED")
    malicious = "</script><script>globalThis.monitorPwned=true</script> 한글"
    event = _event(
        "event-safe",
        ts="2026-09-29T01:00:00Z",
        seq=1,
        details={
            "evidence": malicious,
            "thinking": "PRIVATE CHAIN",
            "encrypted_content": "PRIVATE ENCRYPTED REASONING",
            "password": "PRIVATE PASSWORD",
        },
    )
    (activity / "operation.jsonl").write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "run_id": "D0_mock_monitor",
                "status": "COMPLETED",
                "episodes": 1,
                "completed_episodes": 1,
                "successful_episodes": 1,
                "api_calls": 0,
                "mode": "mock",
                "raw_response": "must never be copied",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "ai.local.xml").write_text("<api_key>PRIVATE CONFIG KEY</api_key>", encoding="utf-8")

    output = write_snapshot(run_dir)
    html = output.read_text(encoding="utf-8")

    assert output == run_dir / "monitor.html"
    assert "window.__CCS_SNAPSHOT__={" in html
    assert malicious not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html
    assert "PRIVATE CHAIN" not in html
    assert "PRIVATE ENCRYPTED REASONING" not in html
    assert "PRIVATE PASSWORD" not in html
    assert "PRIVATE CONFIG KEY" not in html
    assert "must never be copied" not in html
    assert "한글" in html
    assert "fetch('/api/state?'" in html


def test_snapshot_marks_old_run_without_activity(tmp_path: Path) -> None:
    run_dir = tmp_path / "old-run"
    run_dir.mkdir()
    _write_manifest(run_dir, status="COMPLETED")

    output = write_snapshot(run_dir)
    html = output.read_text(encoding="utf-8")

    assert '"activity_present":false' in html
    assert "이 run에는 activity event가 없습니다" in html


def test_normalized_event_adds_safe_bilingual_presentation_after_redaction() -> None:
    event = _event(
        "event-presentation",
        ts="2026-09-29T01:00:00Z",
        seq=1,
        status="failed",
        details={
            "role": "diagnosis",
            "tool": "get_kpi",
            "arguments": {"target": "HOST-001"},
            "raw_response": "PRIVATE RESPONSE",
        },
    )
    event["component"] = "mcp"
    event["action"] = "call"

    normalized = _normalize_event(event)

    assert normalized is not None
    assert normalized["details"]["raw_response"] == "[redacted by monitor]"
    assert normalized["presentation"]["route"] == "diag_mcp"
    assert normalized["presentation"]["submodule"] == "read"
    assert normalized["presentation"]["target"] == "HOST-001"
    assert "PRIVATE RESPONSE" not in json.dumps(normalized)


def test_document_is_white_large_topology_and_embedded_height_aware() -> None:
    html = _document()

    assert 'viewBox="0 0 1300 650"' in html
    assert "--bg:#f5f5f7" in html
    assert "--surface:#fff" in html
    assert "ccs-monitor-height" in html
    assert "window.self!==window.top" in html
    assert "ccs-ui-language" in html
    assert "staleOperationIds" in html
    assert "event.presentation?.track_active===false" in html
    assert "eventEpoch(a.ts_utc)-eventEpoch(b.ts_utc)" in html
    assert ".embedded .top,.embedded .summary{display:none}" in html
    assert "에이전트 처리 흐름" in html
    assert "진행 기록" in html
    assert "원본 이벤트" in html
    assert "routeRequest:'요청 전달'" in html
    for route, color in {
        "request": "#0071e3",
        "rag": "#af52de",
        "memory": "#00897b",
        "delegate": "#5856d6",
        "return": "#6e5ce6",
        "op_mcp": "#c77800",
        "diag_mcp": "#008db3",
        "report": "#248a3d",
        "internal": "#6e6e73",
    }.items():
        assert f"{route}:'{color}'" in html
