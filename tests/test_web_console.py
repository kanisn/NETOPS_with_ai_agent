"""Security, persistence and frozen-input checks for the local web console."""

from __future__ import annotations

import asyncio
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit
import uuid
import xml.etree.ElementTree as ET

import pytest

from tests.support_paths import workspace_for
from ccs.web_console import WebConsoleServer
from ccs.studio_script import SCRIPT


PROJECT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_web_console")


def _working(name: str) -> Path:
    path = WORK / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _write_system_config(workspace: Path, output_root: Path) -> Path:
    path = workspace / "config" / "system.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.parse(PROJECT / "configs/system.xml").getroot()
    paths = root.find("paths")
    assert paths is not None
    paths.set("output_root", str(output_root.resolve()))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def _server(name: str) -> WebConsoleServer:
    workspace = _working(name)
    system_path = _write_system_config(workspace, workspace / "configured-output")
    return WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", workspace)


def _request(server: WebConsoleServer, method: str, path: str, body: object | bytes | None = None, *,
             token: bool = True, origin: bool = True, content_type: str = "application/json",
             headers: dict[str, str] | None = None) -> tuple[int, dict | str]:
    parsed = urlsplit(server.url or "")
    query = parse_qs(parsed.query)
    suffix = ("&" if "?" in path else "?") + urlencode({"token": query["token"][0]}) if token else ""
    request_headers = dict(headers or {})
    if origin:
        request_headers["Origin"] = f"http://{parsed.netloc}"
    if body is not None:
        encoded = body if isinstance(body, bytes) else json.dumps(body).encode()
        request_headers["Content-Type"] = content_type
    else:
        encoded = None
    connection = HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    connection.request(method, path + suffix, body=encoded, headers=request_headers)
    response = connection.getresponse()
    raw = response.read().decode()
    connection.close()
    try:
        value: dict | str = json.loads(raw)
    except json.JSONDecodeError:
        value = raw
    return response.status, value


def _start_payload(**updates: object) -> dict:
    payload = {
        "mode": "mock", "profile": "luna6", "faults": ["W1"], "seeds": [1],
        "repeat": 1, "request": "", "rag_enabled": True, "memory_enabled": True,
        "runbook_k": 3, "memory_k": 3, "delay_seconds": 0, "difficulty": "L1",
        "approval": "auto", "diagnosis_tool_budget": 8, "context_steps": 6,
        "max_agent_steps": 12,
    }
    payload.update(updates)
    return payload


def test_auth_origin_content_limits_and_fixed_routes() -> None:
    server = _server("http-security").start()
    try:
        status, _ = _request(server, "GET", "/api/console", token=False, origin=False)
        assert status == 403

        status, _ = _request(server, "POST", "/api/delay", {"seconds": 1}, origin=False)
        assert status == 403

        status, _ = _request(server, "POST", "/api/delay", {"seconds": 1}, content_type="text/plain")
        assert status == 415

        parsed = urlsplit(server.url or "")
        token = parse_qs(parsed.query)["token"][0]
        connection = HTTPConnection(parsed.hostname, parsed.port, timeout=5)
        connection.request(
            "POST", f"/api/delay?{urlencode({'token': token})}", body=None,
            headers={"Origin": f"http://{parsed.netloc}", "Content-Type": "application/json", "Content-Length": str(2 * 1024 * 1024 + 1)},
        )
        response = connection.getresponse()
        response.read()
        connection.close()
        assert response.status == 413

        status, result = _request(server, "POST", "/api/delay", {"seconds": 1, "extra": True})
        assert status == 400 and result["error"]["type"] == "invalid_request"

        status, _ = _request(server, "POST", "/api/documents/remove", {"kind": "runbooks", "id": "../../configs/ai.local.xml"})
        assert status == 400

        status, _ = _request(server, "GET", "/configs/ai.local.xml", origin=False)
        assert status == 404
        status, _ = _request(server, "GET", "/api/state?run_id=../../configs", origin=False)
        assert status == 404
    finally:
        server.stop()


def test_console_never_exposes_ai_keys_and_serves_same_origin_monitor() -> None:
    server = _server("public-data")
    run_id = "D0_mock_web_test"
    run_dir = server.workspace / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(json.dumps({"run_id": run_id, "status": "COMPLETED", "episodes": []}), encoding="utf-8")
    server._state["runs"].append({"run_id": run_id, "status": "COMPLETED", "conditions": _start_payload()})
    server._save_locked()
    server.start()
    try:
        status, value = _request(server, "GET", "/api/console", origin=False)
        assert status == 200
        rendered = json.dumps(value)
        assert "api_key" not in rendered and "OPENAI_API_KEY" not in rendered
        parsed = urlsplit(server.url or "")
        token = parse_qs(parsed.query)["token"][0]
        connection = HTTPConnection(parsed.hostname, parsed.port, timeout=5)
        connection.request("GET", f"/monitor?{urlencode({'token': token, 'run_id': run_id})}")
        response = connection.getresponse()
        html = response.read().decode()
        connection.close()
        assert response.status == 200
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
        assert "frame-ancestors 'self'" in response.headers["Content-Security-Policy"]
        assert "NetOps Agent Activity Monitor" in html

        status, network = _request(server, "GET", "/api/network?fault=W4&seed=1&difficulty=L1", origin=False)
        assert status == 200 and network["source"] == "preview" and network["available"] is True
        status, network = _request(server, "GET", f"/api/network?run_id={run_id}", origin=False)
        assert status == 200 and network["source"] == "run" and network["available"] is False
        status, _ = _request(server, "GET", f"/api/network?run_id={run_id}&episode_id=../manifest.json", origin=False)
        assert status == 400
        status, _ = _request(server, "GET", "/api/network?fault=F7&seed=1&difficulty=L1", origin=False)
        assert status == 400
    finally:
        server.stop()


