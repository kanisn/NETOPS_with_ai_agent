from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import uuid

import pytest

from tests.support_paths import workspace_for
from ccs.core.bus import EventBus
from ccs.core.gateway import Gateway
from ccs.observability import ActivityLog, activity_for_episode
from ccs.tool_access import InstrumentedTools


WORKING_ROOT = workspace_for("test_activity", legacy_env="CCS_ACTIVITY_WORKING_ROOT")


@pytest.fixture
def run_dir() -> Path:
    WORKING_ROOT.mkdir(parents=True, exist_ok=True)
    path = WORKING_ROOT / f"run-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def _events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_activity_log_flushes_schema_pairs_operations_and_resumes(run_dir: Path) -> None:
    activity = ActivityLog(run_dir, "runner", "episode-0001", "mock")
    operation = activity.emit(
        "runner",
        "episode",
        "started",
        "Episode started",
        details={"request": "inspect HOST-001"},
        trace_id="trace-1",
    )
    activity.emit(
        "runner",
        "episode",
        "succeeded",
        "Episode completed",
        operation_id=operation,
        details={"outcome": "RECOVERED"},
        trace_id="trace-1",
    )

    # A second instance resumes the shard rather than overwriting it.
    resumed = ActivityLog(run_dir, "runner", "episode-0002", "mock")
    resumed.emit("runner", "episode", "info", "Next episode")
    events = _events(activity.shard_path)
    required = {
        "event_id",
        "ts_utc",
        "run_id",
        "episode_id",
        "writer_id",
        "local_seq",
        "component",
        "action",
        "status",
        "summary",
        "details",
        "operation_id",
        "mode",
    }
    assert all(required <= event.keys() for event in events)
    assert events[0]["operation_id"] == operation == events[0]["event_id"]
    assert events[1]["operation_id"] == operation
    assert [event["local_seq"] for event in events] == [1, 2, 3]
    assert events[-1]["episode_id"] == "episode-0002"


def test_activity_log_scrubs_entire_record_and_explicit_secrets(run_dir: Path) -> None:
    provider_key = "arbitrary-provider-key-value-12345"
    activity = ActivityLog(run_dir, "unsafe writer/name", secrets=[provider_key])
    activity.emit(
        "model",
        "request",
        "info",
        f"Bearer bearer-secret-123 and {provider_key}",
        details={
            "api_key": provider_key,
            "change_token": "capability-token-value",
            "nested": {"text": f"key={provider_key}", "raw_response": "must-not-be-passed"},
        },
        note=f"sk-examplecredential12345 {provider_key}",
    )
    text = activity.shard_path.read_text(encoding="utf-8")
    event = json.loads(text)
    assert provider_key not in text
    assert "bearer-secret-123" not in text
    assert "sk-examplecredential12345" not in text
    assert "must-not-be-passed" not in text
    assert event["details"]["api_key"] == "[REDACTED]"
    assert event["details"]["change_token"] == "[REDACTED]"
    assert event["details"]["nested"]["raw_response"] == "[REDACTED]"
    assert "/" not in activity.shard_path.name


def test_activity_for_episode_derives_run_and_collision_free_writer(run_dir: Path) -> None:
    episode_dir = run_dir / "episodes" / "episode-0042"
    episode_dir.mkdir(parents=True)
    activity = activity_for_episode(episode_dir, "diagnosis", "mock")
    activity.emit("diagnosis", "investigate", "started", "Started")
    event = _events(run_dir / "activity" / "diagnosis-episode-0042.jsonl")[0]
    assert event["run_id"] == run_dir.name
    assert event["episode_id"] == "episode-0042"
    assert event["writer_id"] == "diagnosis-episode-0042"


@pytest.mark.asyncio
async def test_instrumented_tools_records_list_call_arguments_results_and_duration(run_dir: Path) -> None:
    episode = "episode-0001"
    (run_dir / "episodes" / episode).mkdir(parents=True)
    bus = EventBus(run_dir, "test-caller", run_dir.name, episode)
    gateway = Gateway(bus)
    tools = InstrumentedTools(
        "http://127.0.0.1:1/mcp",
        "diagnosis-token-value",
        gateway,
        "diagnosis",
        "trace-tools",
        read_retries=0,
        mode="mock",
    )

    class FakeClient:
        async def list_tools(self):
            return [{"name": "get_config", "parameters": {"type": "object"}}]

        async def call(self, name, arguments, metadata):
            assert metadata["trace_id"] == "trace-tools"
            return {"items": [{"target": arguments["target"], "value": 7}], "_ccs_event_id": "server-event"}

    tools.client = FakeClient()
    assert [item["name"] for item in await tools.list_tools()] == ["get_config"]
    result = await tools.call("get_config", {"target": "HOST-001"})
    assert result == {"items": [{"target": "HOST-001", "value": 7}]}

    events = _events(run_dir / "activity" / f"mcp-diagnosis-{episode}.jsonl")
    assert [(event["action"], event["status"]) for event in events] == [
        ("list_tools", "started"),
        ("list_tools", "succeeded"),
        ("call", "started"),
        ("call", "succeeded"),
    ]
    completed = events[-1]
    assert completed["details"]["arguments"] == {"target": "HOST-001"}
    assert completed["details"]["result"] == result
    assert completed["details"]["duration_seconds"] >= 0
    assert "diagnosis-token-value" not in completed["summary"]
