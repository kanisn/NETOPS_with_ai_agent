"""Configured output-root and persisted web-run location regression checks."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import threading
import time
import uuid
import xml.etree.ElementTree as ET

import pytest

from tests.support_paths import workspace_for
from ccs.config import load_system
from ccs.web_console import WebConsoleServer


PROJECT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_web_output_root")


def _case(name: str) -> Path:
    path = WORK / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _set_output_root(system_path: Path, output_root: Path) -> Path:
    source = system_path if system_path.is_file() else PROJECT / "configs/system.xml"
    root = ET.parse(source).getroot()
    paths = root.find("paths")
    assert paths is not None
    paths.set("output_root", str(output_root.resolve()))
    system_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(system_path, encoding="utf-8", xml_declaration=True)
    return system_path


def _server(name: str, output_name: str = "configured-output") -> tuple[WebConsoleServer, Path, Path, Path]:
    base = _case(name)
    workspace = base / "workspace"
    workspace.mkdir()
    output_root = base / output_name
    system_path = _set_output_root(base / "config" / "system.xml", output_root)
    server = WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", workspace)
    return server, system_path, output_root.resolve(), base


def _payload(**updates: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "mode": "mock",
        "profile": "luna6",
        "faults": ["W1"],
        "seeds": [1],
        "repeat": 1,
        "request": "",
        "rag_enabled": True,
        "memory_enabled": True,
        "runbook_k": 3,
        "memory_k": 3,
        "delay_seconds": 0,
        "difficulty": "L1",
        "approval": "auto",
        "diagnosis_tool_budget": 8,
        "context_steps": 6,
        "max_agent_steps": 12,
    }
    payload.update(updates)
    return payload


def _wait_for_worker(server: WebConsoleServer) -> None:
    deadline = time.monotonic() + 5
    while server._worker is not None and time.monotonic() < deadline:
        time.sleep(0.02)
    assert server._worker is None


def _create_fake_run(root: Path, run_id: str, on_created: object) -> tuple[Path, dict[str, object]]:
    assert root.is_dir()
    run_dir = root / run_id
    run_dir.mkdir()
    manifest = {"run_id": run_id, "status": "RUNNING", "episodes": []}
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert callable(on_created)
    on_created(run_dir)
    summary: dict[str, object] = {"run_id": run_id, "status": "COMPLETED", "integrity_valid": True}
    manifest["status"] = "COMPLETED"
    (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return run_dir, summary


def test_start_uses_configured_output_for_snapshot_runner_and_public_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, _, output_root, base = _server("configured-root")
    captured: dict[str, Path] = {}
    mutable_decoy = (base / "mutable-decoy").resolve()

    assert not output_root.exists()
    initial = server.console_state()
    assert Path(initial["options"]["output_root"]) == output_root
    assert not output_root.exists()

    async def fake_run(system_path: Path, _ai_path: Path, **options: object):
        captured["snapshot"] = Path(system_path).resolve()
        captured["snapshot_root"] = load_system(Path(system_path)).output_root.resolve()
        captured["runner_root"] = Path(options["output_root"]).resolve()
        return _create_fake_run(captured["runner_root"], "D0_mock_configured_root", options["on_created"])

    original_freeze = server._freeze_inputs

    def freeze_then_change_mutable_root(launch_id: str, conditions: dict[str, object]):
        frozen = original_freeze(launch_id, conditions)
        server._runs_root = mutable_decoy
        return frozen

    monkeypatch.setattr(server, "_freeze_inputs", freeze_then_change_mutable_root)
    monkeypatch.setattr("ccs.runner.run", fake_run)
    server.start_run(_payload())
    _wait_for_worker(server)

    assert captured["snapshot"].is_file()
    assert captured["snapshot_root"] == output_root
    assert captured["runner_root"] == output_root
    assert not (server.workspace / "runs").exists()
    expected_run = (output_root / "D0_mock_configured_root").resolve()
    record = server._state["runs"][0]
    assert Path(record["output_root"]) == output_root
    assert Path(record["run_dir"]) == expected_run
    public = server.console_state()["runs"][0]
    assert Path(public["run_dir"]) == expected_run


def test_each_start_freezes_its_root_and_both_roots_survive_restart(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, system_path, output_a, base = _server("per-start-freeze", "output-a")
    output_b = (base / "output-b").resolve()
    first_created = threading.Event()
    release_first = threading.Event()
    calls: list[dict[str, Path]] = []
    run_ids = ["D0_mock_root_a", "D0_mock_root_b"]

    async def fake_run(frozen_system: Path, _ai_path: Path, **options: object):
        index = len(calls)
        root = Path(options["output_root"]).resolve()
        calls.append({"runner_root": root, "snapshot_root": load_system(Path(frozen_system)).output_root.resolve()})
        run_dir = root / run_ids[index]
        run_dir.mkdir()
        (run_dir / "manifest.json").write_text(
            json.dumps({"run_id": run_dir.name, "status": "RUNNING", "episodes": []}), encoding="utf-8"
        )
        callback = options["on_created"]
        assert callable(callback)
        callback(run_dir)
        if index == 0:
            first_created.set()
            await asyncio.to_thread(release_first.wait, 5)
        summary = {"run_id": run_dir.name, "status": "COMPLETED", "integrity_valid": True}
        (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (run_dir / "manifest.json").write_text(
            json.dumps({"run_id": run_dir.name, "status": "COMPLETED", "episodes": []}), encoding="utf-8"
        )
        return run_dir, summary

    monkeypatch.setattr("ccs.runner.run", fake_run)
    server.start_run(_payload())
    assert first_created.wait(5)

    _set_output_root(system_path, output_b)
    active_state = server.console_state()
    assert Path(active_state["options"]["output_root"]) == output_b
    active_record = next(item for item in active_state["runs"] if item["run_id"] == run_ids[0])
    assert Path(active_record["run_dir"]) == (output_a / run_ids[0]).resolve()

    release_first.set()
    _wait_for_worker(server)
    server.start_run(_payload())
    _wait_for_worker(server)

    assert calls == [
        {"runner_root": output_a, "snapshot_root": output_a},
        {"runner_root": output_b, "snapshot_root": output_b},
    ]
    restarted = WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", server.workspace)
    restarted_state = restarted.console_state()
    public = {item["run_id"]: item for item in restarted_state["runs"]}
    assert Path(public[run_ids[0]]["run_dir"]) == (output_a / run_ids[0]).resolve()
    assert Path(public[run_ids[1]]["run_dir"]) == (output_b / run_ids[1]).resolve()
    assert restarted._run_record(run_ids[0])[1] == (output_a / run_ids[0]).resolve()
    assert restarted._run_record(run_ids[1])[1] == (output_b / run_ids[1]).resolve()
    assert restarted.state_for_run(run_ids[0], "")["meta"]["manifest"]["run_id"] == run_ids[0]
    assert restarted.state_for_run(run_ids[1], "")["meta"]["manifest"]["run_id"] == run_ids[1]


def test_legacy_workspace_run_is_preferred_pinned_and_left_untouched() -> None:
    server, system_path, configured_root, _ = _server("legacy-record")
    run_id = "D0_mock_legacy_workspace"
    legacy_dir = server.workspace / "runs" / run_id
    configured_dir = configured_root / run_id
    legacy_dir.mkdir(parents=True)
    configured_dir.mkdir(parents=True)
    (legacy_dir / "manifest.json").write_text(
        json.dumps({"run_id": run_id, "status": "COMPLETED", "episodes": []}), encoding="utf-8"
    )
    (configured_dir / "manifest.json").write_text(
        json.dumps({"run_id": run_id, "status": "ABORTED", "episodes": []}), encoding="utf-8"
    )
    sealed = legacy_dir / "sealed-evidence.json"
    sealed.write_bytes(b'{"preserved":true}')
    evidence_before = (sealed.read_bytes(), sealed.stat().st_mtime_ns)
    server._state["runs"].append({"run_id": run_id, "status": "UNKNOWN", "conditions": _payload()})
    server._save_locked()

    restarted = WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", server.workspace)
    state = restarted.console_state()
    public = next(item for item in state["runs"] if item["run_id"] == run_id)
    assert public["status"] == "COMPLETED"
    assert Path(public["run_dir"]) == legacy_dir.resolve()
    record = next(item for item in restarted._state["runs"] if item["run_id"] == run_id)
    assert Path(record["output_root"]) == (server.workspace / "runs").resolve()
    assert Path(record["run_dir"]) == legacy_dir.resolve()
    persisted = json.loads((server.workspace / "console-state.json").read_text(encoding="utf-8"))
    persisted_record = next(item for item in persisted["runs"] if item["run_id"] == run_id)
    assert Path(persisted_record["run_dir"]) == legacy_dir.resolve()
    assert restarted.state_for_run(run_id, "")["meta"]["manifest"]["status"] == "COMPLETED"
    assert (sealed.read_bytes(), sealed.stat().st_mtime_ns) == evidence_before


def test_client_cannot_supply_output_root() -> None:
    server, _, _, base = _server("client-root")
    with pytest.raises(ValueError, match="unknown run option"):
        server.start_run(_payload(output_root=str(base / "client-selected")))
    assert server._worker is None
    assert server._state["runs"] == []


def test_runner_callback_outside_frozen_root_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    server, _, output_root, base = _server("unsafe-callback")
    outside = base / "outside-root" / "D0_mock_outside"

    async def fake_run(_system_path: Path, _ai_path: Path, **options: object):
        assert Path(options["output_root"]).resolve() == output_root
        outside.mkdir(parents=True)
        (outside / "manifest.json").write_text(
            json.dumps({"run_id": outside.name, "status": "RUNNING", "episodes": []}), encoding="utf-8"
        )
        callback = options["on_created"]
        assert callable(callback)
        callback(outside)
        return outside, {"run_id": outside.name, "status": "COMPLETED"}

    monkeypatch.setattr("ccs.runner.run", fake_run)
    server.start_run(_payload())
    _wait_for_worker(server)

    assert server._state["runs"] == []
    assert server.console_state()["active"]["status"] == "ABORTED"
