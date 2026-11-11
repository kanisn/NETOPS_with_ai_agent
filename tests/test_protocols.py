from __future__ import annotations

import asyncio
from importlib.metadata import version

import httpx
import httpx2
import pytest
from a2a.client import ClientCallContext, ClientConfig, ClientFactory
from a2a.helpers import new_data_part
from a2a.types import Message, Role, SendMessageConfiguration, SendMessageRequest, Task, TaskState
from a2a.utils.constants import TransportProtocol

from ccs.protocols import (
    A2AClient,
    A2ATaskError,
    MCPClient,
    ProtocolCallError,
    ProtocolTransportError,
    build_a2a_app,
    build_mcp_app,
)


@pytest.mark.asyncio
async def test_mcp_real_wire_enforces_role_schema_and_metadata() -> None:
    assert version("mcp") == "2.2.0"
    calls: list[tuple[str, dict, dict]] = []

    async def handler(tool: str, arguments: dict, metadata: dict) -> dict:
        calls.append((tool, arguments, metadata))
        return {"tool": tool, "target": arguments["target"]}

    read_schema = {
        "name": "get_config",
        "description": "Read configuration.",
        "parameters": {
            "type": "object",
            "properties": {"target": {"type": "string"}},
            "required": ["target"],
            "additionalProperties": False,
        },
    }
    change_schema = {
        "name": "apply_change",
        "description": "Apply a previewed change.",
        "parameters": {
            "type": "object",
            "properties": {"target": {"type": "string"}},
            "required": ["target"],
            "additionalProperties": False,
        },
    }
    app = build_mcp_app(
        {
            "operation": [read_schema, change_schema],
            "diagnosis": [read_schema],
        },
        {"operation": "operation-token", "diagnosis": "diagnosis-token"},
        handler,
    )

    transport = httpx2.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:8000") as wire_client:
            diagnosis = MCPClient(
                "http://localhost:8000/mcp",
                "diagnosis-token",
                http_client=wire_client,
            )
            operation = MCPClient(
                "http://localhost:8000/mcp",
                "operation-token",
                http_client=wire_client,
            )

            assert [tool["name"] for tool in await diagnosis.list_tools()] == ["get_config"]
            assert [tool["name"] for tool in await operation.list_tools()] == [
                "get_config",
                "apply_change",
            ]

            result = await diagnosis.call(
                "get_config",
                {"target": "HOST-001"},
                metadata={"trace_id": "trace-1", "causation_event_id": "event-1"},
            )
            assert result == {"tool": "get_config", "target": "HOST-001"}
            assert calls[0][2]["role"] == "diagnosis"
            assert calls[0][2]["trace_id"] == "trace-1"
            assert calls[0][2]["causation_event_id"] == "event-1"
            assert calls[0][2]["protocol_call_id"]

            with pytest.raises(ProtocolCallError, match="not available"):
                await diagnosis.call("apply_change", {"target": "HOST-001"})
            with pytest.raises(ProtocolCallError, match="Invalid arguments"):
                await operation.call("get_config", {})
            with pytest.raises(ProtocolCallError, match="Invalid arguments"):
                await operation.call(
                    "get_config",
                    {"target": "HOST-001", "unexpected": "rejected"},
                )


@pytest.mark.asyncio
async def test_mcp_bad_token_is_rejected_on_real_transport() -> None:
    async def handler(_tool: str, _arguments: dict, _metadata: dict) -> dict:
        return {}

    schema = {
        "name": "ping_tool",
        "description": "Test tool.",
        "parameters": {"type": "object", "additionalProperties": False},
    }
    app = build_mcp_app(
        {"operation": [schema], "diagnosis": [schema]},
        {"operation": "operation-token", "diagnosis": "diagnosis-token"},
        handler,
    )
    transport = httpx2.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:8000") as wire_client:
            client = MCPClient("http://localhost:8000/mcp", "wrong-token", http_client=wire_client)
            with pytest.raises(ProtocolTransportError):
                await client.list_tools()


def _diagnosis_payload(*, idempotency_key: str = "idem-1", target: str = "HOST-001") -> dict:
    return {
        "schema_version": "diagnosis@1",
        "task_id": "domain-task-1",
        "trace_id": "trace-1",
        "message_id": "message-1",
        "idempotency_key": idempotency_key,
        "incident": {"summary": "Video calls are dropping.", "targets": [target]},
        "context": {"runbook_refs": ["RB-QOS-01"]},
        "constraints": {"tool_budget": 8},
    }


