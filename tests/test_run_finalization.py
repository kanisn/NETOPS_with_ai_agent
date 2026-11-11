from __future__ import annotations

import json
from decimal import Decimal
import os
from pathlib import Path
from types import SimpleNamespace
import uuid

import pytest

from tests.support_paths import isolated_ai_config, workspace_for
import ccs.runner as runner


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = workspace_for("test_run_finalization")
AI_CONFIG = isolated_ai_config("test_run_finalization")


class FakeActivity:
    def __init__(self, failure: BaseException | None = None):
        self.failure = failure

    def emit(self, *args, **kwargs):
        if self.failure:
            raise self.failure


def fixture_run(run_dir: Path) -> tuple[Path, dict, dict, SimpleNamespace]:
    (run_dir / "episodes" / "episode-0001").mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": "run-finalization",
        "status": "COMPLETED",
        "models": {"operation": "scripted-mock", "diagnosis": "scripted-mock"},
        "episodes": [{"episode_id": "episode-0001", "status": "CLOSED", "fault": "W1", "seed": 1, "outcome": "RECOVERED", "utility": 1, "diagnosis_correct": True, "latency_seconds": 0.1}],
    }
    effective = {"system": {"memory_enabled": True}}
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    ai = SimpleNamespace(ledger_path=run_dir / "budget.sqlite", budget_usd=Decimal("5"))
    return run_dir, manifest, effective, ai


def call_finalize(run_dir: Path, manifest: dict, effective: dict, ai: SimpleNamespace, activity=None):
    return runner._finalize_run(
        run_dir,
        manifest,
        effective,
        {"condition_hash": "fixed"},
        1,
        [],
        ai,
        "mock",
        activity or FakeActivity(),
        "operation-id",
    )


@pytest.fixture
def scratch_run() -> Path:
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    return WORK_ROOT / f"run-{uuid.uuid4().hex}"


def mock_integrity_and_ledger(monkeypatch) -> None:
    monkeypatch.setattr(runner, "validate_and_merge", lambda run_dir: {"valid": True, "event_count": 0, "errors": []})
    monkeypatch.setattr(runner, "summarize_timing", lambda *args, **kwargs: {"elapsed_wall_seconds": 0.1, "delay_union_seconds": 0.0, "summed_worker_delay_seconds": 0.0, "delayed_event_count": 0})
    monkeypatch.setattr("ccs.evaluation.ledger.build_ledger", lambda run_dir, registry: {"valid": True, "items": []})
    monkeypatch.setattr("ccs.monitor.write_snapshot", lambda run_dir: None)


@pytest.mark.parametrize(
    ("phase", "inject"),
    [
        ("integrity", lambda monkeypatch: monkeypatch.setattr(runner, "validate_and_merge", lambda path: (_ for _ in ()).throw(PermissionError("secret should not be recorded")))),
        ("ledger", lambda monkeypatch: monkeypatch.setattr("ccs.evaluation.ledger.build_ledger", lambda *args: (_ for _ in ()).throw(PermissionError("secret should not be recorded")))),
        ("effective_config", lambda monkeypatch: fail_write_for(monkeypatch, "effective-config.json")),
        ("manifest", lambda monkeypatch: fail_write_for(monkeypatch, "manifest.json")),
        ("summary", lambda monkeypatch: fail_write_for(monkeypatch, "summary.json")),
        ("reports", lambda monkeypatch: monkeypatch.setattr("ccs.reporting.write_reports", lambda *args: (_ for _ in ()).throw(PermissionError("secret should not be recorded")))),
        ("terminal_event", lambda monkeypatch: None),
        ("monitor_snapshot", lambda monkeypatch: monkeypatch.setattr("ccs.monitor.write_snapshot", lambda path: (_ for _ in ()).throw(PermissionError("secret should not be recorded")))),
        ("artifact_hashes", lambda monkeypatch: monkeypatch.setattr(runner, "_seal_artifacts", lambda path: (_ for _ in ()).throw(PermissionError("secret should not be recorded")))),
        ("seal_manifest", lambda monkeypatch: fail_seal_manifest_write(monkeypatch)),
    ],
)
def test_finalization_errors_are_terminal_unsealed_and_safe(scratch_run, monkeypatch, phase, inject):
    mock_integrity_and_ledger(monkeypatch)
    run_dir, manifest, effective, ai = fixture_run(scratch_run)
    activity = FakeActivity(PermissionError("secret should not be recorded")) if phase == "terminal_event" else FakeActivity()
    inject(monkeypatch)

    error_message = "Access is denied" if phase == "seal_manifest" else "secret should not be recorded"
    with pytest.raises(PermissionError, match=error_message):
        call_finalize(run_dir, manifest, effective, ai, activity)

    saved = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    failure = json.loads((run_dir / "finalization-error.json").read_text(encoding="utf-8"))
    assert saved["status"] == "ABORTED"
    assert saved["finished_at_utc"]
    expected_error = {"phase": phase, "error_type": "PermissionError"}
    if phase == "seal_manifest":
        expected_error.update({"errno": 13, "winerror": 5})
    assert saved["finalization_error"] == expected_error
    assert failure == saved["finalization_error"]
    assert "secret" not in json.dumps(saved).lower()
    assert "secret" not in json.dumps(failure).lower()
    assert not saved.get("artifact_hashes")
    assert not (run_dir / "report.md").exists()
    assert not (run_dir / "report.html").exists()
    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary["status"] == "ABORTED"
        assert summary["successful_episodes"] is None
        assert summary["diagnoses_correct"] is None
        assert summary["integrity_valid"] is False


