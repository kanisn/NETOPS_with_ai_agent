"""Display actual message direction and admitted payloads for activity records.

Callers pass already-scrubbed event details. No provider transcript is read here.
"""
from __future__ import annotations

from typing import Any


def _dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def communication_for_event(event: dict[str, Any]) -> dict[str, Any]:
    component, action, status = (str(event.get(k, "")) for k in ("component", "action", "status"))
    details = _dict(event.get("details"))
    writer = str(event.get("writer_id", ""))
    role = details.get("role") or details.get("caller_role")
    if role not in {"operation", "diagnosis"}:
        role = "diagnosis" if "diagnosis" in writer else "operation" if "operation" in writer else "unknown"
    actor = role if role != "unknown" else component
    source = destination = actor
    protocol, kind = "local", "internal"
    sections: list[dict[str, Any]] = []

    def section(key: str, ko: str, en: str, value: Any) -> None:
        if value is not None:
            sections.append({"key": key, "label": {"ko": ko, "en": en}, "value": value})

    response = status == "succeeded"
    if component == "a2a":
        returning = action == "response" or (action == "delegate_diagnosis" and response)
        if returning:
            source, destination, protocol, kind = "diagnosis", "operation", "A2A", "response"
            section("response", "진단 결론과 전달 내용", "Diagnosis and returned content", details.get("response", details.get("result")))
        else:
            source, destination, protocol, kind = "operation", "diagnosis", "A2A", "request"
            request = _dict(details.get("request"))
            section("incident", "사고 정보 · 운영자 요청", "Incident and operator request", request.get("incident"))
            context = _dict(request.get("context"))
            section("runbooks", "전달한 Runbook", "Forwarded Runbooks", context.get("runbooks"))
            section("history", "전달한 Memory", "Forwarded Memory", context.get("history"))
            extra = {k: v for k, v in context.items() if k not in {"runbooks", "history"}}
            if extra:
                section("context", "추가 관측 정보", "Additional observations", extra)
            section("constraints", "수행 제약 · 도구 예산", "Constraints and tool budget", request.get("constraints"))
            envelope = {k: v for k, v in request.items() if k not in {"incident", "context", "constraints"}}
            if envelope:
                section("envelope", "메시지 식별 정보", "Message identifiers", envelope)
    elif component == "mcp":
        if action == "execute":
            source, destination, protocol = "tools", "network", "NetworkBackend"
            if response or "result" in details:
                source, destination, kind = destination, source, "response"
            else:
                kind = "request"
        else:
            source, destination, protocol, kind = actor, "tools", "MCP", "request"
            if response or "result" in details:
                source, destination, kind = destination, source, "response"
        section("arguments", "요청 인자", "Request arguments", details.get("arguments"))
        section("result", "응답 내용", "Response content", details.get("result", details.get("tools")))
    elif component in {"runbook", "memory"} and action in {"search", "write", "import_reference"} and status != "skipped":
        source, destination, protocol, kind = "operation", component, "local store", "request"
        if response:
            source, destination, kind = destination, source, "response"
        section("query", "검색 요청", "Search query", details.get("query"))
        section("results", "검색 결과", "Search results", details.get("results"))
        section("record", "저장한 내용", "Stored content", details.get("record", details.get("payload")))
    elif component == "model" and action == "request":
        source, destination, protocol, kind = actor, "model", "provider API", "request"
        if response:
            source, destination, kind = destination, source, "response"
        section("request", "모델 초기 입력", "Initial model input", details.get("request"))
        section("offered_tools", "사용 가능한 기능", "Available functions", details.get("offered_tools"))
        section("selected_tools", "모델이 반환한 기능과 인자", "Returned functions and arguments", details.get("selected_tools"))
    elif component == "operation" and action == "request_received":
        source, destination, protocol, kind = "human", "operation", "operator input", "request"
        section("request", "운영자 요청", "Operator request", details.get("request", details))
    elif component == "operation" and action == "report_delivered":
        source, destination, protocol, kind = "operation", "human", "operator report", "response"
        section("report", "운영 결과 보고", "Operation report", details.get("report", details))
    elif component == "operation" and action == "diagnosis_received":
        source, destination, protocol, kind = "diagnosis", "operation", "A2A", "response"
        section("diagnosis", "받은 진단 결과", "Received diagnosis", details.get("diagnosis", details))
    if status == "failed":
        # An exception without a result is a failed request, not an observed reply.
        if kind == "request":
            kind = "request_failed"
        section("error", "실패 정보", "Failure information", {k: v for k, v in details.items() if k in {"error_type", "error", "http_status"}} or None)
    if not sections and details:
        section("details", "기록된 처리 내용", "Recorded activity details", details)
    return {"source": source, "destination": destination, "protocol": protocol, "kind": kind,
            "model": details.get("model", ""), "sections": sections}
