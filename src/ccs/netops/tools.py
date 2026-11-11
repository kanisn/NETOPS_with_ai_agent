"""Provider-independent JSON schemas for the stable Network Tools surface."""

from copy import deepcopy


def _object(properties: dict, required: list[str] | None = None) -> dict:
    schema = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        schema["required"] = required
    return schema


_READ_TOOLS = [
    {"name": "list_alarms", "description": "List wired operational alarms. Omit scope to discover affected node IDs. Window is logical ticks.", "parameters": _object({"scope": {"type": "string"}, "window": {"type": "integer", "minimum": 1, "maximum": 1000}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}})},
    {"name": "get_kpi", "description": "Read current wired service KPIs. Omit metrics on the first call to discover all exact names; window is logical ticks, not minutes.", "parameters": _object({"target": {"type": "string"}, "metrics": {"type": "array", "items": {"type": "string", "enum": ["throughput_mbps", "latency_ms", "packet_loss_pct", "reachability_pct"]}, "maxItems": 12}, "window": {"type": "integer", "minimum": 1, "maximum": 1000}}, ["target"])},
    {"name": "get_logs", "description": "Read a bounded set of wired network log lines; lines may contain host or flow identifiers.", "parameters": _object({"target": {"type": "string"}, "window": {"type": "integer", "minimum": 1, "maximum": 1000}, "severity": {"type": "string", "enum": ["DEBUG", "INFO", "WARN", "ERROR"]}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}}, ["target"])},
    {"name": "get_config", "description": "Read current and ordinary reference configuration for one wired host. Omit params on the first call. A healthy alternate path can be safer than the ordinary reference when topology proves the primary path failed.", "parameters": _object({"target": {"type": "string"}, "params": {"type": "array", "items": {"type": "string", "enum": ["active_path", "admin_state", "default_gateway", "loss_pct", "bandwidth_mbps", "delay_ms"]}, "maxItems": 20}}, ["target"])},
    {"name": "get_topology", "description": "Read a bounded normalized topology around a network target.", "parameters": _object({"target": {"type": "string"}, "depth": {"type": "integer", "minimum": 0, "maximum": 2}}, ["target"])},
    {"name": "lookup_flows", "description": "Look up a bounded set of wired traffic flows by host, source IP, or destination IP.", "parameters": _object({"host": {"type": "string"}, "src_ip": {"type": "string"}, "dst_ip": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 25}})},
]

_CHANGE_TOOLS = [
    {"name": "preview_change", "description": "Validate and bind a proposed change to the current network-state version.", "parameters": _object({"target": {"type": "string"}, "param": {"type": "string"}, "value": {}, "reason": {"type": "string", "minLength": 1, "maxLength": 500}}, ["target", "param", "value", "reason"])},
    {"name": "apply_change", "description": "Apply exactly the change bound into a non-stale preview token.", "parameters": _object({"change_token": {"type": "string"}, "idempotency_key": {"type": "string", "minLength": 1, "maxLength": 128}}, ["change_token", "idempotency_key"])},
    {"name": "get_change_status", "description": "Read the durable result associated with an idempotency key.", "parameters": _object({"idempotency_key": {"type": "string", "minLength": 1, "maxLength": 128}}, ["idempotency_key"])},
    {"name": "rollback_change", "description": "Restore a directly applied change when no later network mutation conflicts.", "parameters": _object({"change_id": {"type": "string"}, "idempotency_key": {"type": "string", "minLength": 1, "maxLength": 128}}, ["change_id", "idempotency_key"])},
    {"name": "verify_service", "description": "Evaluate service health from current state and deterministic operational predicates.", "parameters": _object({"target": {"type": "string"}, "checks": {"type": "array", "items": {"type": "string"}, "maxItems": 12}}, ["target"])},
    {"name": "update_ticket", "description": "Update incident status and append a bounded operator note.", "parameters": _object({"ticket_id": {"type": "string"}, "status": {"type": "string", "enum": ["open", "investigating", "resolved", "escalated"]}, "note": {"type": "string", "maxLength": 1000}, "idempotency_key": {"type": "string", "minLength": 1, "maxLength": 128}}, ["ticket_id", "status", "note"])},
]


def tool_schemas(role: str) -> list[dict]:
    """Return schemas visible to a role without backend-specific details."""

    normalized = role.strip().lower()
    if normalized == "diagnosis":
        return deepcopy(_READ_TOOLS)
    if normalized == "operation":
        return deepcopy(_READ_TOOLS + _CHANGE_TOOLS)
    raise ValueError("role must be 'operation' or 'diagnosis'")