def test_terminal_index_overrides_stale_running_manifest_for_console_and_analysis() -> None:
    server = _server("stale-running-manifest")
    run_id = "D0_live_20260930T003540Z_db4cc55b"
    run_dir = Path(server.console_state()["options"]["output_root"]) / run_id
    run_dir.mkdir(parents=True)
    manifest_bytes = json.dumps({"run_id": run_id, "status": "RUNNING", "episodes": []}).encode()
    (run_dir / "manifest.json").write_bytes(manifest_bytes)
    server._state["runs"].append(
        {
            "run_id": run_id,
            "output_root": str(run_dir.parent.resolve()),
            "run_dir": str(run_dir.resolve()),
            "status": "ABORTED",
            "conditions": _start_payload(mode="live"),
        }
    )
    server._save_locked()

    restarted = WebConsoleServer(server.system_path, server.ai_path, server.workspace)
    state = restarted.console_state()
    assert state["runs"][0]["status"] == "ABORTED"
    assert (run_dir / "manifest.json").read_bytes() == manifest_bytes
    assert not (run_dir / "summary.json").exists()

    restarted.start()
    try:
        status, analysis = _request(restarted, "GET", f"/api/analysis?run_id={run_id}", origin=False)
        assert status == 200
        assert analysis["status"] == "ABORTED"
        assert analysis["ready"] is True
        assert analysis["complete"] is False
        assert analysis["sealed"] is False
        assert "partial_terminal_run" in {item["code"] for item in analysis["limitations"]}
        assert "const ANALYSIS_PENDING=new Set(['STARTING','LAUNCHING','RUNNING','STOPPING'])" in SCRIPT
        assert "pending?t('running'):a?.status?statusName(a.status)" in SCRIPT
        assert "analysisSummary(headline)" in SCRIPT
        assert "interrupted:{ko:'" + chr(92) + "uC2E4" in SCRIPT
        assert "interrupted:{ko:'" + chr(92) * 2 + "uC2E4" not in SCRIPT
    finally:
        restarted.stop()


def test_memory_clear_is_soft_and_prior_run_artifacts_are_untouched() -> None:
    server = _server("memory-clear")
    added = server.add_document({"kind": "memory", "title": "Operator note", "content": "Unverified lead only"})
    old_run = server.workspace / "runs" / "D0_mock_preserved"
    old_run.mkdir(parents=True)
    evidence = old_run / "sealed-evidence.json"
    evidence.write_text('{"preserved":true}', encoding="utf-8")

    server.clear_memory({})

    assert server.console_state()["library"]["memory"] == []
    archived = next(item for item in server._state["documents"] if item["id"] == added["id"])
    assert archived["archived_at_utc"] and archived["selected"] is False
    assert evidence.read_text(encoding="utf-8") == '{"preserved":true}'


