import json
import sqlite3
from pathlib import Path

import pytest

from tests.support_paths import workspace_for
from ccs.bench.scenarios import FAULTS, create_world
from ccs.evaluation.oracle import evaluate
from ccs.netops.errors import ChangeConflictError, ContractError, IdempotencyConflictError, UnknownToolError, VersionConflictError
from ccs.netops.sqlite_backend import BACKEND_ID, SCHEMA_VERSION, SQLiteBackend
from ccs.netops.tools import tool_schemas

WORK_DIR = workspace_for("test_backend")
WORK_DIR.mkdir(parents=True, exist_ok=True)

def _world(name: str, **kwargs):
    path = WORK_DIR / f"{name}.sqlite"
    return path, create_world(path, **kwargs)

def _apply(backend: SQLiteBackend, change: dict, key: str = "apply-once") -> dict:
    preview = backend.call("preview_change", change)
    return backend.call("apply_change", {"change_token": preview["change_token"], "idempotency_key": key})

def test_backend_identity_rejects_legacy_database():
    legacy = WORK_DIR / "legacy.sqlite"
    if legacy.exists(): legacy.unlink()
    db = sqlite3.connect(legacy)
    db.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
    db.executemany("INSERT INTO metadata VALUES(?,?)", [("backend_id", "sqlite-stateful-v1"), ("schema_version", "1")])
    db.commit(); db.close()
    with pytest.raises(ContractError, match=BACKEND_ID): SQLiteBackend(legacy)

def test_role_contract_and_wired_read_surface():
    diagnosis = {item["name"] for item in tool_schemas("diagnosis")}
    operation = {item["name"] for item in tool_schemas("operation")}
    assert "lookup_flows" in diagnosis and "lookup_sessions" not in diagnosis
    assert diagnosis < operation
    assert {"preview_change", "apply_change", "rollback_change", "verify_service"} <= operation
    path, scenario = _world("surface", seed=11, fault_id="W4", target="HOST-001", difficulty="L3")
    with SQLiteBackend(path) as backend:
        snapshot = backend.snapshot()
        assert snapshot["backend_id"] == BACKEND_ID and snapshot["schema_version"] == SCHEMA_VERSION
        assert {"nodes", "interfaces", "links", "flows", "configuration", "changes"} <= snapshot.keys()
        topology = backend.call("get_topology", {"target": "HOST-001", "depth": 2})
        assert set(topology) == {"target", "depth", "nodes", "interfaces", "links", "flows", "state_version"}
        assert {node["node_type"] for node in topology["nodes"]} >= {"host", "switch", "router"}
        assert {link["path"] for link in topology["links"]} >= {"primary", "backup", "shared"}
        flows = backend.call("lookup_flows", {"host": "HOST-001", "limit": 3})
        assert flows["count"] == 3 and all(flow["src_host"] == "HOST-001" for flow in flows["flows"])
        by_source = backend.call("lookup_flows", {"src_ip": "10.0.1.10"})
        by_destination = backend.call("lookup_flows", {"dst_ip": "198.51.100.10"})
        assert by_source["count"] == 10 and by_destination["count"] == 10
        with pytest.raises(ContractError): backend.call("lookup_flows", {})
        with pytest.raises(UnknownToolError): backend.call("lookup_sessions", {"host": "HOST-001"})
    assert scenario["ground_truth"]["root_cause"] not in json.dumps(snapshot)

@pytest.mark.parametrize("fault_id", ["W1", "W2", "W3", "W4", "W5", "N0"])
def test_all_wired_scenarios_recover_or_noop(fault_id: str):
    path, scenario = _world(f"recover-{fault_id}", seed=23, fault_id=fault_id, target="HOST-001", difficulty="L1")
    with SQLiteBackend(path) as backend:
        before = backend.call("verify_service", {"target": "HOST-001"})
        if fault_id == "N0":
            assert before["passed"] is True
        else:
            assert before["passed"] is False
            applied = _apply(backend, scenario["ground_truth"]["fix"], f"recover-{fault_id}")
            assert applied["status"] == "applied"
            assert backend.call("verify_service", {"target": "HOST-001"})["passed"] is True
    judgment = evaluate(path, scenario)
    assert judgment["utility"] == 1.0 and judgment["verified"] is True and judgment["forbidden_changes"] == []

