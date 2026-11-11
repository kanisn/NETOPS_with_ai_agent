from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import threading
import time
import uuid

import pytest

from tests.support_paths import workspace_for
from ccs.observability import ActivityLog
from ccs.pacing import (
    install_run_pointer,
    read_control,
    summarize_timing,
    validate_delay,
    write_control,
)


WORK = workspace_for("test_pacing")


@pytest.fixture
def work() -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / f"case-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


@pytest.mark.parametrize("value", [-0.1, 30.1, math.inf, -math.inf, math.nan])
def test_delay_rejects_out_of_range_and_nonfinite_values(value: float) -> None:
    with pytest.raises(ValueError):
        validate_delay(value)


@pytest.mark.parametrize("value", [True, "1"])
def test_delay_rejects_non_numeric_values(value: object) -> None:
    with pytest.raises(TypeError):
        validate_delay(value)


def test_atomic_control_writers_keep_valid_monotonic_revisions(work: Path) -> None:
    path = work / "control.json"
    assert write_control(path, 0)["revision"] == 1
    threads = [threading.Thread(target=write_control, args=(path, index / 10)) for index in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()
    current = read_control(path)
    assert current["revision"] == 11
    assert 0 <= current["seconds"] <= 0.9
    history = list((work / "control.json.history").glob("change-*.json"))
    assert len(history) == 11
    assert all(json.loads(item.read_text(encoding="utf-8"))["schema"] == "ccs-pacing-control@1" for item in history)


def test_zero_delay_returns_immediately_without_timing_shard(work: Path) -> None:
    control = work / "control.json"
    write_control(control, 0)
    install_run_pointer(work, control)
    started = time.monotonic()
    ActivityLog(work, "zero").emit("runner", "step", "info", "zero-delay step")
    assert time.monotonic() - started < 0.2
    assert not (work / "pacing").exists()


def test_no_delay_change_releases_current_wait_and_records_union(work: Path) -> None:
    control = work / "control.json"
    write_control(control, 2)
    pointer = install_run_pointer(work, control)
    pointer_before = (work / "pacing-pointer.json").read_bytes()
    started_ns = time.time_ns()
    completed = threading.Event()

    def emit() -> None:
        ActivityLog(work, "dynamic").emit("runner", "step", "info", "paced step")
        completed.set()

    thread = threading.Thread(target=emit)
    thread.start()
    deadline = time.monotonic() + 1
    while not (work / "activity" / "dynamic.jsonl").is_file() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert (work / "activity" / "dynamic.jsonl").is_file()
    time.sleep(0.12)
    changed_at = time.monotonic()
    write_control(control, 0)
    thread.join(timeout=0.5)
    assert completed.is_set()
    assert time.monotonic() - changed_at < 0.2
    assert (work / "pacing-pointer.json").read_bytes() == pointer_before
    timing = summarize_timing(work, started_unix_ns=started_ns, finished_unix_ns=time.time_ns())
    assert timing["initial_delay_seconds"] == pointer["initial_seconds"] == 2
    assert timing["final_delay_seconds"] == 0
    assert timing["delayed_event_count"] == 1
    assert 0.1 <= timing["delay_union_seconds"] < 1
    assert timing["summed_worker_delay_seconds"] >= timing["delay_union_seconds"] - 0.02
    assert timing["delay_change_history"][-1]["seconds"] == 0
