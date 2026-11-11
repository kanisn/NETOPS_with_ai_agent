"""Mutable, cross-process pacing control and run-local delay accounting."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import threading
import time
from typing import Any
import uuid


CONTROL_SCHEMA = "ccs-pacing-control@1"
POINTER_SCHEMA = "ccs-pacing-pointer@1"
POINTER_NAME = "pacing-pointer.json"
MAX_DELAY_SECONDS = 30.0
POLL_SECONDS = 0.05

_WRITE_LOCK = threading.Lock()
_SHARD_LOCK = threading.Lock()
_SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_delay(seconds: Any) -> float:
    """Return a finite delay in the supported inclusive range 0..30 seconds."""

    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise TypeError("delay must be a real number")
    value = float(seconds)
    if not math.isfinite(value) or not 0 <= value <= MAX_DELAY_SECONDS:
        raise ValueError("delay must be finite and between 0 and 30 seconds")
    return value


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writing = path.with_name(
        f"{path.name}.writing-{os.getpid()}-{threading.get_ident()}-{uuid.uuid4().hex}"
    )
    try:
        with writing.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, allow_nan=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(writing, path)
    finally:
        if writing.exists():
            writing.unlink()


def read_control(path: Path) -> dict[str, Any]:
    """Read and validate one atomic pacing control document."""

    control_path = Path(path).resolve()
    value = json.loads(control_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != CONTROL_SCHEMA:
        raise ValueError("invalid pacing control schema")
    seconds = validate_delay(value.get("seconds"))
    revision = value.get("revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("invalid pacing control revision")
    return {**value, "seconds": seconds, "revision": revision, "path": str(control_path)}


def write_control(path: Path, seconds: Any) -> dict[str, Any]:
    """Atomically set a shared delay and append a collision-free change record."""

    value = validate_delay(seconds)
    control_path = Path(path).resolve()
    with _WRITE_LOCK:
        try:
            previous = read_control(control_path)
            revision = int(previous["revision"]) + 1
        except FileNotFoundError:
            revision = 1
        now_ns = time.time_ns()
        document = {
            "schema": CONTROL_SCHEMA,
            "seconds": value,
            "revision": revision,
            "updated_at_utc": _utc_now(),
            "updated_unix_ns": now_ns,
        }
        _atomic_json(control_path, document)
        history_dir = control_path.parent / f"{control_path.name}.history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / (
            f"change-{now_ns}-{os.getpid()}-{threading.get_ident()}-{uuid.uuid4().hex}.json"
        )
        with history_path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump({**document, "control_path": str(control_path)}, handle, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    return {**document, "path": str(control_path)}


def install_run_pointer(run_dir: Path, control_path: Path) -> dict[str, Any]:
    """Install the immutable run-local pointer before the first activity event."""

    run_path = Path(run_dir).resolve()
    pointer_path = run_path / POINTER_NAME
    if pointer_path.exists():
        raise FileExistsError(f"pacing pointer already exists: {pointer_path}")
    control = read_control(Path(control_path))
    pointer = {
        "schema": POINTER_SCHEMA,
        "control_path": control["path"],
        "installed_at_utc": _utc_now(),
        "installed_unix_ns": time.time_ns(),
        "initial_seconds": control["seconds"],
        "initial_revision": control["revision"],
    }
    _atomic_json(pointer_path, pointer)
    return pointer


def control_path_for_run(run_dir: Path) -> Path | None:
    pointer_path = Path(run_dir) / POINTER_NAME
    if not pointer_path.is_file():
        return None
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    if not isinstance(pointer, dict) or pointer.get("schema") != POINTER_SCHEMA:
        raise ValueError("invalid run-local pacing pointer")
    return Path(pointer["control_path"])


def _safe_shard(writer_id: str) -> str:
    stem = _SAFE_NAME.sub("-", writer_id).strip(".-") or "writer"
    digest = hashlib.sha256(writer_id.encode("utf-8")).hexdigest()[:8]
    return f"{stem[:80]}-{digest}.jsonl"


def _append_timing(run_dir: Path, writer_id: str, record: dict[str, Any]) -> None:
    directory = Path(run_dir) / "pacing"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / _safe_shard(writer_id)
    line = json.dumps(record, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    with _SHARD_LOCK:
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def wait_after_event(
    run_dir: Path,
    writer_id: str,
    event_id: str,
    control_path: Path | None = None,
) -> float:
    """Wait after a persisted event while observing shared delay changes."""

    path = Path(control_path) if control_path is not None else control_path_for_run(run_dir)
    if path is None:
        return 0.0
    first = read_control(path)
    if first["seconds"] == 0:
        return 0.0

    wall_started_ns = time.time_ns()
    monotonic_started = time.monotonic()
    current = first
    observations = [{
        "observed_unix_ns": wall_started_ns,
        "revision": current["revision"],
        "seconds": current["seconds"],
    }]
    while True:
        elapsed = time.monotonic() - monotonic_started
        if current["seconds"] == 0 or elapsed >= current["seconds"]:
            break
        time.sleep(min(POLL_SECONDS, current["seconds"] - elapsed))
        updated = read_control(path)
        if (updated["revision"], updated["seconds"]) != (
            current["revision"], current["seconds"]
        ):
            observations.append({
                "observed_unix_ns": time.time_ns(),
                "revision": updated["revision"],
                "seconds": updated["seconds"],
            })
        current = updated

    wall_finished_ns = time.time_ns()
    actual = time.monotonic() - monotonic_started
    _append_timing(
        run_dir,
        writer_id,
        {
            "schema": "ccs-pacing-wait@1",
            "event_id": event_id,
            "writer_id": writer_id,
            "wall_started_unix_ns": wall_started_ns,
            "wall_finished_unix_ns": wall_finished_ns,
            "actual_wait_seconds": actual,
            "initial_seconds": first["seconds"],
            "final_seconds": current["seconds"],
            "observations": observations,
        },
    )
    return actual


def _history(control_path: Path, started_ns: int, finished_ns: int) -> list[dict[str, Any]]:
    directory = control_path.parent / f"{control_path.name}.history"
    changes: list[dict[str, Any]] = []
    if directory.is_dir():
        for path in directory.glob("change-*.json"):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                changed_ns = int(value["updated_unix_ns"])
                if started_ns <= changed_ns <= finished_ns:
                    changes.append({
                        "updated_at_utc": value["updated_at_utc"],
                        "updated_unix_ns": changed_ns,
                        "revision": int(value["revision"]),
                        "seconds": validate_delay(value["seconds"]),
                    })
            except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
    return sorted(changes, key=lambda item: (item["updated_unix_ns"], item["revision"]))


def summarize_timing(
    run_dir: Path,
    *,
    started_unix_ns: int,
    finished_unix_ns: int,
) -> dict[str, Any]:
    """Summarize elapsed time and both union and worker-summed intentional delay."""

    run_path = Path(run_dir)
    intervals: list[tuple[int, int]] = []
    summed = 0.0
    wait_count = 0
    pacing_dir = run_path / "pacing"
    if pacing_dir.is_dir():
        for path in pacing_dir.glob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                value = json.loads(line)
                start = int(value["wall_started_unix_ns"])
                finish = int(value["wall_finished_unix_ns"])
                if finish >= start:
                    intervals.append((start, finish))
                    # Use the same wall-clock endpoints as the union calculation so
                    # rounding between wall and monotonic clocks cannot invert the
                    # expected summed >= union relationship.
                    summed += (finish - start) / 1_000_000_000
                    wait_count += 1
    intervals.sort()
    merged: list[list[int]] = []
    for start, finish in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, finish])
        else:
            merged[-1][1] = max(merged[-1][1], finish)
    union = sum(finish - start for start, finish in merged) / 1_000_000_000
    elapsed = max(0.0, (finished_unix_ns - started_unix_ns) / 1_000_000_000)
    pointer = json.loads((run_path / POINTER_NAME).read_text(encoding="utf-8"))
    control_path = Path(pointer["control_path"])
    final = read_control(control_path)
    return {
        "elapsed_wall_seconds": elapsed,
        "delay_union_seconds": union,
        "summed_worker_delay_seconds": summed,
        "elapsed_minus_delay_union_seconds_estimate": max(0.0, elapsed - union),
        "delayed_event_count": wait_count,
        "initial_delay_seconds": validate_delay(pointer["initial_seconds"]),
        "final_delay_seconds": final["seconds"],
        "delay_change_history": _history(control_path, started_unix_ns, finished_unix_ns),
    }


def timeout_allowance_seconds(system: Any) -> float:
    """Bound protocol headroom using configured finite workflow/step limits."""

    nested_events = (
        16
        + int(system.context_steps) * 4
        + int(system.max_agent_steps) * 4
        + int(system.diagnosis_tool_budget) * (int(system.read_retries) + 1) * 5
    )
    return MAX_DELAY_SECONDS * nested_events
