from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path

import pytest

from tests.support_paths import workspace_for
from ccs.contracts import MemoryRecord
from ccs.core.bus import EventBus
from ccs.core.gateway import Gateway
from ccs.core.integrity import validate_and_merge
from ccs.evaluation.ledger import build_ledger
from ccs.knowledge.stores import MemoryStore, RunbookStore


WORKING_ROOT = workspace_for("test_instrumentation")
RUNBOOKS = Path(__file__).parents[1] / "knowledge" / "runbooks"


@pytest.fixture
def working_case() -> Path:
    WORKING_ROOT.mkdir(parents=True, exist_ok=True)
    path = WORKING_ROOT / f"case-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_null_gateway_preserves_identity_and_records_all_boundaries(working_case: Path) -> None:
    bus = EventBus(working_case, "runner", "run-identity", "episode-a")
    gateway = Gateway(bus)
    payload = {"nested": ["unchanged"], "count": 2}

    for stage in ("G1", "G2", "G3r", "G3w", "G4.call", "G4.ret", "G5.req", "G5.res", "G6"):
        returned, _ = gateway.pass_through(stage, payload, "source", "sink")
        assert returned is payload

    result = validate_and_merge(working_case)
    assert result["valid"], result["errors"]
    assert result["event_count"] == 9
    assert result["stages"] == [
        "G1", "G2", "G3r", "G3w", "G4.call", "G4.ret", "G5.req", "G5.res", "G6"
    ]
    assert len(list((working_case / "blobs").glob("*.json"))) == 9


def test_merge_obeys_cross_writer_causation_before_logical_tiebreakers(working_case: Path) -> None:
    runner = EventBus(working_case, "runner", "run-causal", "episode-a")
    diagnosis = EventBus(working_case, "diagnosis", "run-causal", "episode-a")
    request_id = runner.emit(
        "G5.req",
        {"request": "diagnose"},
        "agent:operation",
        "agent:diagnosis",
        transport="a2a",
        ts_logical=50,
    )
    response_id = diagnosis.emit(
        "G5.res",
        {"result": "complete"},
        "agent:diagnosis",
        "agent:operation",
        causation_event_id=request_id,
        transport="a2a",
        ts_logical=1,
    )

    result = validate_and_merge(working_case)
    assert result["valid"], result["errors"]
    merged = [json.loads(line) for line in Path(result["merged_path"]).read_text(encoding="utf-8").splitlines()]
    assert [event["event_id"] for event in merged] == [request_id, response_id]


def test_numbered_episode_sequence_is_consistent_across_process_writers(working_case: Path) -> None:
    runner = EventBus(working_case, "runner", "run-sequence", "episode-0000")
    runner.episode_id = "episode-0001"
    runner.emit("G1", {"request": "inspect"}, "operator", "agent:operation")
    child = EventBus(working_case, "diagnosis-episode-0001", "run-sequence", "episode-0001")
    child.emit("G4.call", {"tool": "get_kpi"}, "agent:diagnosis", "tool:get_kpi")

    result = validate_and_merge(working_case)
    assert result["valid"], result["errors"]
    events = [
        json.loads(line)
        for line in Path(result["merged_path"]).read_text(encoding="utf-8").splitlines()
    ]
    assert {event["episode_seq"] for event in events} == {1}


@pytest.mark.parametrize("damage", ["missing", "corrupt"])
def test_integrity_rejects_missing_or_corrupt_payload_blob(working_case: Path, damage: str) -> None:
    bus = EventBus(working_case, "runner", "run-damage", "episode-a")
    event_id = bus.emit("G1", {"request": "check service"}, "operator", "agent:operation")
    blob = working_case / "blobs" / f"{event_id}.json"
    if damage == "missing":
        blob.unlink()
    else:
        blob.write_text('{"request":"changed after commit"}', encoding="utf-8")

    result = validate_and_merge(working_case)
    assert not result["valid"]
    assert any(f"{damage} blob" in error or "digest mismatch" in error for error in result["errors"])
    assert result["merged_path"] is None


def test_terminal_episode_rejects_duplicate_causal_returns(working_case: Path) -> None:
    caller = EventBus(working_case, "diagnosis", "run-pair", "episode-a")
    server = EventBus(working_case, "tools", "run-pair", "episode-a")
    call_id = caller.emit(
        "G4.call", {"tool": "get_kpi"}, "agent:diagnosis", "tool:get_kpi", transport="mcp"
    )
    for result in ("first", "duplicate execution"):
        server.emit(
            "G4.ret",
            {"result": result},
            "tool:get_kpi",
            "agent:diagnosis",
            causation_event_id=call_id,
            transport="mcp",
        )
    (working_case / "manifest.json").write_text(
        json.dumps({"episodes": [{"episode_id": "episode-a", "status": "completed"}]}),
        encoding="utf-8",
    )

    result = validate_and_merge(working_case)
    assert not result["valid"]
    assert any("requires exactly one G4.ret" in error and "found 2" in error for error in result["errors"])


