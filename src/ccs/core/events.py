"""Strict event schema shared by the bus and the offline validator."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Stage = Literal["G1", "G2", "G3r", "G3w", "G4.call", "G4.ret", "G5.req", "G5.res", "G6"]
EventStatus = Literal["started", "succeeded", "failed", "duplicate"]

STAGE_ORDER: tuple[str, ...] = (
    "G1",
    "G2",
    "G3r",
    "G3w",
    "G4.call",
    "G4.ret",
    "G5.req",
    "G5.res",
    "G6",
)


class DisclosureEvent(BaseModel):
    """A single measured disclosure crossing.

    Payload bytes are deliberately absent. ``payload_ref`` points to the
    restricted blob store and ``payload_digest`` protects those exact bytes.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal["disclosure-event@1"] = "disclosure-event@1"
    event_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    span_id: str = Field(min_length=1)
    parent_span_id: str | None = None
    causation_event_id: str | None = None
    run_id: str = Field(min_length=1)
    episode_id: str = Field(min_length=1)
    episode_seq: int = Field(ge=0)
    task_id: str = Field(min_length=1)
    writer_id: str = Field(min_length=1)
    local_seq: int = Field(ge=1)
    attempt: int = Field(ge=1)
    stage: Stage
    source: str = Field(min_length=1)
    sink: str = Field(min_length=1)
    authenticated_principal: str = Field(min_length=1)
    principal_role: str = Field(min_length=1)
    purpose: str | None = None
    payload_ref: str = Field(pattern=r"^blobs/[0-9a-f-]+\.json$")
    payload_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    payload_size: int = Field(ge=0)
    transport: str = Field(min_length=1)
    gate_id: str = Field(min_length=1)
    decision: Literal["allow"]
    status: EventStatus
    ts_logical: int = Field(ge=0)
    ts_utc: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ts_utc")
    @classmethod
    def _valid_utc_timestamp(cls, value: str) -> str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("ts_utc must include a UTC offset")
        return value
