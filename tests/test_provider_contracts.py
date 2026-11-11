"""Offline native-SDK contract tests for the provider adapters.

Every HTTP request is intercepted by ``httpx2.MockTransport``. The credentials
are explicit non-secret test sentinels loaded through a module-isolated copy of the
public example configuration.
"""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

import anthropic
import httpx2
import openai
import pytest

from tests.support_paths import workspace_for
from ccs.config import load_ai
from ccs.budget import BudgetExceeded
from ccs.llm import Conversation, ProviderError, ProviderSchemaError, object_tool


PROJECT = Path(__file__).resolve().parents[1]
WORK_ROOT = workspace_for("test_provider_contracts")
OPENAI_FAKE_KEY = "sk-test-openai-not-a-real-key"
ANTHROPIC_FAKE_KEY = "sk-ant-test-not-a-real-key"
TOOL = object_tool(
    "inspect_target",
    "Inspect one synthetic network target.",
    {"target": {"type": "string"}},
    ["target"],
)


def fresh_config():
    work = WORK_ROOT / uuid.uuid4().hex
    work.mkdir(parents=True)
    xml = (PROJECT / "configs" / "ai.example.xml").read_text(encoding="utf-8")
    xml = xml.replace(
        '<api_key env="OPENAI_API_KEY"></api_key>',
        f"<api_key>{OPENAI_FAKE_KEY}</api_key>",
    ).replace(
        '<api_key env="ANTHROPIC_API_KEY"></api_key>',
        f"<api_key>{ANTHROPIC_FAKE_KEY}</api_key>",
    )
    tree = ET.fromstring(xml)
    tree.find("budget").set("ledger_path", str(work / "ledger.sqlite"))
    xml = ET.tostring(tree, encoding="unicode")
    config_path = work / "ai.fake.xml"
    config_path.write_text(xml, encoding="utf-8")
    config = load_ai(config_path)
    assert config.ledger_path.parent == work
    return config, work


def openai_response(
    *,
    response_id: str = "resp_1",
    call_id: str | None = "call_1",
    arguments: str = '{"target":"HOST-001"}',
    cached_tokens: int = 40,
    cache_write_tokens: int = 0,
) -> dict:
    output: list[dict] = [
        {
            "id": f"reasoning_{response_id}",
            "type": "reasoning",
            "summary": [],
            "encrypted_content": f"encrypted-{response_id}",
            "status": "completed",
        }
    ]
    if call_id is not None:
        output.append(
            {
                "id": f"function_{response_id}",
                "type": "function_call",
                "call_id": call_id,
                "name": "inspect_target",
                "arguments": arguments,
                "status": "completed",
            }
        )
    return {
        "id": response_id,
        "object": "response",
        "created_at": 1_800_000_000,
        "model": "gpt-6-luna",
        "output": output,
        "parallel_tool_calls": False,
        "tool_choice": "required",
        "tools": [],
        "status": "completed",
        "usage": {
            "input_tokens": 100,
            "input_tokens_details": {"cached_tokens": cached_tokens, "cache_write_tokens": cache_write_tokens},
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 5},
            "total_tokens": 120,
        },
    }


def anthropic_response(
    *,
    message_id: str = "msg_1",
    tool_id: str = "toolu_1",
    tool_input: object | None = None,
) -> dict:
    return {
        "id": message_id,
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-5",
        "content": [
            {
                "type": "thinking",
                "thinking": "Inspect the current synthetic state.",
                "signature": f"signature-{message_id}",
            },
            {
                "type": "tool_use",
                "id": tool_id,
                "name": "inspect_target",
                "input": {"target": "HOST-001"} if tool_input is None else tool_input,
            },
        ],
        "stop_reason": "tool_use",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 100,
            "output_tokens": 25,
            "cache_creation_input_tokens": 10,
            "cache_read_input_tokens": 20,
        },
    }


async def replace_openai_client(conversation: Conversation, handler) -> None:
    await conversation.client.close()
    wire = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    conversation.client = openai.AsyncOpenAI(
        api_key=OPENAI_FAKE_KEY,
        http_client=wire,
        max_retries=0,
    )