def test_explicit_duplicate_delivery_does_not_count_as_second_return(working_case: Path) -> None:
    caller = EventBus(working_case, "diagnosis", "run-delivery", "episode-a")
    server = EventBus(working_case, "tools", "run-delivery", "episode-a")
    call_id = caller.emit(
        "G4.call", {"tool": "get_kpi"}, "agent:diagnosis", "tool:get_kpi", transport="mcp"
    )
    server.emit(
        "G4.ret",
        {"result": "ok"},
        "tool:get_kpi",
        "agent:diagnosis",
        causation_event_id=call_id,
        transport="mcp",
    )
    server.emit(
        "G4.ret",
        {"result": "already delivered"},
        "tool:get_kpi",
        "agent:diagnosis",
        causation_event_id=call_id,
        transport="mcp",
        status="duplicate",
    )
    (working_case / "manifest.json").write_text(
        json.dumps({"episodes": [{"episode_id": "episode-a", "status": "completed"}]}),
        encoding="utf-8",
    )
    result = validate_and_merge(working_case)
    assert result["valid"], result["errors"]


def test_incomplete_pair_is_valid_in_flight_but_invalid_when_terminal(working_case: Path) -> None:
    bus = EventBus(working_case, "runner", "run-in-flight", "episode-a")
    bus.emit("G5.req", {"request": "diagnose"}, "agent:operation", "agent:diagnosis", transport="a2a")
    assert validate_and_merge(working_case)["valid"]

    (working_case / "manifest.json").write_text(
        json.dumps({"terminal": True, "status": "failed"}), encoding="utf-8"
    )
    result = validate_and_merge(working_case)
    assert not result["valid"]
    assert any("requires exactly one G5.res" in error for error in result["errors"])


def test_runbook_bm25_handles_fault_queries_and_untrusted_query_syntax(working_case: Path) -> None:
    with RunbookStore(working_case / "runbooks.sqlite3", RUNBOOKS) as store:
        transport = store.search("packet loss alternate reroute", k=5)
        assert transport
        assert any(result["doc_id"].startswith("RB-W3") for result in transport[:3])

        no_action = store.search("healthy normal false alarm no action", k=3)
        assert no_action[0]["doc_id"] == "RB-N0-NO-ACTION"

        assert isinstance(store.search('" OR NEAR( * -', k=3), list)
        assert store.search('" (* -', k=3) == []
        with pytest.raises(ValueError):
            store.search("qos", k=0)


def _memory_record(record_id: str = "memory-1") -> MemoryRecord:
    return MemoryRecord(
        record_id=record_id,
        scope_id="episode-a",
        tenant_id="tenant-a",
        purpose="P-recur",
        written_at=1,
        expires_at=0,
        source_event_ids=["event-a"],
        verified_outcome="verified",
        payload={
            "symptom": "gateway reachability failed",
            "cause": "incorrect default gateway",
            "action": "restored default gateway",
            "result": "host reachability recovered",
        },
        items=[],
    )


def test_memory_requires_both_approval_and_verification_then_reuses_across_episode(working_case: Path) -> None:
    with MemoryStore(working_case / "memory.sqlite3") as store:
        with pytest.raises(PermissionError):
            store.write(_memory_record(), verified=True, approved=False)
        with pytest.raises(PermissionError):
            store.write(_memory_record(), verified=False, approved=True)

        assert store.write(_memory_record(), verified=True, approved=True) == "memory-1"
        results = store.search("gateway reachability", k=3)
        assert results[0]["record_id"] == "memory-1"
        assert results[0]["scope_id"] == "episode-a"
        assert results[0]["expires_at"] == 0

        second = _memory_record("memory-2").model_dump()
        second["scope_id"] = "episode-b"
        second["written_at"] = 2
        store.write(second, verified=True, approved=True)
        assert {item["scope_id"] for item in store.search("gateway", k=5)} == {
            "episode-a",
            "episode-b",
        }


def test_offline_ledger_normalizes_values_and_never_returns_registry_plaintext(working_case: Path) -> None:
    bus = EventBus(working_case, "tools", "run-ledger", "episode-a")
    bus.emit(
        "G4.ret",
        {"sessions": [{"employee_number": "001-010-000-000-001", "src_ip": "10.20.30.40"}]},
        "tool:lookup_flows",
        "agent:diagnosis",
        transport="mcp",
    )
    registry = [
        {
            "item_id": "SENS-Employee number-0001",
            "category": "user_identity",
            "field": "employee_number",
            "value": "001010000000001",
            "origin_stage": "network_state",
            "necessary_stages": ["G4.ret"],
        },
        {
            "item_id": "SENS-IP-0001",
            "category": "traffic_metadata",
            "field": "src_ip",
            "value": "10.20.30.40",
            "origin_stage": "network_state",
        },
    ]

    ledger = build_ledger(working_case, registry)
    assert ledger["valid"]
    assert ledger["matched_item_count"] == 2
    assert ledger["stage_counts"] == {"G4.ret": 2}
    rendered = json.dumps(ledger, sort_keys=True)
    assert "001010000000001" not in rendered
    assert "10.20.30.40" not in rendered


