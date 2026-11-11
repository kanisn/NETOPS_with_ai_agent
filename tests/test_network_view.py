import hashlib
import json
import shutil
from pathlib import Path

import pytest

from tests.support_paths import workspace_for, work_root
from ccs.bench.scenarios import create_world
from ccs.netops.sqlite_backend import SQLiteBackend
from ccs.network_view import preview_network, read_network


WORK = workspace_for("test_network_view")


def _assert_safe_working_directory() -> None:
    root = work_root().resolve()
    candidate = WORK.resolve()
    assert candidate.parent == root
    assert candidate != root


@pytest.fixture(autouse=True, scope="module")
def clean_working_directory():
    _assert_safe_working_directory()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    yield
    _assert_safe_working_directory()
    if WORK.exists():
        shutil.rmtree(WORK)


def _file_evidence(root: Path) -> dict[str, tuple[str, int, int]]:
    return {
        str(path.relative_to(root)): (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            path.stat().st_size,
            path.stat().st_mtime_ns,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _configuration(state: dict, param: str) -> dict:
    return next(
        item
        for item in state["configuration"]
        if item["target"] == "HOST-001" and item["param"] == param
    )


def _kpi(state: dict, metric: str) -> dict:
    return next(item for item in state["kpis"] if item["metric"] == metric)


@pytest.mark.parametrize(
    ("fault", "changed_param", "value", "reference", "degraded_metrics"),
    [
        ("W1", "active_path", "primary", "primary", {"throughput_mbps", "latency_ms", "packet_loss_pct", "reachability_pct"}),
        ("W2", "default_gateway", "10.0.1.254", "10.0.1.1", {"throughput_mbps", "latency_ms", "packet_loss_pct", "reachability_pct"}),
        ("W3", "loss_pct", 12.0, 0.1, {"throughput_mbps", "packet_loss_pct", "reachability_pct"}),
        ("W4", "bandwidth_mbps", 10.0, 100.0, {"throughput_mbps"}),
        ("W5", "delay_ms", 120.0, 5.0, {"throughput_mbps", "latency_ms"}),
        ("N0", None, None, None, set()),
    ],
)
def test_preview_projects_each_wired_world(
    fault: str,
    changed_param: str | None,
    value: object,
    reference: object,
    degraded_metrics: set[str],
) -> None:
    state = preview_network(WORK / "preview", fault=fault, seed=17, difficulty="L1")

    assert state["available"] is True
    assert state["source"] == "preview"
    assert state["backend_id"] == "sqlite-wired-v1"
    assert state["target"] == "HOST-001"
    assert {item["param"] for item in state["configuration"]} == {
        "active_path", "admin_state", "default_gateway", "loss_pct",
        "bandwidth_mbps", "delay_ms",
    }
    assert {item["metric"] for item in state["kpis"]} == {
        "throughput_mbps", "latency_ms", "packet_loss_pct", "reachability_pct",
    }
    assert {item["metric"] for item in state["kpis"] if item["status"] == "degraded"} == degraded_metrics
    assert {node["id"] for node in state["topology"]["nodes"]} >= {
        "HOST-001", "ROUTER-001", "SERVER-001", "SWITCH-PRIMARY", "SWITCH-BACKUP",
    }
    assert state["topology"]["interfaces"] and state["topology"]["links"]
    if changed_param is not None:
        item = _configuration(state, changed_param)
        assert item["value"] == value and item["reference_value"] == reference
    else:
        assert all(item["at_reference"] for item in state["configuration"])
        assert all(item["status"] == "ok" for item in state["kpis"])
        assert all(item["status"] == "cleared" for item in state["alarms"])

    rendered = json.dumps(state, sort_keys=True)
    assert "ground_truth" not in rendered and "registry" not in rendered
    assert "flows" not in state


def test_preview_cache_is_immutable() -> None:
    workspace = WORK / "cache"
    first = preview_network(workspace, fault="W3", seed=23, difficulty="L2")
    before = _file_evidence(workspace)
    assert preview_network(workspace, fault="W3", seed=23, difficulty="L2") == first
    assert _file_evidence(workspace) == before


def test_run_view_tracks_w1_reroute_and_never_mutates_run_files() -> None:
    run_dir = WORK / "runs" / "D0_mock_wired_view"
    episode = "episode-0001"
    episode_dir = run_dir / "episodes" / episode
    db_path = episode_dir / "network.sqlite"
    episode_dir.mkdir(parents=True)
    scenario = create_world(db_path, seed=29, fault_id="W1", target="HOST-001", difficulty="L1")
    (episode_dir / "scenario.restricted.json").write_text(
        json.dumps(
            {
                "fault_id": scenario["fault_id"],
                "seed": scenario["seed"],
                "target": scenario["target"],
                "ground_truth": {"secret": "MUST-NOT-LEAK"},
                "registry": [{"value": "MUST-NOT-LEAK"}],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(
        json.dumps({"run_id": run_dir.name, "status": "RUNNING", "episodes": []}),
        encoding="utf-8",
    )

    before = _file_evidence(run_dir)
    initial = read_network(run_dir)
    assert _file_evidence(run_dir) == before
    assert initial["episode_id"] == episode and initial["available"] is True
    assert _configuration(initial, "active_path")["value"] == "primary"
    assert _kpi(initial, "reachability_pct")["value"] == 0.0
    assert next(node for node in initial["topology"]["nodes"] if node["id"] == "SWITCH-PRIMARY")["status"] == "down"

    with SQLiteBackend(db_path) as backend:
        preview = backend.call(
            "preview_change",
            {
                "target": "HOST-001",
                "param": "active_path",
                "value": "backup",
                "reason": "Reroute around the failed primary switch.",
            },
        )
        backend.call(
            "apply_change",
            {"change_token": preview["change_token"], "idempotency_key": "wired-view-reroute"},
        )
        final_snapshot = backend.snapshot()
    (episode_dir / "final-state.restricted.json").write_text(
        json.dumps(final_snapshot, sort_keys=True), encoding="utf-8"
    )
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "status": "COMPLETED",
                "episodes": [{"episode_id": episode, "fault": "W1", "seed": 29}],
            }
        ),
        encoding="utf-8",
    )

    sealed = _file_evidence(run_dir)
    recovered = read_network(run_dir, episode_id=episode)
    assert _file_evidence(run_dir) == sealed
    assert _configuration(recovered, "active_path")["value"] == "backup"
    assert all(item["status"] == "ok" for item in recovered["kpis"])
    assert all(item["status"] == "cleared" for item in recovered["alarms"])
    assert recovered["changes"] == [
        {
            "id": "CHG-000001",
            "target": "HOST-001",
            "param": "active_path",
            "before": "primary",
            "after": "backup",
            "status": "applied",
        }
    ]
    rendered = json.dumps(recovered, sort_keys=True)
    assert "MUST-NOT-LEAK" not in rendered
    assert "change_token" not in rendered and "idempotency" not in rendered
    assert not list(episode_dir.glob("network.sqlite-*"))


def test_mismatched_final_snapshot_is_not_projected() -> None:
    run_dir = WORK / "runs" / "tampered_final"
    episode_dir = run_dir / "episodes" / "episode-0001"
    episode_dir.mkdir(parents=True)
    db_path = episode_dir / "network.sqlite"
    scenario = create_world(db_path, seed=31, fault_id="N0", target="HOST-001", difficulty="L1")
    (episode_dir / "scenario.restricted.json").write_text(
        json.dumps({"fault_id": "N0", "seed": scenario["seed"], "target": scenario["target"]}),
        encoding="utf-8",
    )
    with SQLiteBackend(db_path) as backend:
        final_snapshot = backend.snapshot()
    final_snapshot["configuration"][0]["current_value"] = "tampered"
    (episode_dir / "final-state.restricted.json").write_text(json.dumps(final_snapshot), encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps({"run_id": run_dir.name}), encoding="utf-8")

    assert read_network(run_dir, "episode-0001")["available"] is False


def test_pending_episode_is_unavailable_and_inputs_reject_traversal() -> None:
    run_dir = WORK / "runs" / "pending_run"
    (run_dir / "episodes" / "episode-0001").mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps({"run_id": "pending_run", "status": "RUNNING", "episodes": []}),
        encoding="utf-8",
    )
    assert read_network(run_dir)["available"] is False
    assert read_network(run_dir, "episode-0001")["available"] is False
    with pytest.raises(ValueError):
        read_network(run_dir, "../manifest.json")
    with pytest.raises(ValueError):
        preview_network(WORK, fault="W3", seed=True, difficulty="L1")
    with pytest.raises(ValueError):
        preview_network(WORK, fault="W6", seed=1, difficulty="L1")
    with pytest.raises(ValueError):
        preview_network(WORK, fault="W3", seed=1, difficulty="L1", target="ROUTER-001")