def test_w1_reroutes_around_failed_switch_without_changing_ordinary_reference():
    path, scenario = _world("w1-path", seed=29, fault_id="W1", target="HOST-001", difficulty="L1")
    with SQLiteBackend(path) as backend:
        config = backend.call("get_config", {"target": "HOST-001", "params": ["active_path"]})["items"][0]
        assert config == {"param": "active_path", "current_value": "primary", "reference_value": "primary", "version": 1, "is_at_reference": True}
        topology = backend.call("get_topology", {"target": "HOST-001"})
        nodes = {node["node_id"]: node for node in topology["nodes"]}
        assert nodes["SWITCH-PRIMARY"]["status"] == "down" and nodes["SWITCH-BACKUP"]["status"] == "up"
        _apply(backend, scenario["ground_truth"]["fix"], "w1-reroute")
        after = backend.snapshot()
        assert next(item for item in after["configuration"] if item["param"] == "active_path")["current_value"] == "backup"
        assert next(node for node in after["nodes"] if node["node_id"] == "SWITCH-PRIMARY")["status"] == "down"
        assert backend.call("verify_service", {"target": "HOST-001"})["passed"] is True

def test_preview_version_idempotency_rollback_and_verification_contract():
    path, scenario = _world("conformance", seed=31, fault_id="W2", target="HOST-001", difficulty="L1")
    fix = scenario["ground_truth"]["fix"]
    with SQLiteBackend(path) as backend:
        first = backend.call("preview_change", fix)
        stale = backend.call("preview_change", fix)
        applied = backend.call("apply_change", {"change_token": first["change_token"], "idempotency_key": "stable-key"})
        assert backend.call("apply_change", {"change_token": first["change_token"], "idempotency_key": "stable-key"}) == applied
        assert backend.call("get_change_status", {"idempotency_key": "stable-key"})["response"] == applied
        with pytest.raises(IdempotencyConflictError): backend.call("rollback_change", {"change_id": applied["change_id"], "idempotency_key": "stable-key"})
        with pytest.raises(VersionConflictError): backend.call("apply_change", {"change_token": stale["change_token"], "idempotency_key": "stale-key"})
        assert backend.call("verify_service", {"target": "HOST-001"})["passed"] is True
        rolled_back = backend.call("rollback_change", {"change_id": applied["change_id"], "idempotency_key": "rollback-key"})
        assert rolled_back["status"] == "rolled_back"
        assert backend.call("rollback_change", {"change_id": applied["change_id"], "idempotency_key": "rollback-key"}) == rolled_back
        assert backend.call("verify_service", {"target": "HOST-001"})["passed"] is False
        with pytest.raises(ChangeConflictError): backend.call("rollback_change", {"change_id": applied["change_id"], "idempotency_key": "second-rollback"})

def test_kpi_names_and_scenario_labels_are_exact():
    expected = {
        "W1": "intermediate_switch_failure", "W2": "incorrect_default_gateway",
        "W3": "packet_loss_misconfiguration", "W4": "bandwidth_limit_misconfiguration",
        "W5": "excessive_delay_misconfiguration", "N0": "no_fault_detected",
    }
    assert {key: value["root_cause"] for key, value in FAULTS.items()} == expected
    path, _ = _world("kpis", seed=37, fault_id="N0", target="HOST-001", difficulty="L1")
    with SQLiteBackend(path) as backend:
        names = [sample["metric"] for sample in backend.call("get_kpi", {"target": "HOST-001"})["samples"]]
    assert names == ["throughput_mbps", "latency_ms", "packet_loss_pct", "reachability_pct"]

