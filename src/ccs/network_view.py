"""Read-only, human-facing wired-network state for the web console.

The projection is deliberately separate from agent context collection. It
opens episode databases read-only and returns only the wired topology,
configuration, alarms, KPIs, and recorded changes needed by the operator UI.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any

from ccs.bench.scenarios import FAULTS, create_world
from ccs.netops.errors import ContractError
from ccs.netops.sqlite_backend import BACKEND_ID, SCHEMA_VERSION, SQLiteBackend


_DIFFICULTIES = {"L1", "L2", "L3"}
_TARGET = re.compile(r"HOST-[A-Z0-9][A-Z0-9_-]{0,63}\Z")
_EPISODE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
_PREVIEW_CACHE: dict[tuple[str, tuple[str, int, str, str]], dict[str, Any]] = {}
_PREVIEW_LOCK = threading.RLock()
_SNAPSHOT_KEYS = (
    "backend_id",
    "schema_version",
    "state_version",
    "nodes",
    "interfaces",
    "links",
    "flows",
    "configuration",
    "changes",
)


class _ReadOnlyBackend(SQLiteBackend):
    """Use ``SQLiteBackend`` reads over a transactionally pinned connection."""

    def __init__(self, path: Path):
        self.path = Path(path).resolve()
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            self.path.as_uri() + "?mode=ro",
            uri=True,
            isolation_level=None,
            check_same_thread=False,
            timeout=1.0,
        )
        self._connection.row_factory = sqlite3.Row
        try:
            self._connection.execute("PRAGMA query_only=ON")
            self._connection.execute("PRAGMA busy_timeout=1000")
            self._connection.execute("BEGIN")
            metadata = dict(self._connection.execute("SELECT key, value FROM metadata"))
            if metadata.get("backend_id") != BACKEND_ID or metadata.get("schema_version") != SCHEMA_VERSION:
                raise ContractError(
                    f"database does not implement {BACKEND_ID} schema version {SCHEMA_VERSION}"
                )
        except Exception:
            self.close()
            raise


def _selection(fault: str, seed: int, difficulty: str, target: str) -> tuple[str, int, str, str]:
    if not isinstance(fault, str):
        raise ValueError("fault must be W1 through W5 or N0")
    fault = fault.strip().upper()
    if fault not in FAULTS:
        raise ValueError("fault must be W1 through W5 or N0")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2**31 - 1:
        raise ValueError("seed must be an integer from 0 through 2147483647")
    if not isinstance(difficulty, str):
        raise ValueError("difficulty must be L1, L2, or L3")
    difficulty = difficulty.strip().upper()
    if difficulty not in _DIFFICULTIES:
        raise ValueError("difficulty must be L1, L2, or L3")
    if not isinstance(target, str):
        raise ValueError("target must be a safe HOST identifier")
    target = target.strip().upper()
    if _TARGET.fullmatch(target) is None:
        raise ValueError("target must be a safe HOST identifier")
    return fault, seed, difficulty, target


def _safe_episode(episode_id: str | None) -> str | None:
    if episode_id is None:
        return None
    if not isinstance(episode_id, str) or _EPISODE.fullmatch(episode_id) is None:
        raise ValueError("episode_id must be a safe path component")
    return episode_id


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_run_id(run_dir: Path, manifest: Any) -> str | None:
    candidate = manifest.get("run_id") if isinstance(manifest, dict) else None
    if not isinstance(candidate, str) or _RUN_ID.fullmatch(candidate) is None:
        candidate = run_dir.name
    return candidate if _RUN_ID.fullmatch(candidate) is not None else None


def _empty_run(run_id: str | None, episode_id: str | None) -> dict[str, Any]:
    return {
        "source": "run",
        "backend_id": BACKEND_ID,
        "fault": None,
        "seed": None,
        "episode_id": episode_id,
        "run_id": run_id,
        "state_version": None,
        "target": None,
        "configuration": [],
        "kpis": [],
        "alarms": [],
        "topology": {"nodes": [], "interfaces": [], "links": []},
        "changes": [],
        "available": False,
    }


def _changes(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    raw_changes = snapshot.get("changes", [])
    if not isinstance(raw_changes, list):
        return result
    for raw in raw_changes[-50:]:
        if not isinstance(raw, dict):
            continue
        change_id, target, param = raw.get("change_id"), raw.get("target"), raw.get("param")
        if not all(isinstance(value, str) and value for value in (change_id, target, param)):
            continue
        result.append(
            {
                "id": change_id,
                "target": target,
                "param": param,
                "before": copy.deepcopy(raw.get("before_value")),
                "after": copy.deepcopy(raw.get("after_value")),
                "status": raw.get("status"),
            }
        )
    return result


def _configuration(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    raw_configuration = snapshot.get("configuration", [])
    if not isinstance(raw_configuration, list):
        return result
    for item in raw_configuration:
        if not isinstance(item, dict):
            continue
        target, param = item.get("target"), item.get("param")
        if not isinstance(target, str) or not target or not isinstance(param, str) or not param:
            continue
        value = copy.deepcopy(item.get("current_value"))
        reference = copy.deepcopy(item.get("reference_value"))
        at_reference = item.get("is_at_reference")
        result.append(
            {
                "id": f"{target}:{param}",
                "target": target,
                "param": param,
                "value": value,
                "reference_value": reference,
                "at_reference": at_reference if isinstance(at_reference, bool) else value == reference,
            }
        )
    return result


def _kpis(raw: dict[str, Any]) -> list[dict[str, Any]]:
    target = raw.get("target")
    return [
        {
            "id": f"{target}:{sample.get('metric')}",
            "target": target,
            "metric": sample.get("metric"),
            "value": sample.get("value"),
            "unit": sample.get("unit"),
            "status": sample.get("status"),
        }
        for sample in raw.get("samples", [])
        if isinstance(sample, dict)
    ]


def _alarms(raw: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for alarm in raw.get("alarms", []):
        if not isinstance(alarm, dict):
            continue
        item = {
            "id": alarm.get("alarm_id"),
            "target": alarm.get("target"),
            "severity": alarm.get("severity"),
            "status": alarm.get("status"),
        }
        if alarm.get("summary"):
            item["message"] = alarm["summary"]
        result.append(item)
    return result


def _topology(snapshot: dict[str, Any], kpis: list[dict[str, Any]], target: str) -> dict[str, Any]:
    degraded = any(item.get("status") != "ok" for item in kpis)
    nodes = []
    for raw in snapshot.get("nodes", []):
        if not isinstance(raw, dict):
            continue
        node_id, node_type = raw.get("node_id"), raw.get("node_type")
        if not isinstance(node_id, str) or not node_id:
            continue
        recorded_status = raw.get("status")
        nodes.append(
            {
                "id": node_id,
                "type": node_type,
                "label": raw.get("label") or node_id,
                "status": (
                    recorded_status
                    if isinstance(recorded_status, str) and recorded_status
                    else "degraded" if node_id == target and degraded else "ok"
                ),
            }
        )

    interfaces = []
    interface_to_node: dict[str, str] = {}
    for raw in snapshot.get("interfaces", []):
        if not isinstance(raw, dict):
            continue
        interface_id, node_id = raw.get("interface_id"), raw.get("node_id")
        if not isinstance(interface_id, str) or not isinstance(node_id, str):
            continue
        interface_to_node[interface_id] = node_id
        admin_state = raw.get("admin_state")
        interfaces.append(
            {
                "id": interface_id,
                "node": node_id,
                "name": raw.get("name"),
                "ipv4_cidr": raw.get("ipv4_cidr"),
                "admin_state": admin_state,
                "status": "ok" if admin_state == "up" else "degraded",
            }
        )

    links = []
    for raw in snapshot.get("links", []):
        if not isinstance(raw, dict):
            continue
        link_id = raw.get("link_id")
        source_interface, target_interface = raw.get("source_interface"), raw.get("target_interface")
        if not all(isinstance(value, str) and value for value in (link_id, source_interface, target_interface)):
            continue
        links.append(
            {
                "id": link_id,
                "source": interface_to_node.get(source_interface, source_interface),
                "target": interface_to_node.get(target_interface, target_interface),
                "source_interface": source_interface,
                "target_interface": target_interface,
                "path": raw.get("path"),
                "capacity_mbps": raw.get("capacity_mbps"),
                "delay_ms": raw.get("delay_ms"),
                "loss_pct": raw.get("loss_pct"),
                "status": raw.get("status"),
            }
        )
    return {"nodes": nodes, "interfaces": interfaces, "links": links}


def _validated_snapshot(live: dict[str, Any], final: dict[str, Any] | None) -> dict[str, Any]:
    if final is None:
        return live
    if not isinstance(final.get("configuration"), list):
        raise ContractError("final state is missing wired configuration")
    if any(final.get(key) != live.get(key) for key in _SNAPSHOT_KEYS):
        raise ContractError("final state does not match the run database")
    return live


def _state_from_db(
    db_path: Path,
    *,
    source: str,
    fault: str,
    seed: int,
    episode_id: str | None,
    run_id: str | None,
    target: str,
    final_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with _ReadOnlyBackend(db_path) as backend:
        snapshot = _validated_snapshot(backend.snapshot(), final_snapshot)
        kpis = _kpis(backend.call("get_kpi", {"target": target}))
        alarms = _alarms(backend.call("list_alarms", {"limit": 50}))
    return {
        "source": source,
        "backend_id": snapshot["backend_id"],
        "fault": fault,
        "seed": seed,
        "episode_id": episode_id,
        "run_id": run_id,
        "state_version": snapshot["state_version"],
        "target": target,
        "configuration": _configuration(snapshot),
        "kpis": kpis,
        "alarms": alarms,
        "topology": _topology(snapshot, kpis, target),
        "changes": _changes(snapshot),
        "available": True,
    }


def _preview_paths(workspace: Path, key: tuple[str, int, str, str]) -> tuple[Path, Path, Path]:
    fingerprint = hashlib.sha256(
        json.dumps(key, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()[:24]
    directory = Path(workspace).resolve() / "preview" / fingerprint
    return directory / "network.sqlite", directory / "network.building.sqlite", directory / "pane.json"


def preview_network(
    workspace: Path,
    *,
    fault: str,
    seed: int,
    difficulty: str,
    target: str = "HOST-001",
) -> dict[str, Any]:
    """Return a deterministic wired initial-state preview, cached by selection."""

    key = _selection(fault, seed, difficulty, target)
    workspace = Path(workspace).resolve()
    memory_key = (str(workspace), key)
    with _PREVIEW_LOCK:
        cached = _PREVIEW_CACHE.get(memory_key)
        if cached is not None:
            return copy.deepcopy(cached)
        db_path, building_path, pane_path = _preview_paths(workspace, key)
        if pane_path.is_file():
            try:
                pane = _read_json(pane_path)
                if (
                    isinstance(pane, dict)
                    and pane.get("source") == "preview"
                    and pane.get("backend_id") == BACKEND_ID
                    and pane.get("available") is True
                    and (pane.get("fault"), pane.get("seed"), pane.get("target"))
                    == (key[0], key[1], key[3])
                ):
                    _PREVIEW_CACHE[memory_key] = pane
                    return copy.deepcopy(pane)
            except (OSError, ValueError, TypeError):
                pass

        db_path.parent.mkdir(parents=True, exist_ok=True)
        scenario = create_world(
            building_path,
            seed=key[1],
            fault_id=key[0],
            target=key[3],
            difficulty=key[2],
        )
        os.replace(building_path, db_path)
        pane = _state_from_db(
            db_path,
            source="preview",
            fault=key[0],
            seed=key[1],
            episode_id=None,
            run_id=None,
            target=key[3],
        )
        if (scenario.get("fault_id"), scenario.get("seed"), scenario.get("target")) != (
            key[0], key[1], key[3]
        ):
            raise RuntimeError("preview scenario metadata did not match its cache key")
        writing = pane_path.with_name("pane.building.json")
        writing.write_text(json.dumps(pane, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(writing, pane_path)
        _PREVIEW_CACHE[memory_key] = pane
        return copy.deepcopy(pane)


def read_network(run_dir: Path, episode_id: str | None = None) -> dict[str, Any]:
    """Read the selected or latest wired episode without mutating artifacts."""

    episode_id = _safe_episode(episode_id)
    run_dir = Path(run_dir).resolve()
    manifest: Any = {}
    try:
        if (run_dir / "manifest.json").is_file():
            manifest = _read_json(run_dir / "manifest.json")
    except (OSError, ValueError, TypeError):
        manifest = {}
    run_id = _safe_run_id(run_dir, manifest)

    episodes_root = (run_dir / "episodes").resolve()
    if episode_id is None:
        try:
            candidates = sorted(
                path.name
                for path in episodes_root.iterdir()
                if path.is_dir()
                and _EPISODE.fullmatch(path.name) is not None
                and (path / "network.sqlite").is_file()
            )
        except OSError:
            candidates = []
        if not candidates:
            return _empty_run(run_id, None)
        episode_id = candidates[-1]

    episode_dir = (episodes_root / episode_id).resolve()
    if not episode_dir.is_relative_to(episodes_root):
        raise ValueError("episode_id escaped the run episodes directory")
    unavailable = _empty_run(run_id, episode_id)
    db_path = episode_dir / "network.sqlite"
    scenario_path = episode_dir / "scenario.restricted.json"
    if not db_path.is_file() or not scenario_path.is_file():
        return unavailable

    try:
        scenario = _read_json(scenario_path)
        if not isinstance(scenario, dict):
            return unavailable
        fault, seed, _, target = _selection(
            scenario.get("fault_id"), scenario.get("seed"), "L1", scenario.get("target")
        )
        final_path = episode_dir / "final-state.restricted.json"
        final_snapshot = _read_json(final_path) if final_path.is_file() else None
        if final_snapshot is not None and not isinstance(final_snapshot, dict):
            return unavailable
        return _state_from_db(
            db_path,
            source="run",
            fault=fault,
            seed=seed,
            episode_id=episode_id,
            run_id=run_id,
            target=target,
            final_snapshot=final_snapshot,
        )
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error, ContractError):
        return unavailable
