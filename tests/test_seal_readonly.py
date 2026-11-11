from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path

import pytest

from tests.support_paths import workspace_for
from ccs.core.bus import EventBus
from ccs.core.integrity import validate_and_merge
from ccs.reporting import compare_runs, verify_seal


WORKING_ROOT = workspace_for("test_seal_readonly")


@pytest.fixture
def sealed_run() -> Path:
    WORKING_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = WORKING_ROOT / f"run-{uuid.uuid4().hex}"
    run_dir.mkdir()
    try:
        bus = EventBus(run_dir, "runner", "run-readonly", "episode-a")
        bus.emit("G1", {"request": "inspect"}, "operator", "agent:operation")
        integrity = validate_and_merge(run_dir)
        assert integrity["valid"], integrity["errors"]

        artifact_hashes = {}
        for artifact in sorted(run_dir.rglob("*")):
            if artifact.is_file() and artifact.name != "manifest.json":
                relative = artifact.relative_to(run_dir).as_posix()
                artifact_hashes[relative] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        (run_dir / "manifest.json").write_text(
            json.dumps({"manifest_schema": "netops-run@1", "artifact_hashes": artifact_hashes}),
            encoding="utf-8",
        )
        yield run_dir
    finally:
        shutil.rmtree(run_dir)


def test_report_and_compare_leave_modified_sealed_merge_untouched(sealed_run: Path) -> None:
    merged = sealed_run / "events_merged.jsonl"
    damaged_bytes = b"preserve this invalid sealed artifact\n"
    merged.write_bytes(damaged_bytes)

    result = verify_seal(sealed_run)
    assert not result["valid"]
    assert any("Artifact mismatch: events_merged.jsonl" in error for error in result["errors"])
    assert merged.read_bytes() == damaged_bytes

    with pytest.raises(ValueError, match="Cannot compare an invalid run"):
        compare_runs([sealed_run])
    assert merged.read_bytes() == damaged_bytes


def test_report_keeps_existing_merge_when_source_events_fail_validation(sealed_run: Path) -> None:
    merged = sealed_run / "events_merged.jsonl"
    original_merge = merged.read_bytes()
    shard = next((sealed_run / "events").glob("*.jsonl"))
    shard.write_text("not json\n", encoding="utf-8")

    result = verify_seal(sealed_run)
    assert not result["valid"]
    assert any("invalid event" in error for error in result["errors"])
    assert merged.read_bytes() == original_merge
