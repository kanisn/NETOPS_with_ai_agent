"""Evidence and security checks for the read-only Result Analysis backend."""

from __future__ import annotations

import asyncio
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
import uuid
import xml.etree.ElementTree as ET

import pytest

from tests.support_paths import isolated_ai_config, workspace_for
from ccs.run_analysis import analyze_run
from ccs.runner import run
from ccs.scenario_catalog import SCENARIOS
from ccs.studio_markup import BODY
from ccs.studio_script import SCRIPT
from ccs.web_console import WebConsoleServer


PROJECT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_run_analysis")
AI_CONFIG = isolated_ai_config("test_run_analysis")


def _working(name: str) -> Path:
    path = WORK / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def actual_mock_run() -> Path:
    """Save one real mock run containing the normal N0 and rerouted W1 paths."""

    directory = _working("actual-n0-w1")
    run_dir, summary = asyncio.run(
        run(
            PROJECT / "configs/system.xml",
            AI_CONFIG,
            mode="mock",
            faults=["N0", "W1"],
            seeds=[17],
            repeat=1,
            memory_off=True,
            output_root=directory / "runs",
            rag_enabled=False,
        )
    )
    assert summary["status"] == "COMPLETED"
    return run_dir


def test_actual_n0_w1_analysis_uses_observed_data_and_is_read_only(actual_mock_run: Path) -> None:
    watched = [
        actual_mock_run / "manifest.json",
        actual_mock_run / "summary.json",
        *sorted(actual_mock_run.glob("episodes/*/result.json")),
        *sorted(actual_mock_run.glob("episodes/*/oracle.json")),
        *sorted(actual_mock_run.glob("episodes/*/network.sqlite")),
    ]
    before = {path: _digest(path) for path in watched}
    before_mtime = {path: path.stat().st_mtime_ns for path in watched}

    analysis = analyze_run(actual_mock_run)

    assert analysis["ready"] is True
    assert analysis["complete"] is True
    assert analysis["sealed"] is True
    assert analysis["integrity"]["source"] == "recorded_integrity"
    assert analysis["integrity"]["live_verified"] is False
    assert analysis["timing"]["elapsed_wall_seconds"] >= 0
    assert "elapsed_minus_delay_union_seconds_estimate" in analysis["timing"]
    assert "no_delay" not in analysis["timing"]

    by_fault = {episode["fault"]: episode for episode in analysis["episodes"]}
    normal, changed = by_fault["N0"], by_fault["W1"]
    assert normal["outcome"] == "NO_CHANGE"
    assert normal["configuration_changes"] == []
    assert any(item["kind"] == "normal_no_action" for item in normal["observations"])
    assert normal["verify"]["passed"] is True
    assert normal["kpi_changes"]
    assert all(item["before_source"] == "observed_get_kpi" for item in normal["kpi_changes"])
    assert any(item["after"] is not None for item in normal["kpi_changes"])

    assert changed["outcome"] == "RECOVERED"
    assert changed["configuration_changes"]
    assert changed["configuration_changes"][0]["before"] != changed["configuration_changes"][0]["after"]
    assert changed["diagnosis"]["confidence_kind"] == "provider_reported_uncalibrated"
    assert changed["oracle"]["utility"] == 1
    assert "details" not in changed["oracle"]
    reachability = next(
        item for item in changed["kpi_changes"]
        if item["target"] == "HOST-001" and item["metric"] == "reachability_pct"
    )
    assert reachability["before"] == 0
    assert reachability["after"] == 99.9
    assert reachability["after_source"] == "final_state_read"
    assert changed["configuration_changes"][0]["param"] == "active_path"
    assert changed["configuration_changes"][0]["before"] == "primary"
    assert changed["configuration_changes"][0]["after"] == "backup"
    assert changed["diagnosis"]["root_cause"] == "intermediate_switch_failure"
    assert changed["diagnosis"]["root_cause_label"]["ko"] == "중간 스위치 장애"
    assert changed["scenario"] == SCENARIOS["W1"]
    assert all(item["after"] is not None for item in changed["kpi_changes"])

    counts = analysis["activity_counts"]
    assert counts["tool_calls"]["total"] == counts["tool_calls"]["operation"] + counts["tool_calls"]["diagnosis"]
    assert counts["by_component"]["mcp"] > counts["tool_calls"]["total"]
    assert counts["runbook_queries"] == 0 and counts["runbook_hits"] == 0
    assert counts["runbook_disabled"] == 2
    assert counts["memory_queries"] == 0 and counts["memory_hits"] == 0
    assert counts["memory_disabled"] == 2
    assert counts["a2a_handoffs"] == 2

    rendered = json.dumps(analysis, ensure_ascii=False).casefold()
    for forbidden in (
        "ground_truth", "registry", "expected_state_reached", "initial_state_hash",
        "final_state_hash", "runbook_ids", "memory_ids", "api_key", "raw_response",
    ):
        assert forbidden not in rendered
    assert {path: _digest(path) for path in watched} == before
    assert {path: path.stat().st_mtime_ns for path in watched} == before_mtime