def test_ledger_separates_seed_bindings_and_marks_cross_episode_visits(working_case: Path) -> None:
    bus = EventBus(working_case, "runner", "run-registry", "episode-a")
    bus.emit("G1", {"host": "HOST-001"}, "operator", "agent:operation")
    bus.episode_id = "episode-c"
    bus.emit("G6", {"summary": "HOST-001 remains healthy"}, "agent:operation", "operator")
    binding = {
        "item_id": "SENS-HOST-0001",
        "category": "location",
        "field": "host_id",
        "value": "host-001",
        "origin_stage": "operator_request",
        "necessary_stages": ["G1"],
        "origin_episode_id": "episode-a",
    }
    repeat = dict(binding)
    repeat["value"] = "HOST-001"
    repeat["necessary_stages"] = ["G6"]
    repeat["origin_episode_id"] = "episode-b"

    ledger = build_ledger(working_case, [binding, repeat])
    assert ledger["registry_binding_count"] == 2
    assert ledger["item_count"] == 1
    assert ledger["items"][0]["necessary_stages"] == ["G1", "G6"]
    assert ledger["items"][0]["origin_episode_ids"] == ["episode-a", "episode-b"]
    assert ledger["cross_episode_item_count"] == 1
    assert ledger["cross_episode_visit_count"] == 1
    assert len(ledger["items"][0]["aggregation_key"]) == 64
    assert len(ledger["registry_fingerprint"]) == 64

    local_alias = dict(binding)
    local_alias["item_id"] = "SENS-S002-HOST-0001"
    local_alias["origin_episode_id"] = "episode-c"
    locally_present = build_ledger(working_case, [binding, repeat, local_alias])
    assert locally_present["item_count"] == 1
    assert locally_present["items"][0]["registry_item_ids"] == [
        "SENS-HOST-0001",
        "SENS-S002-HOST-0001",
    ]
    assert locally_present["cross_episode_item_count"] == 0

    conflict = dict(binding)
    conflict["value"] = "HOST-999"
    conflict["origin_episode_id"] = "episode-c"
    multi_seed = build_ledger(working_case, [binding, conflict])
    assert multi_seed["item_count"] == 2
    assert len({item["binding_id"] for item in multi_seed["items"]}) == 2

    mislabeled = dict(binding)
    mislabeled["category"] = "traffic_metadata"
    with pytest.raises(ValueError, match="conflicting metadata"):
        build_ledger(working_case, [binding, mislabeled])


def test_ledger_matcher_has_perfect_precision_recall_on_labeled_normalization_cases(
    working_case: Path,
) -> None:
    bus = EventBus(working_case, "tools", "run-matcher", "episode-a")
    positive_event = bus.emit(
        "G4.ret",
        {
            "message": "Employee number 001-010-000-000-001 and session FLOW-A7 were observed at host - 001.",
            "phone": "+1 (555) 0101",
            "ipv6": "2001:0db8:0:0:0:0:0:1",
        },
        "tool:lookup_flows",
        "agent:diagnosis",
    )
    negative_event = bus.emit(
        "G4.ret",
        {
            "message": "Employee number 001-010-000-000-002 and session FLOW-A70 were observed at HOST-0010.",
            "phone": "+1 (555) 0102",
            "ipv6": "2001:db8::2",
        },
        "tool:lookup_flows",
        "agent:diagnosis",
    )
    registry = [
        {"item_id": "I1", "category": "user_identity", "field": "employee_number", "value": "001010000000001", "origin_stage": "network_state"},
        {"item_id": "I2", "category": "user_identity", "field": "phone", "value": "15550101", "origin_stage": "network_state"},
        {"item_id": "I3", "category": "traffic_metadata", "field": "src_ip", "value": "2001:db8::1", "origin_stage": "network_state"},
        {"item_id": "I4", "category": "location", "field": "host_id", "value": "HOST-001", "origin_stage": "network_state"},
        {"item_id": "I5", "category": "traffic_metadata", "field": "flow_id", "value": "FLOW-A7", "origin_stage": "network_state"},
    ]

    ledger = build_ledger(working_case, registry)
    observed = {
        (item["item_id"], visit["event_id"])
        for item in ledger["items"]
        for visit in item["trace"]
    }
    expected = {(item["item_id"], positive_event) for item in registry}
    true_positives = len(observed & expected)
    precision = true_positives / len(observed)
    recall = true_positives / len(expected)
    assert negative_event not in {event_id for _, event_id in observed}
    assert precision == 1.0
    assert recall == 1.0