def test_operator_requests_describe_user_symptoms_without_revealing_causes():
    expected_phrases = {
        "W1": "lost access to the team server", "W2": "cannot connect to the company intranet",
        "W3": "audio repeatedly drops out", "W4": "shared server is unusually slow",
        "W5": "noticeable conversation lag", "N0": "current condition is unknown",
    }
    forbidden_hints = {"intermediate switch", "backup path", "default gateway", "packet loss", "bandwidth cap", "excessive latency"}
    for fault_id, phrase in expected_phrases.items():
        _, scenario = _world(f"request-{fault_id}", seed=43, fault_id=fault_id, target="HOST-001", difficulty="L1")
        request = scenario["request"].lower()
        assert phrase in request
        assert not any(hint in request for hint in forbidden_hints)

@pytest.mark.parametrize(
    ("fault_id", "config_param", "link_field", "injected", "restored"),
    [
        ("W3", "loss_pct", "loss_pct", 12.0, 0.1),
        ("W4", "bandwidth_mbps", "capacity_mbps", 10.0, 100.0),
        ("W5", "delay_ms", "delay_ms", 120.0, 5.0),
    ],
)
def test_tc_faults_mutate_both_real_host_egress_links_and_apply_rollback_in_sync(
    fault_id: str, config_param: str, link_field: str, injected: float, restored: float
):
    path, scenario = _world(f"tc-binding-{fault_id}", seed=47, fault_id=fault_id, target="HOST-001", difficulty="L1")
    with SQLiteBackend(path) as backend:
        initial = backend.snapshot()
        interface_nodes = {item["interface_id"]: item["node_id"] for item in initial["interfaces"]}
        egress = [link for link in initial["links"] if interface_nodes[link["source_interface"]] == "HOST-001"]
        unrelated = [link for link in initial["links"] if interface_nodes[link["source_interface"]] != "HOST-001"]
        assert len(egress) == 2
        assert {link[link_field] for link in egress} == {injected}
        assert all(link[link_field] != injected for link in unrelated)
        config = next(item for item in initial["configuration"] if item["param"] == config_param)
        assert config["current_value"] == injected and config["reference_value"] == restored
        applied = _apply(backend, scenario["ground_truth"]["fix"], f"tc-apply-{fault_id}")
        restored_snapshot = backend.snapshot()
        restored_egress = [link for link in restored_snapshot["links"] if interface_nodes[link["source_interface"]] == "HOST-001"]
        assert {link[link_field] for link in restored_egress} == {restored}
        backend.call("rollback_change", {"change_id": applied["change_id"], "idempotency_key": f"tc-rollback-{fault_id}"})
        rolled_back = backend.snapshot()
        rollback_egress = [link for link in rolled_back["links"] if interface_nodes[link["source_interface"]] == "HOST-001"]
        assert {link[link_field] for link in rollback_egress} == {injected}

@pytest.mark.parametrize("fault_id", ["W1", "W2", "W3", "W4", "W5", "N0"])
def test_l3_world_references_only_existing_nodes_interfaces_and_targets(fault_id: str):
    path, _ = _world(f"references-{fault_id}", seed=53, fault_id=fault_id, target="HOST-001", difficulty="L3")
    with SQLiteBackend(path) as backend:
        snapshot = backend.snapshot()
    node_ids = {item["node_id"] for item in snapshot["nodes"]}
    interface_ids = {item["interface_id"] for item in snapshot["interfaces"]}
    assert all(item["node_id"] in node_ids for item in snapshot["interfaces"])
    assert all(item["source_interface"] in interface_ids and item["target_interface"] in interface_ids for item in snapshot["links"])
    assert all(item["src_host"] in node_ids and item["dst_host"] in node_ids for item in snapshot["flows"])
    db = sqlite3.connect(path)
    try:
        assert all(target in node_ids for (target,) in db.execute("SELECT target FROM alarms"))
        assert all(target in node_ids for (target,) in db.execute("SELECT target FROM logs"))
    finally:
        db.close()
