"""Protection-free D0 gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .bus import EventBus


@dataclass(frozen=True)
class GateTrace:
    action: str
    rule_ids: list[str] = field(default_factory=list)


class Gate(Protocol):
    def decide(self, event: dict[str, Any], payload: Any) -> tuple[Any, GateTrace]: ...


class NullGate:
    """D0 gate: permit the exact input object without copying or mutation."""

    gate_id = "null@v0"

    def decide(self, event: dict[str, Any], payload: Any) -> tuple[Any, GateTrace]:
        return payload, GateTrace(action="allow")


class Gateway:
    def __init__(self, bus: EventBus, gate: Gate | None = None):
        self.bus = bus
        self.gate = gate or NullGate()

    def pass_through(
        self,
        stage: str,
        payload: Any,
        source: str,
        sink: str,
        **metadata: Any,
    ) -> tuple[Any, str]:
        envelope = {
            "stage": stage,
            "source": source,
            "sink": sink,
            "run_id": self.bus.run_id,
            "episode_id": self.bus.episode_id,
        }
        transformed, trace = self.gate.decide(envelope, payload)
        emit_metadata = dict(metadata)
        emit_metadata["gate_id"] = getattr(self.gate, "gate_id", type(self.gate).__name__)
        emit_metadata["decision"] = trace.action
        emit_metadata["gate_rule_ids"] = list(trace.rule_ids)
        event_id = self.bus.emit(stage, transformed, source, sink, **emit_metadata)
        return transformed, event_id
