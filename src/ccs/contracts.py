"""Provider-independent Agent payload contracts."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ProposedChange(Contract):
    target: str
    param: Literal['active_path','admin_state','default_gateway','loss_pct','bandwidth_mbps','delay_ms']
    value: Any
    reason: str = "Incident remediation"

class DiagnosisRequest(Contract):
    schema_version: Literal["diagnosis@1"] = "diagnosis@1"
    task_id: str
    trace_id: str
    message_id: str
    idempotency_key: str
    incident: dict[str, Any]
    context: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=lambda: {"tool_budget": 8})

class DiagnosisResult(Contract):
    root_cause: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    proposed_change: ProposedChange | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    notes: str = ""

class Report(Contract):
    summary: str
    root_cause: str
    action: str
    outcome: str
    evidence: list[str] = Field(default_factory=list)

class MemoryRecord(Contract):
    record_id: str
    scope_id: str
    tenant_id: str
    purpose: Literal["P-recur", "P-ctx", "P-audit", "P-know"]
    written_at: int
    expires_at: int | None = None
    source_event_ids: list[str] = Field(default_factory=list)
    verified_outcome: str
    payload: dict[str, Any]
    items: list[str] = Field(default_factory=list)