def fail_write_for(monkeypatch, basename: str) -> None:
    original = runner.write_json
    failed = False

    def injected(path, value):
        nonlocal failed
        if Path(path).name == basename and not failed:
            failed = True
            raise PermissionError("secret should not be recorded")
        return original(path, value)

    monkeypatch.setattr(runner, "write_json", injected)


def fail_seal_manifest_write(monkeypatch) -> None:
    original = runner.write_json

    def injected(path, value):
        if Path(path).name == "manifest.json" and value.get("artifact_hashes"):
            raise win32_sharing_error()
        return original(path, value)

    monkeypatch.setattr(runner, "write_json", injected)


def test_finalization_success_writes_summary_and_seal(scratch_run, monkeypatch):
    mock_integrity_and_ledger(monkeypatch)
    run_dir, manifest, effective, ai = fixture_run(scratch_run)

    returned_dir, summary = call_finalize(run_dir, manifest, effective, ai)

    saved = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert returned_dir == run_dir
    assert summary["status"] == "COMPLETED"
    assert summary["successful_episodes"] == 1
    assert saved["status"] == "COMPLETED"
    assert saved["artifact_hashes"]
    assert "finalization_error" not in saved
    assert (run_dir / "report.md").exists()
    assert (run_dir / "report.html").exists()


def win32_sharing_error() -> PermissionError:
    error = PermissionError(13, "Access is denied")
    error.winerror = 5
    return error


def test_write_json_retries_transient_sharing_violation(scratch_run, monkeypatch):
    scratch_run.mkdir(parents=True)
    target = scratch_run / "manifest.json"
    target.write_text('{"old": true}', encoding="utf-8")
    real_replace = runner.os.replace
    attempts = 0
    delays = []

    def replace(source, destination):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise win32_sharing_error()
        return real_replace(source, destination)

    monkeypatch.setattr(runner.os, "replace", replace)
    monkeypatch.setattr(runner.time, "sleep", delays.append)

    runner.write_json(target, {"new": True})

    assert attempts == 3
    assert delays == list(runner._REPLACE_RETRY_DELAYS[:2])
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}
    assert not target.with_name(target.name + ".writing").exists()


def test_write_json_permanent_sharing_violation_is_bounded_and_propagated(scratch_run, monkeypatch):
    scratch_run.mkdir(parents=True)
    target = scratch_run / "manifest.json"
    original = '{"old": true}'
    target.write_text(original, encoding="utf-8")
    attempts = 0
    delays = []

    def replace(source, destination):
        nonlocal attempts
        attempts += 1
        raise win32_sharing_error()

    monkeypatch.setattr(runner.os, "replace", replace)
    monkeypatch.setattr(runner.time, "sleep", delays.append)

    with pytest.raises(PermissionError) as raised:
        runner.write_json(target, {"new": True})

    assert attempts == len(runner._REPLACE_RETRY_DELAYS) + 1
    assert delays == list(runner._REPLACE_RETRY_DELAYS)
    assert raised.value.winerror == 5
    assert target.read_text(encoding="utf-8") == original
    assert not target.with_name(target.name + ".writing").exists()


@pytest.mark.skipif(os.name != "nt", reason="requires native Windows file sharing semantics")
def test_write_json_recovers_from_native_win32_delete_share_lock(scratch_run, monkeypatch):
    import ctypes
    from ctypes import wintypes

    scratch_run.mkdir(parents=True)
    target = scratch_run / "manifest.json"
    target.write_text('{"old": true}', encoding="utf-8")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateFileW(str(target), 0x80000000, 0x00000001, None, 3, 0x00000080, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    real_replace = runner.os.replace
    attempts = 0

    def replace_and_release_after_retries(source, destination):
        nonlocal attempts, handle
        attempts += 1
        try:
            return real_replace(source, destination)
        except PermissionError as error:
            assert getattr(error, "winerror", None) in {5, 32, 33}
            if attempts == 2:
                kernel.CloseHandle(handle)
                handle = None
            raise

    monkeypatch.setattr(runner.os, "replace", replace_and_release_after_retries)
    monkeypatch.setattr(runner.time, "sleep", lambda seconds: None)
    try:
        runner.write_json(target, {"new": True})
    finally:
        if handle is not None:
            kernel.CloseHandle(handle)

    assert attempts == 3
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}


@pytest.mark.asyncio
async def test_run_abort_records_type_and_reraises_original_exception(scratch_run, monkeypatch):
    output_root = scratch_run / "runs"
    output_root.mkdir(parents=True)
    original_error = win32_sharing_error()

    async def abort_episode(*args, **kwargs):
        raise original_error

    monkeypatch.setattr(runner, "execute_episode", abort_episode)
    with pytest.raises(PermissionError) as raised:
        await runner.run(
            PROJECT_ROOT / "configs" / "system.xml",
            AI_CONFIG,
            mode="mock",
            faults=["W1"],
            seeds=[1],
            output_root=output_root,
        )

    assert raised.value is original_error
    run_dir = next(output_root.iterdir())
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    failure = json.loads((run_dir / "run-error.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ABORTED"
    assert manifest["finished_at_utc"]
    assert failure == {"phase": "episode_execution", "error_type": "PermissionError", "errno": 13, "winerror": 5}
    assert not (run_dir / "summary.json").exists()
    assert not manifest.get("artifact_hashes")


