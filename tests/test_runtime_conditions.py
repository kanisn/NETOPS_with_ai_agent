from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3
import uuid

import pytest

from tests.support_paths import isolated_ai_config, workspace_for
from ccs.monitor import read_activity
from ccs.pacing import write_control
from ccs.runner import run


PROJECT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_runtime_conditions")
AI_CONFIG = isolated_ai_config("test_runtime_conditions")


@pytest.fixture
def work() -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / f"case-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def _runbook(path: Path) -> None:
    path.write_text(
        """---
doc_id: RB-OPERATOR-SELECTED
version: 1
tenant: synthetic-tenant
classification: internal
source: operator-selection
---
# Alpha Sentinel Recovery

## Verification
Alpha sentinel video quality requires checking the current QoS profile.
""",
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_selected_runbook_and_seed_memory_are_snapshotted_with_explicit_provenance(work: Path) -> None:
    selected = work / "selected"
    selected.mkdir()
    _runbook(selected / "selected.md")
    seed = [{
        "id": "operator-note-1",
        "title": "Prior operator note",
        "content": "HOST-001 HOST-001 alpha sentinel appeared in an external note.",
        "source_kind": "uploaded-note",
        "source_run_id": "external-run-7",
    }]
    run_dir, summary = await run(
        PROJECT / "configs/system.xml",
        AI_CONFIG,
        faults=["W4"],
        seeds=[1],
        output_root=work / "runs",
        request_override="Alpha sentinel video quality degraded; restore service.",
        runbooks_override=selected,
        initial_memory=seed,
        rag_enabled=True,
        experiment_metadata={"interface": "web", "label": "selected-inputs"},
    )
    assert summary["status"] == "COMPLETED"
    assert summary["successful_episodes"] == 1
    assert (run_dir / "inputs/runbooks/selected.md").read_text(encoding="utf-8") == (selected / "selected.md").read_text(encoding="utf-8")
    assert json.loads((run_dir / "inputs/initial-memory.json").read_text(encoding="utf-8")) == seed

    events = read_activity(run_dir)
    runbook_result = next(
        event for event in events
        if event["component"] == "runbook" and event["action"] == "search" and event["status"] == "succeeded"
    )
    assert runbook_result["details"]["results"][0]["doc_id"] == "RB-OPERATOR-SELECTED"
    memory_result = next(
        event for event in events
        if event["component"] == "memory" and event["action"] == "search" and event["status"] == "succeeded"
    )
    imported = next(item for item in memory_result["details"]["results"] if item["record_id"] == "operator-note-1")
    assert imported["verified_outcome"] == "unverified_operator_reference"
    assert imported["payload"]["provenance"] == {
        "origin": "operator-imported-reference",
        "validation_status": "unverified",
        "reference_only": True,
        "source_kind": "uploaded-note",
        "source_run_id": "external-run-7",
    }
    connection = sqlite3.connect(run_dir / "memory.sqlite")
    try:
        outcome = connection.execute(
            "SELECT verified_outcome FROM memory_records WHERE record_id=?", ("operator-note-1",)
        ).fetchone()[0]
    finally:
        connection.close()
    assert outcome == "unverified_operator_reference"
    assert summary["input_conditions"]["runbooks"]["count"] == 1
    assert summary["input_conditions"]["initial_memory"]["count"] == 1
    assert summary["timing"]["initial_delay_seconds"] == 0
    assert summary["timing"]["final_delay_seconds"] == 0


@pytest.mark.asyncio
async def test_empty_runbook_selection_and_disabled_rag_complete_mock_flow(work: Path) -> None:
    empty = work / "empty-selection"
    empty.mkdir()
    run_dir, summary = await run(
        PROJECT / "configs/system.xml",
        AI_CONFIG,
        faults=["N0"],
        seeds=[2],
        output_root=work / "runs",
        runbooks_override=empty,
        initial_memory=[],
        rag_enabled=False,
        memory_off=True,
        experiment_metadata={"interface": "web", "label": "empty-inputs"},
    )
    assert summary["status"] == "COMPLETED"
    assert summary["successful_episodes"] == 1
    assert summary["input_conditions"]["rag_enabled"] is False
    assert summary["input_conditions"]["runbooks"]["count"] == 0
    assert summary["input_conditions"]["initial_memory"]["count"] == 0
    assert list((run_dir / "inputs/runbooks").rglob("*.md")) == []
    events = read_activity(run_dir)
    skipped = [event for event in events if event["action"] == "search" and event["status"] == "skipped"]
    assert any(event["component"] == "runbook" and event["details"]["results"] == []
        and event["details"]["empty"] is True and event["details"]["disabled"] is True
        for event in skipped)
    assert any(event["component"] == "memory" and event["details"]["results"] == [] and event["details"]["disabled"] is True for event in skipped)
    diagnosis_start = next(event for event in events if event["component"] == "diagnosis" and event["action"] == "investigate" and event["status"] == "started")
    assert diagnosis_start["details"]["context"]["runbooks"] == []
    assert diagnosis_start["details"]["context"]["history"] == []


@pytest.mark.asyncio
async def test_runner_applies_real_delay_in_parent_and_child_activity(work: Path) -> None:
    control = work / "shared-control.json"
    write_control(control, 0.01)
    run_dir, summary = await run(
        PROJECT / "configs/system.xml",
        AI_CONFIG,
        faults=["N0"],
        seeds=[3],
        output_root=work / "runs",
        delay_control_path=control,
    )
    assert summary["status"] == "COMPLETED"
    timing = summary["timing"]
    assert timing["initial_delay_seconds"] == timing["final_delay_seconds"] == 0.01
    assert timing["delayed_event_count"] >= 20
    assert timing["delay_union_seconds"] >= 0.15
    assert timing["summed_worker_delay_seconds"] + 1e-9 >= timing["delay_union_seconds"]
    assert timing["elapsed_wall_seconds"] > timing["delay_union_seconds"]
    effective = json.loads((run_dir / "effective-config.json").read_text(encoding="utf-8"))
    pacing = effective["input_conditions"]["pacing"]
    assert pacing["runtime_request_timeout_seconds"] > pacing["configured_request_timeout_seconds"]
    writers = {json.loads(line)["writer_id"] for path in (run_dir / "pacing").glob("*.jsonl")
        for line in path.read_text(encoding="utf-8").splitlines() if line}
    assert "run" in writers
    assert any(writer.startswith("mcp-server-") for writer in writers)
    assert any(writer.startswith("a2a-diagnosis-") for writer in writers)