@pytest.mark.parametrize(
    "outcome",
    ["NO_CHANGE", "ESCALATED", "ROLLED_BACK", "DECLINED", "FAILED", "ABORTED"],
)
def test_episode_outcomes_remain_distinct(outcome: str) -> None:
    run_dir = _working("outcome") / "D0_mock_outcomes"
    episode_dir = run_dir / "episodes" / "episode-0001"
    episode_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "status": "COMPLETED",
                "episodes": [
                    {
                        "episode_id": "episode-0001",
                        "fault": "N0",
                        "seed": 1,
                        "outcome": outcome,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (episode_dir / "result.json").write_text(
        json.dumps(
            {
                "outcome": outcome,
                "diagnosis": {
                    "root_cause": "unknown",
                    "evidence": [{"ground_truth": "must-not-leak", "registry": ["secret-id"]}],
                },
                "memory_written": False,
            }
        ),
        encoding="utf-8",
    )
    analysis = analyze_run(run_dir)
    assert analysis["episodes"][0]["outcome"] == outcome
    rendered = json.dumps(analysis)
    assert "ground_truth" not in rendered and "registry" not in rendered


def test_aborted_partial_and_malformed_artifacts_are_ready_but_unsealed() -> None:
    run_dir = _working("partial") / "D0_mock_partial"
    episode_dir = run_dir / "episodes" / "episode-0001"
    episode_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "status": "ABORTED",
                "artifact_hashes": {"partial.json": "recorded-but-not-a-complete-seal"},
                "episodes": [{"episode_id": "episode-0001", "fault": "W1", "seed": 1}],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "integrity.json").write_text(
        json.dumps({"valid": True, "event_count": 0, "errors": []}),
        encoding="utf-8",
    )
    (episode_dir / "result.json").write_text("{broken", encoding="utf-8")

    analysis = analyze_run(run_dir, controller_status="ABORTED")

    assert analysis["status"] == "ABORTED"
    assert analysis["ready"] is True
    assert analysis["complete"] is False
    assert analysis["sealed"] is False
    assert analysis["episodes"][0]["outcome"] == "UNKNOWN"
    codes = {item["code"] for item in analysis["limitations"]}
    assert {"partial_terminal_run", "partial_or_malformed_artifacts", "not_recorded_as_sealed"} <= codes


def _write_system_config(workspace: Path, output_root: Path) -> Path:
    path = workspace / "config" / "system.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.parse(PROJECT / "configs/system.xml").getroot()
    paths = root.find("paths")
    assert paths is not None
    paths.set("output_root", str(output_root.resolve()))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def _request(server: WebConsoleServer, path: str, *, token: bool = True) -> tuple[int, dict]:
    parsed = urlsplit(server.url or "")
    query = parse_qs(parsed.query)
    suffix = ("&" if "?" in path else "?") + urlencode({"token": query["token"][0]}) if token else ""
    connection = HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    connection.request("GET", path + suffix)
    response = connection.getresponse()
    value = json.loads(response.read().decode())
    connection.close()
    return response.status, value


def test_studio_uses_shared_wired_story_and_topology_contract() -> None:
    assert "data.options?.scenarios" in SCRIPT
    assert "const SCENARIOS={};" in SCRIPT
    assert "networkTopologyNodes" in SCRIPT and "networkTopologyLinks" in SCRIPT
    assert "networkTopologyNodes" in BODY and "networkTopologyLinks" in BODY
    from ccs.bench.scenarios import FAULTS
    assert set(SCENARIOS) == set(FAULTS) == {"W1", "W2", "W3", "W4", "W5", "N0"}
    for fault in ("W1", "W2", "W3", "W4", "W5", "N0"):
        assert all(SCENARIOS[fault][field][language] for field in ("title", "impact", "goal") for language in ("ko", "en"))
        assert SCENARIOS[fault]["title"]["ko"] not in SCRIPT
    for legacy in ("CELL-", "SLICE-", "UPF", "GNB", "slice_throughput_mbps"):
        assert legacy not in SCRIPT and legacy not in BODY


def test_analysis_endpoint_requires_auth_known_path_and_controller_terminal(
    actual_mock_run: Path,
) -> None:
    workspace = _working("endpoint")
    system_path = _write_system_config(workspace, actual_mock_run.parent)
    server = WebConsoleServer(system_path, AI_CONFIG, workspace)
    record = {
        "run_id": actual_mock_run.name,
        "output_root": str(actual_mock_run.parent.resolve()),
        "run_dir": str(actual_mock_run.resolve()),
        "status": "COMPLETED",
        "conditions": {"faults": ["N0", "W1"], "seeds": [17], "rag_enabled": False},
    }
    server._state["runs"].append(record)
    server._state["active"] = {"run_id": actual_mock_run.name, "status": "RUNNING"}
    server._save_locked()
    server.start()
    try:
        status, _ = _request(server, f"/api/analysis?run_id={actual_mock_run.name}", token=False)
        assert status == 403
        status, error = _request(server, "/api/analysis?run_id=../../configs")
        assert status == 404 and error["error"]["type"] == "unknown_run"
        status, error = _request(server, f"/api/analysis?run_id={actual_mock_run.name}&extra=1")
        assert status == 400 and error["error"]["type"] == "invalid_request"

        status, active = _request(server, f"/api/analysis?run_id={actual_mock_run.name}")
        assert status == 200 and active["status"] == "RUNNING" and active["ready"] is False

        server._state["active"] = {"run_id": actual_mock_run.name, "status": "COMPLETED"}
        server._save_locked()
        status, completed = _request(server, f"/api/analysis?run_id={actual_mock_run.name}")
        assert status == 200 and completed["ready"] is True and completed["sealed"] is True
        assert completed["conditions"]["rag_enabled"] is False
    finally:
        server.stop()
