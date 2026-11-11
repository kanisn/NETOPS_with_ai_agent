from __future__ import annotations

import pytest

from ccs.event_presentation import presentation_for_event


def _event(
    component: str,
    action: str,
    status: str = "started",
    *,
    details: dict[str, object] | None = None,
    writer_id: str = "operation",
) -> dict[str, object]:
    return {
        "component": component,
        "action": action,
        "status": status,
        "details": details or {},
        "writer_id": writer_id,
    }


@pytest.mark.parametrize(
    ("event", "route", "node", "submodule"),
    [
        (_event("operation", "request_received", "info"), "request", "operation", "context"),
        (_event("operation", "collect_context"), "internal", "operation", "context"),
        (_event("runbook", "search"), "rag", "runbook", "search"),
        (_event("runbook", "search", "succeeded", details={"results": [{}, {}]}), "rag", "runbook", "result"),
        (_event("memory", "search"), "memory", "memory", "read"),
        (_event("memory", "draft"), "memory", "memory", "draft"),
        (_event("memory", "write", "succeeded"), "memory", "memory", "write"),
        (_event("a2a", "delegate_diagnosis"), "delegate", "diagnosis", "inspect"),
        (_event("a2a", "delegate_diagnosis", "succeeded"), "return", "diagnosis", "conclusion"),
        (_event("operation", "report_delivered", "succeeded"), "report", "operation", "report"),
    ],
)
def test_maps_workflow_phases_to_stable_routes_and_submodules(
    event: dict[str, object], route: str, node: str, submodule: str
) -> None:
    presentation = presentation_for_event(event)

    assert presentation["route"] == route
    assert presentation["node"] == node
    assert presentation["submodule"] == submodule
    assert presentation["headline"]["ko"]
    assert presentation["headline"]["en"]
    assert presentation["detail"]["ko"]
    assert presentation["detail"]["en"]
    assert presentation["generic"] is False


@pytest.mark.parametrize(
    ("role_field", "role", "tool", "route", "submodule"),
    [
        ("role", "operation", "get_config", "op_mcp", "read"),
        ("role", "operation", "preview_change", "op_mcp", "preview"),
        ("role", "operation", "apply_change", "op_mcp", "apply"),
        ("role", "operation", "verify_service", "op_mcp", "verify"),
        ("role", "operation", "rollback_change", "op_mcp", "rollback"),
        ("caller_role", "diagnosis", "get_kpi", "diag_mcp", "read"),
    ],
)
def test_mcp_role_and_tool_choose_direction_without_changing_failure_channel(
    role_field: str, role: str, tool: str, route: str, submodule: str
) -> None:
    presentation = presentation_for_event(
        _event(
            "mcp",
            "execute" if role_field == "caller_role" else "call",
            "failed",
            details={
                role_field: role,
                "tool": tool,
                "arguments": {"target": "HOST-001"},
                "result": {"error": "TEST_FAILURE"},
            },
            writer_id=f"mcp-{role}",
        )
    )

    assert presentation["route"] == route
    assert presentation["submodule"] == submodule
    assert presentation["tool"] == tool
    assert presentation["target"] == "HOST-001"
    assert "failed" in presentation["headline"]["en"]
    assert "실패" in presentation["headline"]["ko"]


def test_result_count_is_concrete_and_unknown_event_uses_explicit_generic_copy() -> None:
    runbook = presentation_for_event(
        _event("runbook", "search", "succeeded", details={"results": [{"id": 1}, {"id": 2}, {"id": 3}]})
    )
    unknown = presentation_for_event(
        _event("future-component", "future-action", "waiting", details={"summary": "do not infer"})
    )

    assert runbook["result_count"] == 3
    assert "3" in runbook["detail"]["ko"]
    assert "3" in runbook["detail"]["en"]
    assert unknown["route"] == "internal"
    assert unknown["generic"] is True
    assert "일반 activity 단계" in unknown["headline"]["ko"]
    assert "do not infer" not in unknown["headline"]["ko"]
    assert "do not infer" not in unknown["detail"]["ko"]


def test_progress_copy_is_status_aware_and_keeps_literal_query_out_of_primary_log() -> None:
    started_context = presentation_for_event(
        _event("operation", "collect_context", "started", details={"incident": {"target": "HOST-001"}})
    )
    finished_context = presentation_for_event(
        _event("operation", "collect_context", "succeeded", details={"incident": {"target": "HOST-001"}})
    )
    literal_query = "Investigate the full operator request with a very long English payload"
    started_search = presentation_for_event(
        _event("runbook", "search", "started", details={"query": literal_query, "limit": 3})
    )

    assert "정리하고 있습니다" in started_context["detail"]["ko"]
    assert "준비했습니다" in finished_context["detail"]["ko"]
    assert "Searching" in started_search["detail"]["en"]
    assert "찾고 있습니다" in started_search["detail"]["ko"]
    assert literal_query not in started_search["headline"]["ko"]
    assert literal_query not in started_search["detail"]["ko"]
    assert literal_query not in started_search["headline"]["en"]
    assert literal_query not in started_search["detail"]["en"]


@pytest.mark.parametrize("action", ["run", "episode", "services", "workflow", "episode_error", "oracle"])
def test_runner_container_events_remain_visible_but_never_drive_active_glow(action: str) -> None:
    presentation = presentation_for_event(_event("runner", action, "started", writer_id="run"))

    assert presentation["route"] == "internal"
    assert presentation["track_active"] is False