async def replace_anthropic_client(conversation: Conversation, handler) -> None:
    await conversation.client.close()
    wire = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    conversation.client = anthropic.AsyncAnthropic(
        api_key=ANTHROPIC_FAKE_KEY,
        http_client=wire,
        max_retries=0,
    )


def records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.asyncio
async def test_openai_responses_preserves_reasoning_tool_history_and_cached_usage() -> None:
    config, work = fresh_config()
    requests: list[dict] = []
    replies = [
        openai_response(response_id="resp_1", call_id="call_1", cache_write_tokens=30),
        openai_response(response_id="resp_2", call_id="call_2", cached_tokens=10),
    ]

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json=replies.pop(0),
            headers={"x-request-id": f"request-{len(requests)}"},
        )

    conversation = Conversation(config, "operation", "System contract", {"incident": "synthetic"}, work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        first = (await conversation.next([TOOL]))[0]
        conversation.result(first, {"state": "degraded"})
        second = (await conversation.next([TOOL]))[0]
    finally:
        await conversation.close()

    assert first.id == "call_1"
    assert second.id == "call_2"
    assert all(request["model"] == "gpt-6-luna" for request in requests)
    assert requests[0]["include"] == ["reasoning.encrypted_content"]
    assert requests[0]["reasoning"] == {"effort": "low"}
    assert requests[0]["store"] is False
    assert requests[0]["parallel_tool_calls"] is False
    assert requests[0]["tool_choice"] == "required"
    second_input = requests[1]["input"]
    assert all('async_' not in item for item in second_input)
    assert all(value is not None for item in second_input for value in item.values())
    assert any(item.get("type") == "reasoning" and item.get("encrypted_content") == "encrypted-resp_1" for item in second_input)
    assert any(item.get("type") == "function_call" and item.get("call_id") == "call_1" for item in second_input)
    assert any(item.get("type") == "function_call_output" and item.get("call_id") == "call_1" for item in second_input)

    usage = records(conversation.log_path)
    assert usage[0]["input_tokens"] == 100
    assert usage[0]["cached_input_tokens"] == 40
    assert usage[0]["cache_write_input_tokens"] == 30
    assert Decimal(usage[0]["cost_usd"]) == Decimal("0.00001715")
    assert usage[0]["resolved_model"] == "gpt-6-luna"
    assert usage[0]["request_id"] == "request-1"
    assert OPENAI_FAKE_KEY not in conversation.log_path.read_text(encoding="utf-8")
    assert config.ledger_path.parent == work


@pytest.mark.asyncio
async def test_cache_write_premium_is_reserved_before_api_request() -> None:
    config, work = fresh_config()
    # This request fits at the ordinary input rate, but not at the write rate.
    config.budget_usd = Decimal("0.0019")
    requests = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=openai_response())

    conversation = Conversation(config, "operation", "System", "incident", work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        with pytest.raises(BudgetExceeded):
            await conversation.next([TOOL])
    finally:
        await conversation.close()
    assert requests == []
    assert conversation.ledger.summary()["calls"] == 0


@pytest.mark.asyncio
async def test_anthropic_adaptive_tool_blocks_history_and_cache_accounting() -> None:
    config, work = fresh_config()
    requests: list[dict] = []
    replies = [
        anthropic_response(message_id="msg_1", tool_id="toolu_1"),
        anthropic_response(message_id="msg_2", tool_id="toolu_2"),
    ]

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json=replies.pop(0),
            headers={"request-id": f"anthropic-request-{len(requests)}"},
        )

    conversation = Conversation(
        config,
        "diagnosis",
        "System contract",
        {"incident": "synthetic"},
        work / "logs",
        profile_override="sonnet5",
    )
    await replace_anthropic_client(conversation, handler)
    try:
        first = (await conversation.next([TOOL]))[0]
        conversation.result(first, {"state": "degraded"})
        second = (await conversation.next([TOOL]))[0]
    finally:
        await conversation.close()

    assert first.id == "toolu_1"
    assert second.id == "toolu_2"
    assert requests[0]["thinking"] == {"type": "adaptive"}
    assert requests[0]["output_config"] == {"effort": "low"}
    assert all(option not in requests[0] for option in ("temperature", "top_p", "top_k"))
    assert requests[0]["tools"][0]["input_schema"] == TOOL["parameters"]
    second_messages = requests[1]["messages"]
    assistant = next(message for message in second_messages if message["role"] == "assistant")
    assert [block["type"] for block in assistant["content"]] == ["thinking", "tool_use"]
    tool_result = second_messages[-1]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert tool_result["tool_use_id"] == "toolu_1"

    usage = records(conversation.log_path)
    assert usage[0]["input_tokens"] == 130
    assert usage[0]["cached_input_tokens"] == 20
    assert Decimal(usage[0]["cost_usd"]) == Decimal("0.000479")
    assert ANTHROPIC_FAKE_KEY not in conversation.log_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_openai_nonbillable_http_error_releases_reservation_without_leaking_body() -> None:
    config, work = fresh_config()

    async def handler(_request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            400,
            json={"error": {"message": "SENSITIVE_PROVIDER_BODY", "type": "invalid_request_error"}},
        )

    conversation = Conversation(config, "operation", "System", "incident", work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        with pytest.raises(ProviderError, match="HTTP 400"):
            await conversation.next([TOOL])
    finally:
        await conversation.close()

    assert config.ledger_path.exists()
    assert conversation.ledger.summary()["accounted_usd"] == "0"
    assert conversation.ledger.summary()["unconfirmed_calls"] == 0
    log_text = conversation.log_path.read_text(encoding="utf-8")
    assert "SENSITIVE_PROVIDER_BODY" not in log_text
    assert OPENAI_FAKE_KEY not in log_text


@pytest.mark.asyncio
async def test_timeout_keeps_full_reservation_across_ledger_restart() -> None:
    config, work = fresh_config()

    async def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("synthetic timeout", request=request)

    conversation = Conversation(config, "operation", "System", "incident", work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        with pytest.raises(ProviderError, match="HTTP None"):
            await conversation.next([TOOL])
    finally:
        await conversation.close()

    summary = conversation.ledger.summary()
    assert summary["unconfirmed_calls"] == 1
    assert Decimal(summary["accounted_usd"]) > 0
    from ccs.budget import BudgetLedger

    restarted = BudgetLedger(config.ledger_path, config.budget_usd).summary()
    assert restarted == summary


@pytest.mark.asyncio
async def test_completed_response_without_tool_is_a_billable_schema_error() -> None:
    config, work = fresh_config()

    async def handler(_request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=openai_response(call_id=None))

    conversation = Conversation(config, "operation", "System", "incident", work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        with pytest.raises(ProviderSchemaError):
            await conversation.next([TOOL])
    finally:
        await conversation.close()

    summary = conversation.ledger.summary()
    assert summary["unconfirmed_calls"] == 0
    assert Decimal(summary["accounted_usd"]) == Decimal("0.0000164")


@pytest.mark.asyncio
async def test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement() -> None:
    config, work = fresh_config()

    async def handler(_request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=openai_response(arguments="not-json"))

    conversation = Conversation(config, "operation", "System", "incident", work / "logs")
    await replace_openai_client(conversation, handler)
    try:
        with pytest.raises(ProviderSchemaError):
            await conversation.next([TOOL])
    finally:
        await conversation.close()

    summary = conversation.ledger.summary()
    assert summary["unconfirmed_calls"] == 0
    assert Decimal(summary["accounted_usd"]) == Decimal("0.0000164")


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:Pydantic serializer warnings:UserWarning")
async def test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement() -> None:
    config, work = fresh_config()

    async def handler(_request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=anthropic_response(tool_input="not-an-object"))

    conversation = Conversation(
        config,
        "diagnosis",
        "System",
        "incident",
        work / "logs",
        profile_override="sonnet5",
    )
    await replace_anthropic_client(conversation, handler)
    try:
        with pytest.raises(ProviderSchemaError):
            await conversation.next([TOOL])
    finally:
        await conversation.close()

    summary = conversation.ledger.summary()
    assert summary["unconfirmed_calls"] == 0
    assert Decimal(summary["accounted_usd"]) == Decimal("0.000479")