@pytest.mark.asyncio
async def test_a2a_real_agent_card_task_lifecycle_and_idempotency() -> None:
    assert version("a2a-sdk") == "1.1.5"
    invocations: list[tuple[dict, dict]] = []

    async def handler(payload: dict, metadata: dict) -> dict:
        invocations.append((payload, metadata))
        return {
            "root_cause": "bandwidth_limit_misconfiguration",
            "evidence": [{"source": "get_config", "param": "bandwidth_mbps", "current": 20, "reference": 100}],
            "proposed_change": {
                "target": "HOST-001",
                "param": "bandwidth_mbps",
                "value": 100,
                "reason": "Restore the documented QoS profile.",
            },
            "confidence": 0.9,
            "notes": "Read-only diagnosis.",
        }

    app = build_a2a_app("http://localhost", "a2a-token", handler)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as wire_client:
        client = A2AClient("http://localhost", "a2a-token", http_client=wire_client)
        first = await client.diagnose(
            _diagnosis_payload(),
            metadata={"causation_event_id": "event-9"},
        )
        second = await client.diagnose(
            _diagnosis_payload(),
            metadata={"causation_event_id": "event-9"},
        )

        assert first == second
        assert first["root_cause"] == "bandwidth_limit_misconfiguration"
        assert first["proposed_change"]["target"] == "HOST-001"
        assert len(invocations) == 1
        assert invocations[0][1]["protocol"] == "a2a"
        assert invocations[0][1]["task_id"] == "domain-task-1"
        assert invocations[0][1]["trace_id"] == "trace-1"
        assert invocations[0][1]["causation_event_id"] == "event-9"
        assert invocations[0][1]["a2a_task_id"]

        card_response = await wire_client.get("/.well-known/agent-card.json")
        assert card_response.status_code == 200
        assert card_response.json()["skills"][0]["id"] == "diagnose_incident"
        assert "bearerAuth" in card_response.json()["securitySchemes"]


@pytest.mark.asyncio
async def test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire() -> None:
    invocations = 0

    async def handler(_payload: dict, _metadata: dict) -> dict:
        nonlocal invocations
        invocations += 1
        return {
            "root_cause": "unused",
            "evidence": [],
            "proposed_change": None,
            "confidence": 0.5,
            "notes": "",
        }

    app = build_a2a_app("http://localhost", "a2a-token", handler)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
        headers={"Authorization": "Bearer a2a-token"},
    ) as wire_client:
        payload = _diagnosis_payload()
        payload["unexpected"] = "rejected"
        task = await _send_raw_a2a(wire_client, payload)
        assert task.status.state == TaskState.TASK_STATE_FAILED
        assert invocations == 0


@pytest.mark.asyncio
async def test_a2a_rejects_idempotency_key_payload_mismatch() -> None:
    async def handler(payload: dict, _metadata: dict) -> dict:
        return {
            "root_cause": "test",
            "evidence": [],
            "proposed_change": None,
            "confidence": 0.5,
            "notes": payload["incident"]["summary"],
        }

    app = build_a2a_app("http://localhost", "a2a-token", handler)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as wire_client:
        client = A2AClient("http://localhost", "a2a-token", http_client=wire_client)
        await client.diagnose(_diagnosis_payload())
        changed = _diagnosis_payload(target="HOST-002")
        with pytest.raises(A2ATaskError, match="TASK_STATE_FAILED"):
            await client.diagnose(changed)


@pytest.mark.asyncio
async def test_a2a_callback_timeout_reaches_failed_terminal_state() -> None:
    async def handler(_payload: dict, _metadata: dict) -> dict:
        await asyncio.sleep(0.2)
        return {"root_cause": "late"}

    app = build_a2a_app(
        "http://localhost",
        "a2a-token",
        handler,
        timeout_seconds=0.01,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as wire_client:
        client = A2AClient(
            "http://localhost",
            "a2a-token",
            timeout_seconds=1.0,
            http_client=wire_client,
        )
        with pytest.raises(A2ATaskError, match="TASK_STATE_FAILED"):
            await client.diagnose(_diagnosis_payload())


@pytest.mark.asyncio
async def test_a2a_bad_token_cannot_send_task() -> None:
    async def handler(_payload: dict, _metadata: dict) -> dict:
        return {
            "root_cause": "unused",
            "evidence": [],
            "proposed_change": None,
            "confidence": 0.5,
            "notes": "",
        }

    app = build_a2a_app("http://localhost", "a2a-token", handler)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as wire_client:
        client = A2AClient("http://localhost", "wrong-token", http_client=wire_client)
        with pytest.raises(ProtocolTransportError):
            await client.diagnose(_diagnosis_payload())


async def _send_raw_a2a(http_client: httpx.AsyncClient, payload: dict) -> Task:
    """Send a deliberately unvalidated payload through the pinned A2A SDK."""

    factory = ClientFactory(
        ClientConfig(
            streaming=False,
            polling=False,
            httpx_client=http_client,
            supported_protocol_bindings=[TransportProtocol.JSONRPC],
            accepted_output_modes=["application/json"],
        )
    )
    client = await factory.create_from_url("http://localhost")
    request = SendMessageRequest(
        message=Message(
            message_id="raw-message-1",
            context_id="raw-trace-1",
            role=Role.ROLE_USER,
            parts=[new_data_part(payload, media_type="application/json")],
        ),
        configuration=SendMessageConfiguration(
            accepted_output_modes=["application/json"],
            return_immediately=False,
        ),
    )
    final_task: Task | None = None
    async for response in client.send_message(request, context=ClientCallContext(timeout=1.0)):
        if response.HasField("task"):
            final_task = response.task
    assert final_task is not None
    return final_task