def test_selection_is_frozen_and_concurrent_start_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    server = _server("frozen-input")
    original = server.console_state()["library"]["runbooks"]
    server.select_document({"kind": "runbooks", "id": original[0]["id"], "selected": False})
    custom = server.add_document({"kind": "runbooks", "title": "Custom runbook", "content": "# Custom\n\n## Check\nUse current evidence."})
    captured: dict[str, object] = {}
    entered = threading.Event()
    release = threading.Event()

    async def fake_run(_system: Path, _ai: Path, **options: object):
        selected = Path(options["runbooks_override"])
        captured["files"] = [path.read_text(encoding="utf-8") for path in selected.glob("*.md")]
        captured["memory"] = options["initial_memory"]
        run_dir = Path(options["output_root"]) / "D0_mock_frozen"
        run_dir.mkdir(parents=True)
        (run_dir / "manifest.json").write_text(json.dumps({"run_id": run_dir.name, "status": "RUNNING", "episodes": []}), encoding="utf-8")
        options["on_created"](run_dir)
        entered.set()
        await asyncio.to_thread(release.wait, 5)
        summary = {"run_id": run_dir.name, "status": "COMPLETED", "integrity_valid": True}
        (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (run_dir / "manifest.json").write_text(json.dumps({"run_id": run_dir.name, "status": "COMPLETED", "episodes": []}), encoding="utf-8")
        return run_dir, summary

    monkeypatch.setattr("ccs.runner.run", fake_run)
    first = server.start_run(_start_payload())
    assert first["status"] == "STARTING"
    assert entered.wait(5)
    with pytest.raises(RuntimeError, match="already active"):
        server.start_run(_start_payload())
    with pytest.raises(RuntimeError, match="locked"):
        server.remove_document({"kind": "runbooks", "id": custom["id"]})
    release.set()
    deadline = time.monotonic() + 5
    while server._worker is not None and time.monotonic() < deadline:
        time.sleep(0.02)
    assert server._worker is None
    files = captured["files"]
    assert isinstance(files, list)
    assert any("operator-" + custom["id"] in content for content in files)
    assert all(original[0]["content"] != content for content in files)
    assert server.console_state()["active"]["status"] == "COMPLETED"


def test_delay_and_options_persist_without_mutating_source_config() -> None:
    workspace = _working("persistence")
    system_path = _write_system_config(workspace, workspace / "configured-output")
    before = system_path.read_bytes()
    source_before = (PROJECT / "configs/system.xml").read_bytes()
    server = WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", workspace)
    assert server.set_delay({"seconds": 1.25}) == 1.25
    server = WebConsoleServer(system_path, PROJECT / "configs/ai.example.xml", workspace)
    state = server.console_state()
    assert state["delay"]["seconds"] == 1.25
    assert state["options"]["defaults"]["delay_seconds"] == 1.25
    assert state["options"]["defaults"]["faults"] == ["W4"]
    assert state["options"]["defaults"]["seeds"] == [1]
    assert state["options"]["faults"] == ["W1", "W2", "W3", "W4", "W5", "N0"]
    assert {"id", "provider", "model"} == set(state["options"]["profiles"][0])
    assert system_path.read_bytes() == before
    assert (PROJECT / "configs/system.xml").read_bytes() == source_before


def test_zero_selected_runbooks_is_a_valid_frozen_condition() -> None:
    server = _server("zero-runbooks")
    for item in server.console_state()["library"]["runbooks"]:
        server.select_document({"kind": "runbooks", "id": item["id"], "selected": False})
    conditions = server._validate_start(_start_payload(rag_enabled=True))
    runbooks, memory, config = server._freeze_inputs("launch-zero-runbooks", conditions)
    assert list(runbooks.glob("*.md")) == []
    assert memory == []
    assert conditions["runbook_count"] == 0 and conditions["runbook_ids"] == []
    assert config.is_file()


def test_stop_releases_force_delay_before_cancelling(monkeypatch: pytest.MonkeyPatch) -> None:
    from ccs.pacing import read_control

    server = _server("stop-delay")
    entered = threading.Event()

    async def waiting_run(_system: Path, _ai: Path, **_options: object):
        entered.set()
        while True:
            await asyncio.sleep(1)

    monkeypatch.setattr("ccs.runner.run", waiting_run)
    server.start_run(_start_payload(delay_seconds=5))
    assert entered.wait(5)
    stopped = server.stop_run({})
    assert stopped["status"] == "STOPPING"
    assert read_control(server._delay_path)["seconds"] == 0
    deadline = time.monotonic() + 5
    while server._worker is not None and time.monotonic() < deadline:
        time.sleep(0.02)
    assert server._worker is None
    assert server.console_state()["active"]["status"] == "CANCELLED"


def test_server_stop_waits_for_cancellation_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    from ccs.pacing import read_control

    server = _server("server-stop-cleanup")
    entered = threading.Event()
    cleanup_finished = threading.Event()

    async def cancellable_run(_system: Path, _ai: Path, **_options: object):
        entered.set()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await asyncio.sleep(0.1)
            cleanup_finished.set()
            raise

    monkeypatch.setattr("ccs.runner.run", cancellable_run)
    server.start_run(_start_payload(delay_seconds=5))
    assert entered.wait(5)

    server.stop()

    assert cleanup_finished.is_set()
    assert read_control(server._delay_path)["seconds"] == 0
    assert server._worker is None
    assert server.console_state()["active"]["status"] == "CANCELLED"


def test_server_stop_reports_worker_cleanup_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import ccs.web_console as web_console

    server = _server("server-stop-timeout")
    entered = threading.Event()
    release_cleanup = threading.Event()

    async def resistant_run(_system: Path, _ai: Path, **_options: object):
        entered.set()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await asyncio.to_thread(release_cleanup.wait, 5)
            raise

    monkeypatch.setattr("ccs.runner.run", resistant_run)
    monkeypatch.setattr(web_console, "_WORKER_STOP_TIMEOUT_SECONDS", 0.05)
    server.start_run(_start_payload(delay_seconds=5))
    assert entered.wait(5)
    worker = server._worker
    assert worker is not None

    with pytest.raises(TimeoutError, match="active run cleanup did not finish"):
        server.stop()

    release_cleanup.set()
    worker.join(timeout=5)
    assert not worker.is_alive()


def test_workspace_symlink_is_rejected() -> None:
    base = _working("symlink")
    target = base / "target"
    target.mkdir()
    link = base / "linked-workspace"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("creating a directory symlink is unavailable on this host")
    with pytest.raises(ValueError, match="symbolic-link"):
        WebConsoleServer(PROJECT / "configs/system.xml", PROJECT / "configs/ai.example.xml", link)
