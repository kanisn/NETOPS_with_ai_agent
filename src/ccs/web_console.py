"""Authenticated local experiment controller used by the browser console.

The controller owns mutable operator state outside immutable run artifacts. It
serves loopback by default and can bind one explicitly allowlisted IPv4 LAN
address. Requests use a per-process capability token; LAN requests also pass
peer, Host, and same-Origin checks. Library input is frozen before each run and
those snapshots are passed to :mod:`ccs.runner`.
"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import errno
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
from functools import partial
from typing import Any, Callable
from urllib.parse import parse_qs, quote, urlsplit
import uuid
import xml.etree.ElementTree as ET

from ccs.config import load_ai, load_system
from ccs.scenario_catalog import CATALOG_ID, SCENARIOS
from ccs.knowledge.stores import runbook_files
from ccs.monitor import _decode_cursor, _document as monitor_document, _encode_cursor, _metadata, _read_incremental


_MAX_BODY = 2 * 1024 * 1024
_MAX_TITLE = 240
_MAX_CONTENT = 1_500_000
_WORKER_STOP_TIMEOUT_SECONDS = 30.0
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,159}$")
_EPISODE_ID = re.compile(r"^episode-[0-9]{4,8}$")
_DOC_ID = re.compile(r"^[a-f0-9]{32}$")
_KINDS = {"runbooks", "memory"}
_FAULTS = {"W1", "W2", "W3", "W4", "W5", "N0"}
_ACTIVE_RUN_STATUSES = {"STARTING", "LAUNCHING", "RUNNING", "STOPPING"}
_TERMINAL_RUN_STATUSES = {
    "COMPLETED", "FAILED", "ABORTED", "CANCELLED", "CANCELED",
    "INVALID_ARTIFACT", "INTERRUPTED",
}


class WebConsoleBindError(RuntimeError):
    """A failure to bind the web console listener, with no OS detail exposed."""

    def __init__(self, host: str, port: int, error: OSError):
        self.host = host
        self.port = port
        self.errno = error.errno
        self.winerror = getattr(error, "winerror", None)
        code = self.winerror if self.winerror is not None else self.errno
        if code in {10048, errno.EADDRINUSE, 98, 48}:
            self.reason = "address already in use"
        elif self.winerror == 10013:
            self.reason = "binding denied; the port may already be in use or reserved"
        elif code in {10013, errno.EACCES, errno.EPERM}:
            self.reason = "permission denied"
        else:
            self.reason = "socket bind failed"
        detail = f" (socket error {code})" if isinstance(code, int) else ""
        super().__init__(f"{self.reason} for {host}:{port}{detail}")
_CATALOG = CATALOG_ID
_START_FIELDS = {
    "mode", "profile", "faults", "seeds", "repeat", "request", "rag_enabled",
    "memory_enabled", "runbook_k", "memory_k", "delay_seconds", "difficulty",
    "approval", "diagnosis_tool_budget", "context_steps", "max_agent_steps",
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writing = path.with_name(path.name + ".writing")
    writing.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    os.replace(writing, path)


def _read_object(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return deepcopy(default)
    return value if isinstance(value, dict) else deepcopy(default)


def _within(path: Path, parent: Path) -> bool:
    try:
        return path.resolve().is_relative_to(parent.resolve())
    except (OSError, RuntimeError):
        return False


def _safe_existing_file(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    return path.resolve()


def _safe_directory(path: Path, parent: Path | None = None) -> Path:
    if path.is_symlink():
        raise ValueError("symbolic-link workspaces are not supported")
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve()
    if parent is not None and not resolved.is_relative_to(parent.resolve()):
        raise ValueError("workspace path escaped its configured root")
    if not path.is_dir():
        raise ValueError("workspace path must be a directory")
    return resolved


def _safe_text(value: Any, field: str, *, limit: int, empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    value = value.replace("\x00", "").strip()
    if (not empty and not value) or len(value.encode("utf-8")) > limit:
        raise ValueError(f"{field} is empty or too large")
    return value


def _bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be true or false")
    return value


def _int(value: Any, field: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{field} must be an integer from {low} to {high}")
    return value


def _delay(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("seconds must be a finite number from 0 to 30")
    result = float(value)
    if not math.isfinite(result) or not 0 <= result <= 30:
        raise ValueError("seconds must be a finite number from 0 to 30")
    return result


def _write_delay(path: Path, seconds: float) -> None:
    from ccs.pacing import write_control

    write_control(path, seconds)


def _read_delay(path: Path) -> float:
    from ccs.pacing import read_control

    return float(read_control(path)["seconds"])


def _front_matter(content: str, doc_id: str) -> str:
    stripped = content.lstrip("\ufeff\r\n ")
    if stripped.startswith("---\n") or stripped.startswith("---\r\n"):
        return stripped
    return (
        "---\n"
        f"doc_id: operator-{doc_id}\n"
        "version: 1\n"
        "tenant: synthetic-tenant\n"
        "classification: internal\n"
        "source: operator-import\n"
        "---\n\n"
        + stripped
    )


def _title_from_markdown(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()[:_MAX_TITLE]
    return fallback


class _ConsoleHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class WebConsoleServer:
    """Serve and execute the local CCS experiment console.

    ``workspace`` stores the mutable library, conditions and delay control.
    Run artifacts follow system.xml output_root, frozen separately for each run.
    """

    def __init__(self, system_path: str | Path, ai_path: str | Path, workspace: Path, port: int = 0,
                 *, host: str = "127.0.0.1", allowed_networks: tuple[str, ...] = ()):
        self.system_path = _safe_existing_file(Path(system_path), "system_path")
        self.ai_path = _safe_existing_file(Path(ai_path), "ai_path")
        if not isinstance(workspace, Path):
            raise TypeError("workspace must be pathlib.Path")
        if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535:
            raise ValueError("port must be an integer from 0 to 65535")
        address = ipaddress.IPv4Address(host)
        if address.is_unspecified or address.is_multicast or address.is_link_local:
            raise ValueError("host must be a specific usable IPv4 address")
        self.host = str(address)
        self.allowed_networks = tuple(ipaddress.IPv4Network(value, strict=True) for value in allowed_networks)
        if not address.is_loopback and not self.allowed_networks:
            raise ValueError("LAN access requires an explicit allowed client network")
        if any(network.prefixlen < 24 for network in self.allowed_networks):
            raise ValueError("allowed client networks must be /24 or narrower")
        self.workspace = _safe_directory(workspace)
        self.port = port
        self._token = secrets.token_urlsafe(32)
        self._lock = threading.RLock()
        self._server: _ConsoleHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._worker: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._run_task: asyncio.Task[Any] | None = None
        self._cancel_requested = False
        self.url: str | None = None
        self._state_path = self.workspace / "console-state.json"
        self._config_path = self.workspace / "console-config.json"
        self._delay_path = self.workspace / "runtime" / "delay-control.json"
        self._runs_root = load_system(self.system_path).output_root.resolve()
        self._legacy_runs_root = self.workspace / "runs"
        self._runtime_root = _safe_directory(self.workspace / "runtime", self.workspace)
        self._library_root = _safe_directory(self.workspace / "library", self.workspace)
        if any(path.is_symlink() for path in (self._state_path, self._config_path, self._delay_path)):
            raise ValueError("symbolic-link workspace files are not supported")
        self._state = _read_object(self._state_path, {"version": 2, "catalog": _CATALOG, "documents": [], "runs": [], "active": None})
        self._config = _read_object(self._config_path, {"version": 1, "delay_seconds": 0.0})
        self._migrate_catalog()
        self._normalize_persistent_state()
        self._initialize_runbooks()
        if not self._delay_path.exists():
            _write_delay(self._delay_path, _delay(self._config.get("delay_seconds", 0.0)))

    def _migrate_catalog(self) -> None:
        """Start a clean wired library/index while retaining legacy evidence."""
        if self._state.get("catalog") == _CATALOG:
            return
        archive_root = _safe_directory(self.workspace / "archive", self.workspace)
        archive = archive_root / ("previous-catalog-" + uuid.uuid4().hex + ".json")
        _atomic_json(archive, self._state)
        self._state = {"version": 2, "catalog": _CATALOG, "documents": [], "runs": [], "active": None,
                       "previous_catalog_archive": str(archive)}

    def _normalize_persistent_state(self) -> None:
        documents = self._state.get("documents")
        runs = self._state.get("runs")
        if not isinstance(documents, list) or not isinstance(runs, list):
            raise ValueError("workspace state has an invalid shape")
        for entry in runs:
            if not isinstance(entry, dict):
                continue
            try:
                self._record_path(entry)
            except (KeyError, OSError, ValueError, RuntimeError):
                pass  # Preserve unavailable history entries without guessing a new location.
            if str(entry.get("status", "")).upper() in _ACTIVE_RUN_STATUSES:
                entry["status"] = "INTERRUPTED"
                entry["finished_at_utc"] = entry.get("finished_at_utc") or _utc()
        self._state["active"] = None
        seconds = _delay(self._config.get("delay_seconds", 0.0))
        self._config = {"version": 1, "delay_seconds": seconds}
        self._save_locked()

    def _save_locked(self) -> None:
        _atomic_json(self._state_path, self._state)
        _atomic_json(self._config_path, self._config)

    def _initialize_runbooks(self) -> None:
        system = load_system(self.system_path)
        source = system.runbooks
        if source.is_symlink() or not source.is_dir():
            raise ValueError("configured runbook catalog must be a regular directory")
        with self._lock:
            if any(isinstance(item, dict) and item.get("kind") == "runbooks" for item in self._state["documents"]):
                return
            for path in runbook_files(source):
                if path.is_symlink() or not _within(path, source):
                    raise ValueError("configured runbook catalog contains an unsafe path")
                content = path.read_text(encoding="utf-8")
                identifier = uuid.uuid5(uuid.NAMESPACE_URL, f"ccs-runbook:{path.relative_to(source).as_posix()}").hex
                self._state["documents"].append(
                    {
                        "id": identifier,
                        "kind": "runbooks",
                        "title": _title_from_markdown(content, path.stem),
                        "content": content,
                        "selected": True,
                        "source_kind": "configured_catalog",
                        "source_name": path.name,
                        "created_at_utc": _utc(),
                        "archived_at_utc": None,
                    }
                )
            self._save_locked()

    def start(self) -> "WebConsoleServer":
        with self._lock:
            if self._server is not None:
                return self
            handler = partial(_ConsoleHandler, console=self)
            try:
                server = _ConsoleHTTPServer((self.host, self.port), handler)
            except OSError as exc:
                raise WebConsoleBindError(self.host, self.port, exc) from None
            self._server = server
            actual_port = int(server.server_address[1])
            self.url = f"http://{self.host}:{actual_port}/?token={quote(self._token)}"
            self._thread = threading.Thread(target=server.serve_forever, name="ccs-web-console", daemon=True)
            self._thread.start()
        return self

    def stop(self) -> None:
        with self._lock:
            worker = self._worker
            if worker is not None and worker.is_alive():
                _write_delay(self._delay_path, 0.0)
                if self._loop is not None and self._run_task is not None:
                    self._loop.call_soon_threadsafe(self._run_task.cancel)
                else:
                    self._cancel_requested = True
            server, thread = self._server, self._thread
            self._server = None
            self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=3)
        if worker is not None and worker is not threading.current_thread() and worker.is_alive():
            worker.join(timeout=_WORKER_STOP_TIMEOUT_SECONDS)
            if worker.is_alive():
                raise TimeoutError(
                    f"active run cleanup did not finish within {_WORKER_STOP_TIMEOUT_SECONDS:g} seconds"
                )

    def __enter__(self) -> "WebConsoleServer":
        return self.start()

    def __exit__(self, *_: object) -> None:
        self.stop()

    def _documents(self, kind: str) -> list[dict[str, Any]]:
        return [
            {key: item[key] for key in ("id", "title", "content", "selected", "source_kind", "source_run_id") if key in item}
            for item in self._state["documents"]
            if isinstance(item, dict) and item.get("kind") == kind and not item.get("archived_at_utc")
        ]

    def _find_document(self, kind: str, identifier: str) -> dict[str, Any]:
        if kind not in _KINDS or not isinstance(identifier, str) or not _DOC_ID.fullmatch(identifier):
            raise ValueError("invalid document identifier")
        for item in self._state["documents"]:
            if item.get("kind") == kind and item.get("id") == identifier and not item.get("archived_at_utc"):
                return item
        raise KeyError(identifier)

    def _assert_library_unlocked(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            raise RuntimeError("library changes are locked while a run is active")

    def add_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != {"kind", "title", "content"}:
            raise ValueError("unknown or missing document fields")
        kind = payload["kind"]
        if kind not in _KINDS:
            raise ValueError("kind must be runbooks or memory")
        title = _safe_text(payload["title"], "title", limit=_MAX_TITLE)
        content = _safe_text(payload["content"], "content", limit=_MAX_CONTENT)
        identifier = uuid.uuid4().hex
        if kind == "runbooks":
            content = _front_matter(content, identifier)
        with self._lock:
            self._assert_library_unlocked()
            item = {
                "id": identifier,
                "kind": kind,
                "title": title,
                "content": content,
                "selected": True,
                "source_kind": "operator_import",
                "created_at_utc": _utc(),
                "archived_at_utc": None,
            }
            self._state["documents"].append(item)
            self._save_locked()
            return {key: item[key] for key in ("id", "title", "content", "selected", "source_kind")}

    def select_document(self, payload: dict[str, Any]) -> None:
        if set(payload) != {"kind", "id", "selected"}:
            raise ValueError("unknown or missing selection fields")
        selected = _bool(payload["selected"], "selected")
        with self._lock:
            self._assert_library_unlocked()
            self._find_document(payload["kind"], payload["id"])["selected"] = selected
            self._save_locked()

    def edit_document(self, payload: dict[str, Any]) -> None:
        if not {"kind", "id"} <= set(payload) or set(payload) - {"kind", "id", "title", "content"} or len(payload) < 3:
            raise ValueError("unknown or missing edit fields")
        with self._lock:
            self._assert_library_unlocked()
            item = self._find_document(payload["kind"], payload["id"])
            if "title" in payload:
                item["title"] = _safe_text(payload["title"], "title", limit=_MAX_TITLE)
            if "content" in payload:
                content = _safe_text(payload["content"], "content", limit=_MAX_CONTENT)
                item["content"] = _front_matter(content, item["id"]) if item["kind"] == "runbooks" else content
            item["updated_at_utc"] = _utc()
            self._save_locked()

    def remove_document(self, payload: dict[str, Any]) -> None:
        if set(payload) != {"kind", "id"}:
            raise ValueError("unknown or missing removal fields")
        with self._lock:
            self._assert_library_unlocked()
            item = self._find_document(payload["kind"], payload["id"])
            item["selected"] = False
            item["archived_at_utc"] = _utc()
            self._save_locked()

    def clear_memory(self, payload: dict[str, Any]) -> None:
        if payload:
            raise ValueError("memory clear accepts an empty object")
        with self._lock:
            self._assert_library_unlocked()
            now = _utc()
            for item in self._state["documents"]:
                if item.get("kind") == "memory" and not item.get("archived_at_utc"):
                    item["selected"] = False
                    item["archived_at_utc"] = now
            self._save_locked()

    def set_delay(self, payload: dict[str, Any]) -> float:
        if set(payload) != {"seconds"}:
            raise ValueError("delay accepts only seconds")
        seconds = _delay(payload["seconds"])
        with self._lock:
            _write_delay(self._delay_path, seconds)
            self._config["delay_seconds"] = seconds
            self._config["delay_updated_at_utc"] = _utc()
            self._save_locked()
        return seconds

    def _validate_start(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) - _START_FIELDS:
            raise ValueError("unknown run option")
        required = _START_FIELDS - {"diagnosis_tool_budget", "context_steps", "max_agent_steps"}
        if not required <= set(payload):
            raise ValueError("missing run option")
        system = load_system(self.system_path)
        ai = load_ai(self.ai_path)
        mode = payload["mode"]
        if mode not in {"mock", "live"}:
            raise ValueError("mode must be mock or live")
        profile = payload["profile"]
        if not isinstance(profile, str) or profile not in ai.profiles:
            raise ValueError("unknown profile")
        faults = payload["faults"]
        if not isinstance(faults, list) or not faults or len(faults) > len(_FAULTS) or any(x not in _FAULTS for x in faults) or len(set(faults)) != len(faults):
            raise ValueError("faults must be a unique non-empty supported list")
        if not set(faults) <= set(system.faults):
            raise ValueError("fault is disabled by the configured system")
        seeds = payload["seeds"]
        if not isinstance(seeds, list) or not seeds or len(seeds) > 100:
            raise ValueError("seeds must be a non-empty list")
        seeds = [_int(value, "seed", 0, 2**31 - 1) for value in seeds]
        if len(set(seeds)) != len(seeds):
            raise ValueError("seeds must be unique")
        difficulty = payload["difficulty"]
        if difficulty not in {"L1", "L2", "L3"}:
            raise ValueError("difficulty must be L1, L2 or L3")
        approval = payload["approval"]
        if approval not in {"auto", "deny"}:
            raise ValueError("approval must be auto or deny")
        result = {
            "mode": mode,
            "profile": profile,
            "faults": list(faults),
            "seeds": seeds,
            "repeat": _int(payload["repeat"], "repeat", 1, 20),
            "request": _safe_text(payload["request"], "request", limit=60_000, empty=True),
            "rag_enabled": _bool(payload["rag_enabled"], "rag_enabled"),
            "memory_enabled": _bool(payload["memory_enabled"], "memory_enabled"),
            "runbook_k": _int(payload["runbook_k"], "runbook_k", 1, 50),
            "memory_k": _int(payload["memory_k"], "memory_k", 1, 50),
            "delay_seconds": _delay(payload["delay_seconds"]),
            "difficulty": difficulty,
            "approval": approval,
            "diagnosis_tool_budget": _int(payload.get("diagnosis_tool_budget", system.diagnosis_tool_budget), "diagnosis_tool_budget", 1, 100),
            "context_steps": _int(payload.get("context_steps", system.context_steps), "context_steps", 1, 100),
            "max_agent_steps": _int(payload.get("max_agent_steps", system.max_agent_steps), "max_agent_steps", 1, 100),
        }
        if mode == "live":
            provider = ai.profiles[profile].provider
            if not ai.keys.get(provider):
                raise ValueError("selected live profile has no configured API key")
        return result

    def _freeze_inputs(self, launch_id: str, conditions: dict[str, Any]) -> tuple[Path, list[dict[str, Any]], Path]:
        snapshot = _safe_directory(self._runtime_root / "snapshots" / launch_id, self._runtime_root)
        runbooks = _safe_directory(snapshot / "runbooks", snapshot)
        selected_runbooks = [item for item in self._state["documents"] if item.get("kind") == "runbooks" and item.get("selected") and not item.get("archived_at_utc")]
        for index, item in enumerate(selected_runbooks, start=1):
            (runbooks / f"runbook-{index:04d}-{item['id']}.md").write_text(item["content"], encoding="utf-8")
        memory = [
            {key: item[key] for key in ("id", "title", "content", "source_kind", "source_run_id") if key in item}
            for item in self._state["documents"]
            if item.get("kind") == "memory" and item.get("selected") and not item.get("archived_at_utc")
        ]
        conditions["runbook_count"] = len(selected_runbooks)
        conditions["runbook_ids"] = [item["id"] for item in selected_runbooks]
        conditions["memory_count"] = len(memory)
        conditions["memory_ids"] = [item["id"] for item in memory]
        frozen = {
            "launch_id": launch_id,
            "created_at_utc": _utc(),
            "conditions": conditions,
            "runbooks": [{"id": x["id"], "title": x["title"], "source_kind": x["source_kind"]} for x in selected_runbooks],
            "memory": memory,
        }
        _atomic_json(snapshot / "inputs.json", frozen)
        config_path = self._write_system_snapshot(snapshot, conditions, runbooks)
        return runbooks, memory, config_path

    def _write_system_snapshot(self, snapshot: Path, conditions: dict[str, Any], runbooks: Path) -> Path:
        root = ET.parse(self.system_path).getroot()
        paths = root.find("paths")
        workflow = root.find("workflow")
        experiment = root.find("experiment")
        if paths is None or workflow is None or experiment is None:
            raise ValueError("system configuration is missing required sections")
        paths.set("runbooks", str(runbooks))
        workflow.set("approval", conditions["approval"])
        workflow.set("memory_enabled", "true" if conditions["memory_enabled"] else "false")
        workflow.set("memory_k", str(conditions["memory_k"]))
        workflow.set("runbook_k", str(conditions["runbook_k"]))
        workflow.set("diagnosis_tool_budget", str(conditions["diagnosis_tool_budget"]))
        workflow.set("operation_context_steps", str(conditions["context_steps"]))
        workflow.set("max_agent_steps", str(conditions["max_agent_steps"]))
        experiment.set("seeds", ",".join(str(x) for x in conditions["seeds"]))
        experiment.set("faults", ",".join(conditions["faults"]))
        experiment.set("difficulty", conditions["difficulty"])
        destination = snapshot / "system.xml"
        ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
        # Resolve from this exact XML snapshot using the same rules as the CLI.
        # Later edits to system.xml must not redirect an already-started run.
        output_root = _safe_directory(load_system(destination).output_root)
        paths.set("output_root", str(output_root))
        ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
        self._runs_root = output_root
        return destination

    def start_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        conditions = self._validate_start(payload)
        with self._lock:
            if self._worker is not None and self._worker.is_alive():
                raise RuntimeError("one run is already active")
            launch_id = "launch-" + uuid.uuid4().hex
            runbooks, memory, config_path = self._freeze_inputs(launch_id, conditions)
            _write_delay(self._delay_path, conditions["delay_seconds"])
            self._config["delay_seconds"] = conditions["delay_seconds"]
            active = {"run_id": launch_id, "status": "STARTING"}
            self._state["active"] = active
            self._cancel_requested = False
            self._save_locked()
            worker = threading.Thread(
                target=self._run_worker,
                args=(launch_id, conditions, runbooks, memory, config_path),
                name=f"ccs-run-{launch_id[-8:]}",
                daemon=True,
            )
            self._worker = worker
            worker.start()
            return deepcopy(active)

    def _run_worker(self, launch_id: str, conditions: dict[str, Any], runbooks: Path, memory: list[dict[str, Any]], config_path: Path) -> None:
        run_dir: Path | None = None
        output_root: Path | None = None

        def on_created(created: Path) -> None:
            nonlocal run_dir
            created_raw = Path(created)
            if created_raw.is_symlink():
                raise RuntimeError("runner returned an unsafe run directory")
            created = created_raw.resolve()
            if output_root is None or not created.parent.samefile(output_root) or not _RUN_ID.fullmatch(created.name):
                raise RuntimeError("runner returned an unsafe run directory")
            run_dir = created
            record = {
                "run_id": created.name,
                "output_root": str(output_root),
                "run_dir": str(created),
                "launch_id": launch_id,
                "status": "RUNNING",
                "conditions": deepcopy(conditions),
                "started_at_utc": _utc(),
            }
            with self._lock:
                self._state["runs"].append(record)
                self._state["active"] = {"run_id": created.name, "status": "RUNNING"}
                self._save_locked()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with self._lock:
            self._loop = loop
        try:
            from ccs.runner import run

            output_root = load_system(config_path).output_root.resolve()

            task = loop.create_task(
                run(
                    config_path,
                    self.ai_path,
                    mode=conditions["mode"],
                    faults=conditions["faults"],
                    seeds=conditions["seeds"],
                    repeat=conditions["repeat"],
                    profile_override=conditions["profile"],
                    memory_off=not conditions["memory_enabled"],
                    output_root=output_root,
                    request_override=conditions["request"] or None,
                    on_created=on_created,
                    runbooks_override=runbooks,
                    initial_memory=memory,
                    rag_enabled=conditions["rag_enabled"],
                    delay_control_path=self._delay_path,
                    experiment_metadata={"web_console": {"conditions": conditions}},
                )
            )
            with self._lock:
                self._run_task = task
                cancel_requested = self._cancel_requested
            if cancel_requested:
                loop.call_soon(task.cancel)
            completed_dir, summary = loop.run_until_complete(task)
            run_dir = Path(completed_dir).resolve()
            if summary.get("integrity_valid") is True:
                self._import_generated_memory(run_dir)
            self._finish_run(run_dir, str(summary.get("status", "COMPLETED")).upper(), summary=summary)
        except asyncio.CancelledError:
            self._finish_run(run_dir, "CANCELLED")
        except BaseException as exc:
            self._finish_run(run_dir, "ABORTED", error_type=type(exc).__name__)
        finally:
            with self._lock:
                self._run_task = None
                self._loop = None
                self._worker = None
                self._cancel_requested = False
                self._save_locked()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    def _finish_run(self, run_dir: Path | None, status: str, *, summary: dict[str, Any] | None = None, error_type: str | None = None) -> None:
        with self._lock:
            run_id = run_dir.name if run_dir is not None else str((self._state.get("active") or {}).get("run_id", "unknown"))
            record = next((x for x in reversed(self._state["runs"]) if x.get("run_id") == run_id), None)
            if record is not None:
                record["status"] = status
                record["finished_at_utc"] = _utc()
                if isinstance(summary, dict):
                    record["summary"] = self._public_summary(summary)
                if error_type:
                    record["error"] = {"type": error_type, "message": "Run failed; inspect the run activity log."}
            active: dict[str, Any] = {"run_id": run_id, "status": status}
            if error_type:
                active["error"] = {"type": error_type, "message": "Run failed; inspect the run activity log."}
            self._state["active"] = active
            self._save_locked()

    @staticmethod
    def _public_summary(summary: dict[str, Any]) -> dict[str, Any]:
        allowed = {
            "run_id", "status", "episodes", "completed_episodes", "successful_episodes",
            "diagnoses_correct", "api_calls", "input_tokens", "output_tokens",
            "estimated_cost_usd", "integrity_valid", "mode", "models", "limitations",
            "timing", "elapsed_seconds", "artificial_delay_seconds", "delay_adjusted_estimate_seconds",
            "input_conditions",
        }
        return {key: summary[key] for key in allowed if key in summary}

    def _import_generated_memory(self, run_dir: Path) -> None:
        database = run_dir / "memory.sqlite"
        if database.is_symlink() or not database.is_file() or not _within(database, run_dir):
            return
        try:
            connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT record_id, purpose, verified_outcome, payload_json, items_json FROM memory_records ORDER BY written_at, record_id"
            ).fetchall()
        except sqlite3.Error:
            return
        finally:
            if "connection" in locals():
                connection.close()
        with self._lock:
            known = {(x.get("source_run_id"), x.get("source_record_id")) for x in self._state["documents"]}
            for row in rows:
                if str(row["verified_outcome"]).strip().casefold() != "verified" or (run_dir.name, row["record_id"]) in known:
                    continue
                try:
                    payload = json.loads(row["payload_json"])
                    items = json.loads(row["items_json"])
                except json.JSONDecodeError:
                    continue
                content = json.dumps(
                    {"purpose": row["purpose"], "verified_outcome": row["verified_outcome"], "payload": payload, "items": items},
                    ensure_ascii=False,
                    indent=2,
                )
                self._state["documents"].append(
                    {
                        "id": uuid.uuid4().hex,
                        "kind": "memory",
                        "title": f"Verified incident: {row['purpose']}",
                        "content": content,
                        "selected": True,
                        "source_kind": "verified_run_memory",
                        "source_run_id": run_dir.name,
                        "source_record_id": row["record_id"],
                        "created_at_utc": _utc(),
                        "archived_at_utc": None,
                    }
                )
            self._save_locked()

    def stop_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload:
            raise ValueError("run stop accepts an empty object")
        with self._lock:
            if self._worker is None or not self._worker.is_alive():
                raise RuntimeError("no run is active")
            active = dict(self._state.get("active") or {})
            active["status"] = "STOPPING"
            self._state["active"] = active
            self._save_locked()
            _write_delay(self._delay_path, 0.0)
            if self._loop is not None and self._run_task is not None:
                self._loop.call_soon_threadsafe(self._run_task.cancel)
            else:
                self._cancel_requested = True
            return active

    def _record_path(self, record: dict[str, Any]) -> Path:
        """Resolve only an indexed run; pin legacy locations without moving files."""
        run_id = record.get("run_id")
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            raise KeyError(run_id)
        stored_root = record.get("output_root")
        if stored_root is not None:
            if not isinstance(stored_root, str) or not Path(stored_root).is_absolute():
                raise KeyError(run_id)
            candidates = [Path(stored_root)]
        else:
            candidates = [self._legacy_runs_root, self._runs_root]
        for root in candidates:
            path = root / run_id
            if root.is_symlink() or path.is_symlink() or not path.is_dir():
                continue
            resolved_root, resolved_path = root.resolve(), path.resolve()
            if resolved_path.parent != resolved_root:
                continue
            if root == self._legacy_runs_root and not _within(root, self.workspace):
                continue
            stored_path = record.get("run_dir")
            if stored_path is not None and (
                not isinstance(stored_path, str) or Path(stored_path).resolve() != resolved_path
            ):
                raise KeyError(run_id)
            record["output_root"] = str(resolved_root)
            record["run_dir"] = str(resolved_path)
            return resolved_path
        raise KeyError(run_id)

    def _run_record(self, run_id: str) -> tuple[dict[str, Any], Path]:
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            raise KeyError(run_id)
        with self._lock:
            record = next((x for x in self._state["runs"] if x.get("run_id") == run_id), None)
            if record is None:
                raise KeyError(run_id)
            return record, self._record_path(record)

    def state_for_run(self, run_id: str, cursor: str) -> dict[str, Any]:
        _, path = self._run_record(run_id)
        events, offsets = _read_incremental(path, _decode_cursor(cursor))
        return {"events": events, "cursor": _encode_cursor(offsets), "meta": _metadata(path)}

    def network_state(self, query: dict[str, list[str]]) -> dict[str, Any]:
        from ccs.network_view import preview_network, read_network

        run_id = query.get("run_id", [""])[0]
        if run_id:
            if set(query) - {"token", "run_id", "episode_id"}:
                raise ValueError("unknown network query option")
            episode_id = query.get("episode_id", [""])[0] or None
            if episode_id is not None and not _EPISODE_ID.fullmatch(episode_id):
                raise ValueError("invalid episode identifier")
            _, run_dir = self._run_record(run_id)
            return read_network(run_dir, episode_id=episode_id)
        if set(query) != {"token", "fault", "seed", "difficulty"}:
            raise ValueError("preview requires fault, seed and difficulty")
        system = load_system(self.system_path)
        fault = query["fault"][0]
        if fault not in _FAULTS or fault not in system.faults:
            raise ValueError("unsupported fault")
        try:
            seed = int(query["seed"][0])
        except (TypeError, ValueError):
            raise ValueError("seed must be an integer") from None
        _int(seed, "seed", 0, 2**31 - 1)
        difficulty = query["difficulty"][0]
        if difficulty not in {"L1", "L2", "L3"}:
            raise ValueError("difficulty must be L1, L2 or L3")
        return preview_network(self.workspace, fault=fault, seed=seed, difficulty=difficulty, target=system.target)

    def analysis_state(self, query: dict[str, list[str]]) -> dict[str, Any]:
        """Return the read-only analysis for one controller-indexed run."""

        if set(query) != {"token", "run_id"} or len(query.get("run_id", [])) != 1:
            raise ValueError("analysis requires exactly one run_id")
        run_id = query["run_id"][0]
        record, run_dir = self._run_record(run_id)
        with self._lock:
            controller_record = deepcopy(record)
            active = deepcopy(self._state.get("active")) or {}
            controller_status: str | None = None
            if active.get("run_id") == run_id:
                controller_status = str(active.get("status", "UNKNOWN")).upper()
                # The runner writes a terminal manifest before report rendering,
                # monitor snapshot generation and sealing finish.  Keep analysis
                # unready throughout that worker-owned interval.
                if self._worker is not None and self._worker.is_alive():
                    controller_status = "RUNNING"
            else:
                indexed_status = str(controller_record.get("status", "")).upper()
                if indexed_status in _TERMINAL_RUN_STATUSES:
                    controller_status = indexed_status
        from ccs.run_analysis import analyze_run

        return analyze_run(
            run_dir,
            controller_status=controller_status,
            controller_record=controller_record,
        )

    def _refresh_runs(self) -> None:
        for record in self._state["runs"]:
            try:
                path = self._record_path(record)
            except (KeyError, OSError, ValueError, RuntimeError):
                continue
            manifest = _read_object(path / "manifest.json", {})
            summary = _read_object(path / "summary.json", {})
            manifest_status = str(manifest.get("status", "")).upper()
            indexed_status = str(record.get("status", "")).upper()
            if manifest_status and not (
                manifest_status in _ACTIVE_RUN_STATUSES
                and indexed_status in _TERMINAL_RUN_STATUSES
            ):
                record["status"] = manifest_status
            if manifest.get("started_at_utc"):
                record["started_at_utc"] = manifest["started_at_utc"]
            if manifest.get("finished_at_utc"):
                record["finished_at_utc"] = manifest["finished_at_utc"]
            if summary:
                record["summary"] = self._public_summary(summary)

    def console_state(self) -> dict[str, Any]:
        system = load_system(self.system_path)
        ai = load_ai(self.ai_path)
        with self._lock:
            self._refresh_runs()
            defaults = {
                "mode": "mock",
                "profile": ai.active_profile,
                "faults": ["W4"] if "W4" in system.faults else [system.faults[0]],
                "seeds": [system.seeds[0]],
                "repeat": 1,
                "request": "",
                "rag_enabled": True,
                "memory_enabled": system.memory_enabled,
                "runbook_k": system.runbook_k,
                "memory_k": system.memory_k,
                "delay_seconds": float(self._config["delay_seconds"]),
                "difficulty": system.difficulty,
                "approval": system.approval if system.approval in {"auto", "deny"} else "deny",
                "diagnosis_tool_budget": system.diagnosis_tool_budget,
                "context_steps": system.context_steps,
                "max_agent_steps": system.max_agent_steps,
            }
            runs = []
            for item in reversed(self._state["runs"]):
                public = {key: deepcopy(item[key]) for key in ("run_id", "run_dir", "output_root", "status", "summary", "conditions", "started_at_utc", "finished_at_utc", "error") if key in item}
                runs.append(public)
            active = deepcopy(self._state.get("active")) or {"run_id": None, "status": "IDLE"}
            try:
                seconds = _read_delay(self._delay_path)
            except (OSError, ValueError, json.JSONDecodeError):
                seconds = float(self._config["delay_seconds"])
            return {
                "options": {
                    "scenario_catalog": _CATALOG,
                    "scenarios": deepcopy(SCENARIOS),
                    "output_root": str(system.output_root.resolve()),
                    "profiles": [{"id": profile.id, "provider": profile.provider, "model": profile.model} for profile in ai.profiles.values()],
                    "faults": list(system.faults),
                    "seeds": list(system.seeds),
                    "defaults": defaults,
                },
                "library": {"runbooks": self._documents("runbooks"), "memory": self._documents("memory")},
                "runs": runs,
                "active": active,
                "delay": {"seconds": seconds, "updated_at_utc": self._config.get("delay_updated_at_utc")},
            }


class _ConsoleHandler(BaseHTTPRequestHandler):
    server_version = "CCSWebConsole/1"

    def __init__(self, *args: Any, console: WebConsoleServer, **kwargs: Any):
        self.console = console
        super().__init__(*args, **kwargs)

    def log_message(self, _format: str, *args: Any) -> None:
        return

    def _headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src data:; frame-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'self'",
        )

    def _send(self, status: HTTPStatus, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self._headers(content_type, len(body))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: HTTPStatus, value: Any) -> None:
        self._send(status, json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8"), "application/json; charset=utf-8")

    def _error(self, status: HTTPStatus, error_type: str, message: str) -> None:
        self._json(status, {"error": {"type": error_type[:80], "message": message[:300]}})

    def _parsed(self) -> tuple[Any, dict[str, list[str]]] | None:
        peer = ipaddress.ip_address(self.client_address[0])
        if not peer.is_loopback and not any(peer in network for network in self.console.allowed_networks):
            self._error(HTTPStatus.FORBIDDEN, "client_network", "Client is outside the allowed network")
            return None
        parsed = urlsplit(self.path)
        query = parse_qs(parsed.query, keep_blank_values=True)
        token = query.get("token", [""])[0]
        if not hmac.compare_digest(token, self.console._token):
            self._error(HTTPStatus.FORBIDDEN, "forbidden", "Forbidden")
            return None
        server = self.console._server
        expected = f"{self.console.host}:{server.server_address[1]}" if server is not None else ""
        if self.headers.get("Host", "") != expected:
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "Invalid local Host header")
            return None
        return parsed, query

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        result = self._parsed()
        if result is None:
            return
        parsed, query = result
        try:
            if parsed.path == "/":
                from ccs.web_ui import document

                self._send(HTTPStatus.OK, document().encode("utf-8"), "text/html; charset=utf-8")
                return
            if parsed.path == "/api/console":
                self._json(HTTPStatus.OK, self.console.console_state())
                return
            if parsed.path == "/api/state":
                run_id = query.get("run_id", [""])[0]
                cursor = query.get("cursor", [""])[0]
                self._json(HTTPStatus.OK, self.console.state_for_run(run_id, cursor))
                return
            if parsed.path == "/api/network":
                self._json(HTTPStatus.OK, self.console.network_state(query))
                return
            if parsed.path == "/api/analysis":
                self._json(HTTPStatus.OK, self.console.analysis_state(query))
                return
            if parsed.path == "/monitor":
                run_id = query.get("run_id", [""])[0]
                self.console._run_record(run_id)
                self._send(HTTPStatus.OK, monitor_document().encode("utf-8"), "text/html; charset=utf-8")
                return
        except KeyError:
            self._error(HTTPStatus.NOT_FOUND, "unknown_run", "Unknown run")
            return
        except (TypeError, ValueError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
            return
        except Exception:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "server_error", "Unable to read console state")
            return
        self._error(HTTPStatus.NOT_FOUND, "not_found", "Not found")

    def _read_payload(self) -> dict[str, Any] | None:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().casefold()
        if content_type != "application/json":
            self._error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "content_type", "Content-Type must be application/json")
            return None
        if self.headers.get("Transfer-Encoding"):
            self._error(HTTPStatus.BAD_REQUEST, "transfer_encoding", "Transfer-Encoding is not supported")
            return None
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(HTTPStatus.LENGTH_REQUIRED, "content_length", "A valid Content-Length is required")
            return None
        if length < 0 or length > _MAX_BODY:
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "body_too_large", "JSON body exceeds 2 MiB")
            return None
        try:
            value = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, "invalid_json", "Request body must be a JSON object")
            return None
        if not isinstance(value, dict):
            self._error(HTTPStatus.BAD_REQUEST, "invalid_json", "Request body must be a JSON object")
            return None
        return value

    def do_POST(self) -> None:  # noqa: N802
        result = self._parsed()
        if result is None:
            return
        parsed, _ = result
        server = self.console._server
        expected_origin = f"http://{self.console.host}:{server.server_address[1]}" if server is not None else ""
        if self.headers.get("Origin", "") != expected_origin:
            self._error(HTTPStatus.FORBIDDEN, "invalid_origin", "POST requires the console's same Origin")
            return
        payload = self._read_payload()
        if payload is None:
            return
        routes: dict[str, tuple[Callable[[dict[str, Any]], Any], HTTPStatus]] = {
            "/api/documents": (self.console.add_document, HTTPStatus.CREATED),
            "/api/documents/select": (self.console.select_document, HTTPStatus.OK),
            "/api/documents/edit": (self.console.edit_document, HTTPStatus.OK),
            "/api/documents/remove": (self.console.remove_document, HTTPStatus.OK),
            "/api/memory/clear": (self.console.clear_memory, HTTPStatus.OK),
            "/api/runs/start": (self.console.start_run, HTTPStatus.ACCEPTED),
            "/api/runs/stop": (self.console.stop_run, HTTPStatus.ACCEPTED),
            "/api/delay": (self.console.set_delay, HTTPStatus.OK),
        }
        route = routes.get(parsed.path)
        if route is None:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "Not found")
            return
        try:
            result_value = route[0](payload)
            response = result_value if isinstance(result_value, dict) else {"ok": True}
            if parsed.path == "/api/delay":
                response = {"seconds": result_value}
            self._json(route[1], response)
        except KeyError:
            self._error(HTTPStatus.NOT_FOUND, "unknown_document", "Unknown document")
        except RuntimeError as exc:
            self._error(HTTPStatus.CONFLICT, "conflict", str(exc))
        except (TypeError, ValueError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
        except Exception:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "server_error", "Request could not be completed")
