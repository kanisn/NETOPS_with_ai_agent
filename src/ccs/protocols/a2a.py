"""A2A SDK 1.1.5 JSON-RPC boundary for the Diagnosis Agent."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from a2a.client import ClientCallContext, ClientConfig, ClientFactory
from a2a.helpers import get_data_parts, new_data_part, new_task_from_user_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Message,
    HTTPAuthSecurityScheme,
    Role,
    SecurityRequirement,
    SecurityScheme,
    SendMessageConfiguration,
    SendMessageRequest,
    Task,
    TaskState,
    StringList,
)
from a2a.utils.constants import PROTOCOL_VERSION_CURRENT, TransportProtocol
from google.protobuf import json_format
from starlette.applications import Starlette
from starlette.middleware import Middleware

from ccs.contracts import DiagnosisRequest, DiagnosisResult
from ccs.protocols._auth import BearerTokenMiddleware
from ccs.protocols.errors import A2ATaskError, ProtocolCallError, ProtocolTransportError

A2AHandler = Callable[[dict[str, Any], dict[str, Any]], Awaitable[dict[str, Any]]]


def build_a2a_app(
    url: str,
    token: str,
    handler: A2AHandler,
    *,
    rpc_path: str = "/a2a",
    timeout_seconds: float = 30.0,
) -> Starlette:
    """Build the authenticated A2A JSON-RPC application and AgentCard.

    ``url`` is the public origin/base (for example ``http://127.0.0.1:8102``).
    The card is public at the standard well-known path and advertises
    ``url + rpc_path``. All task operations require the bearer token.
    """

    if not token:
        raise ValueError("A2A bearer token must not be empty")
    if not rpc_path.startswith("/"):
        raise ValueError("A2A rpc_path must start with '/'")

    interface_url = f"{url.rstrip('/')}{rpc_path}"
    card = AgentCard(
        name="CCS NetOps Diagnosis Agent",
        description="Read-only diagnosis and remediation proposal agent.",
        supported_interfaces=[
            AgentInterface(
                url=interface_url,
                protocol_binding=TransportProtocol.JSONRPC,
                protocol_version=PROTOCOL_VERSION_CURRENT,
            )
        ],
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        security_schemes={
            "bearerAuth": SecurityScheme(
                http_auth_security_scheme=HTTPAuthSecurityScheme(
                    scheme="bearer",
                    bearer_format="opaque",
                )
            )
        },
        security_requirements=[
            SecurityRequirement(schemes={"bearerAuth": StringList(list=[])})
        ],
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="diagnose_incident",
                name="Diagnose incident",
                description="Analyze incident evidence and propose a change without applying it.",
                tags=["netops", "diagnosis"],
                input_modes=["application/json"],
                output_modes=["application/json"],
            )
        ],
    )
    executor = _DiagnosisExecutor(handler, timeout_seconds=timeout_seconds)
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = [
        *create_agent_card_routes(card),
        *create_jsonrpc_routes(request_handler, rpc_url=rpc_path),
    ]
    app = Starlette(
        routes=routes,
        middleware=[
            Middleware(
                BearerTokenMiddleware,
                tokens={"operation": token},
                public_paths=("/.well-known/agent-card.json",),
            )
        ],
    )
    app.state.ccs_a2a_card = card
    app.state.ccs_a2a_executor = executor
    return app


class A2AClient:
    """Diagnosis-specific facade over the A2A 1.1.5 client."""

    def __init__(
        self,
        url: str,
        token: str,
        *,
        timeout_seconds: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if not token:
            raise ValueError("A2A bearer token must not be empty")
        self.url = url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client

    async def diagnose(
        self,
        payload: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request_payload = DiagnosisRequest.model_validate(payload).model_dump(mode="json")
        wire_metadata = dict(metadata or {})
        wire_metadata.setdefault("trace_id", request_payload["trace_id"])
        wire_metadata.setdefault("causation_event_id", None)

        message = Message(
            message_id=request_payload["message_id"],
            context_id=request_payload["trace_id"],
            role=Role.ROLE_USER,
            parts=[new_data_part(request_payload, media_type="application/json")],
            metadata=wire_metadata,
        )
        request = SendMessageRequest(
            message=message,
            configuration=SendMessageConfiguration(
                accepted_output_modes=["application/json"],
                return_immediately=False,
            ),
            metadata=wire_metadata,
        )

        owns_client = self._http_client is None
        http_client = self._http_client or httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self.timeout_seconds,
        )
        if not owns_client:
            http_client.headers["Authorization"] = f"Bearer {self.token}"

        try:
            config = ClientConfig(
                streaming=False,
                polling=False,
                httpx_client=http_client,
                supported_protocol_bindings=[TransportProtocol.JSONRPC],
                accepted_output_modes=["application/json"],
            )
            factory = ClientFactory(config)
            async with asyncio.timeout(self.timeout_seconds):
                client = await factory.create_from_url(self.url)
                final_task: Task | None = None
                async for response in client.send_message(
                    request,
                    context=ClientCallContext(timeout=self.timeout_seconds),
                ):
                    if response.HasField("task"):
                        final_task = response.task
                if final_task is None:
                    raise ProtocolCallError("A2A response did not contain a task")
                if final_task.status.state != TaskState.TASK_STATE_COMPLETED:
                    state_name = TaskState.Name(final_task.status.state)
                    raise A2ATaskError(f"A2A diagnosis ended in {state_name}")
                result = _diagnosis_artifact(final_task)
                return DiagnosisResult.model_validate(result).model_dump(mode="json")
        except (ProtocolCallError, A2ATaskError):
            raise
        except TimeoutError as exc:
            raise ProtocolTransportError("A2A diagnosis timed out") from exc
        except Exception as exc:
            raise ProtocolTransportError(f"A2A exchange failed: {type(exc).__name__}") from exc
        finally:
            if owns_client:
                await http_client.aclose()


class _DiagnosisExecutor(AgentExecutor):
    def __init__(self, handler: A2AHandler, *, timeout_seconds: float) -> None:
        self._handler = handler
        self._timeout_seconds = timeout_seconds
        self._lock = asyncio.Lock()
        self._calls: dict[str, tuple[str, asyncio.Task[dict[str, Any]]]] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message = context.message
        if message is None:
            raise ValueError("A2A diagnosis request has no message")

        task = new_task_from_user_message(message)
        await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()

        try:
            data_parts = get_data_parts(message.parts)
            if len(data_parts) != 1 or not isinstance(data_parts[0], dict):
                raise ValueError("A2A diagnosis requires exactly one JSON data part")
            request_model = DiagnosisRequest.model_validate(data_parts[0])
            request_payload = request_model.model_dump(mode="json")
            request_metadata = {
                **context.metadata,
                **json_format.MessageToDict(message.metadata),
                "protocol": "a2a",
                "a2a_task_id": task.id,
                "task_id": request_model.task_id,
                "trace_id": request_model.trace_id,
                "message_id": request_model.message_id,
                "idempotency_key": request_model.idempotency_key,
            }
            result = await self._idempotent_call(request_model.idempotency_key, request_payload, request_metadata)
            result_payload = DiagnosisResult.model_validate(result).model_dump(mode="json")
            await updater.add_artifact(
                [new_data_part(result_payload, media_type="application/json")],
                name="diagnosis-result",
                metadata={
                    "trace_id": request_model.trace_id,
                    "idempotency_key": request_model.idempotency_key,
                },
                last_chunk=True,
            )
            await updater.complete(
                updater.new_agent_message(
                    [new_text_part("Diagnosis completed.")],
                    metadata={"trace_id": request_model.trace_id},
                )
            )
        except Exception as exc:
            await updater.failed(
                updater.new_agent_message(
                    [new_text_part(f"Diagnosis failed: {type(exc).__name__}")]
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            updater = TaskUpdater(event_queue, context.task_id, context.context_id)
            await updater.cancel()

    async def _idempotent_call(
        self,
        idempotency_key: str,
        payload: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        async with self._lock:
            existing = self._calls.get(idempotency_key)
            if existing is not None:
                previous_digest, call = existing
                if previous_digest != digest:
                    raise ValueError("Idempotency key was reused with a different request")
            else:
                call = asyncio.create_task(self._invoke(payload, metadata))
                self._calls[idempotency_key] = (digest, call)
        return await asyncio.shield(call)

    async def _invoke(self, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        async with asyncio.timeout(self._timeout_seconds):
            result = await self._handler(payload, metadata)
        if not isinstance(result, dict):
            raise TypeError("A2A callback must return a dictionary")
        return result


def _diagnosis_artifact(task: Task) -> dict[str, Any]:
    for artifact in reversed(task.artifacts):
        values = get_data_parts(artifact.parts)
        for value in reversed(values):
            if isinstance(value, dict):
                return value
    raise ProtocolCallError("A2A completed task has no diagnosis-result data artifact")
