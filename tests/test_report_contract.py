import json
import os
from pathlib import Path
import uuid

import pytest

from tests.support_paths import workspace_for
from ccs.agent_runtime import AgentFailure, compose_report
from ccs.config import load_ai, load_system
from ccs.llm import ToolCall


ROOT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_report_contract")


def work():
    path = WORK / uuid.uuid4().hex
    path.mkdir(parents=True)
    return path


def facts():
    return {
        "outcome": "RECOVERED",
        "verify": {"passed": True},
        "diagnosis": {"root_cause": "Primary link recovered after the approved change."},
        "change": {"target": "LINK-001", "param": "active_path", "value": "backup"},
    }


def report(outcome):
    return {
        "summary": "The service recovered and passed verification.",
        "root_cause": "The primary link was unavailable.",
        "action": "Switched the active path to the verified backup.",
        "outcome": outcome,
        "evidence": ["verify.passed was true"],
    }


@pytest.mark.asyncio
async def test_report_contract_rejects_prose_outcome_then_repairs(monkeypatch):
    class ScriptedConversation:
        calls = 0
        schemas = []
        results = []

        def __init__(self, *args, **kwargs):
            pass

        async def next(self, schemas, **kwargs):
            type(self).calls += 1
            type(self).schemas.append(schemas)
            outcome = "RECOVERED: verification passed after the change" if type(self).calls == 1 else "RECOVERED"
            return [ToolCall(str(type(self).calls), "submit_report", report(outcome))]

        def result(self, call, result):
            type(self).results.append(result)

        async def close(self):
            pass

    monkeypatch.setattr("ccs.agent_runtime.Conversation", ScriptedConversation)
    ai = load_ai(ROOT / "configs/ai.example.xml")
    result = await compose_report(ai, load_system(ROOT / "configs/system.xml"), facts(), work(), mode="live")

    assert result == report("RECOVERED")
    assert ScriptedConversation.calls == 2
    schema = ScriptedConversation.schemas[0][0]["parameters"]
    assert schema["properties"]["outcome"]["enum"] == ["RECOVERED"]
    assert "exactly" in schema["properties"]["outcome"]["description"]
    feedback = ScriptedConversation.results[0]["error"]
    assert 'exactly as "RECOVERED"' in feedback
    assert "put explanations in summary" in feedback
    assert "RECOVERED: verification passed" not in json.dumps(ScriptedConversation.results)


@pytest.mark.asyncio
async def test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit(monkeypatch):
    class ScriptedConversation:
        calls = 0
        results = []

        def __init__(self, *args, **kwargs):
            pass

        async def next(self, schemas, **kwargs):
            type(self).calls += 1
            return [ToolCall(str(type(self).calls), "submit_report", report("RECOVERED: verification passed"))]

        def result(self, call, result):
            type(self).results.append(result)

        async def close(self):
            pass

    monkeypatch.setattr("ccs.agent_runtime.Conversation", ScriptedConversation)
    ai = load_ai(ROOT / "configs/ai.example.xml")
    with pytest.raises(AgentFailure, match="FAILED_LLM_SCHEMA"):
        await compose_report(ai, load_system(ROOT / "configs/system.xml"), facts(), work(), mode="live")

    assert ScriptedConversation.calls == ai.schema_retries + 1
    assert len(ScriptedConversation.results) == ai.schema_retries + 1
    assert all('exactly as "RECOVERED"' in result["error"] for result in ScriptedConversation.results)
