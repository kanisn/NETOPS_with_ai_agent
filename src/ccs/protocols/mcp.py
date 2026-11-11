"""MCP 2.2.0 Streamable HTTP boundary for backend-neutral NetOps tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any

import httpx2
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client
from mcp.server.context import ServerRequestContext
from mcp.server.lowlevel import Server
from starlette.applications import Starlette
from starlette.middleware import Middleware

from ccs.protocols._auth import BearerTokenMiddleware, role_from_headers
from ccs.protocols.errors import ProtocolCallError, ProtocolTransportError

MCPHandler = Callable[[str, dict[str, Any], dict[str, Any]], Awaitable[dict[str, Any]]]


def build_mcp_app(
    schemas_by_role: Mapping[str, Sequence[dict[str, Any]]],
    tokens: Mapping[str, str],
    handler: MCPHandler,
    *,
    path: str = "/mcp",
) -> Starlette:
    """Build an authenticated MCP 2.2.0 Streamable HTTP application.

    ``tokens`` maps the roles ``operation`` and ``diagnosis`` to bearer tokens.
    Tool definitions are role-specific, and the same role check is repeated at
    call time so a hidden change tool cannot be invoked by name.
    """

    token_map = _validate_tokens(tokens)
    tools_by_role, validators_by_role = _compile_schemas(schemas_by_role)

    async def list_tools(
        ctx: ServerRequestContext[Any, Any],
        _params: types.PaginatedRequestParams | None,
    ) -> types.ListToolsResult:
        role = _require_role(ctx, token_map)
        return types.ListToolsResult(tools=tools_by_role.get(role, []))

    async def call_tool(
        ctx: ServerRequestContext[Any, Any],
        params: types.CallToolRequestParams,
    ) -> types.CallToolResult:
        role = _require_role(ctx, token_map)
        validator = validators_by_role.get(role, {}).get(params.name)
        if validator is None:
            return _tool_error("tool_not_allowed", f"Tool {params.name!r} is not available for role {role!r}.")

        arguments = dict(params.arguments or {})
        try:
            validator.validate(arguments)
        except ValidationError as exc:
            location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
            return _tool_error("invalid_arguments", f"Invalid arguments at {location}.")

        incoming_meta = dict(params.meta or {})
        metadata = {
            **incoming_meta,
            "protocol": "mcp",
            "role": role,
            "protocol_call_id": str(ctx.request_id),
        }
        try:
            result = await handler(params.name, arguments, metadata)
            if not isinstance(result, dict):
                raise TypeError("MCP callback must return a dictionary")
        except Exception as exc:  # the client receives an explicit tool failure
            return _tool_error("handler_error", f"{type(exc).__name__}: {exc}")

        return types.CallToolResult(
            content=[types.TextContent(text=json.dumps(result, sort_keys=True, ensure_ascii=False))],
            structuredContent=result,
            isError=False,
        )

    server = Server(
        "ccs-netops-tools",
        version="1.0.0",
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )
    app = server.streamable_http_app(
        streamable_http_path=path,
        json_response=True,
        stateless_http=True,
        host="127.0.0.1",
    )
    app.user_middleware.insert(0, Middleware(BearerTokenMiddleware, tokens=token_map))
    app.middleware_stack = None
    app.state.ccs_mcp_server = server
    return app


class MCPClient:
    """Small one-request-at-a-time MCP client used by both agents."""

    def __init__(
        self,
        url: str,
        token: str,
        *,
        timeout_seconds: float = 15.0,
        http_client: httpx2.AsyncClient | None = None,
    ) -> None:
        if not token:
            raise ValueError("MCP bearer token must not be empty")
        self.url = url
        self.token = token
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client

    async def list_tools(self) -> list[dict[str, Any]]:
        async def operation(session: ClientSession) -> list[dict[str, Any]]:
            response = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                }
                for tool in response.tools
            ]

        return await self._exchange(operation)

    async def call(
        self,
        tool: str,
        arguments: dict[str, Any] | None = None,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async def operation(session: ClientSession) -> dict[str, Any]:
            response = await session.call_tool(
                tool,
                arguments or {},
                read_timeout_seconds=self.timeout_seconds,
                meta=metadata or {},
            )
            if not isinstance(response, types.CallToolResult):
                raise ProtocolCallError(f"MCP tool {tool!r} did not return a completed result")
            if response.is_error:
                message = _first_text(response) or f"MCP tool {tool!r} failed"
                raise ProtocolCallError(message)
            result = response.structured_content
            if result is None:
                text = _first_text(response)
                try:
                    result = json.loads(text) if text else None
                except json.JSONDecodeError as exc:
                    raise ProtocolCallError(f"MCP tool {tool!r} returned invalid JSON") from exc
            if not isinstance(result, dict):
                raise ProtocolCallError(f"MCP tool {tool!r} returned a non-object result")
            return result

        return await self._exchange(operation)

    async def _exchange(self, operation: Callable[[ClientSession], Awaitable[Any]]) -> Any:
        owns_client = self._http_client is None
        client = self._http_client or httpx2.AsyncClient(
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self.timeout_seconds,
        )
        if not owns_client:
            client.headers["Authorization"] = f"Bearer {self.token}"
        try:
            call_error: ProtocolCallError | None = None
            value: Any = None
            async with asyncio.timeout(self.timeout_seconds):
                async with streamable_http_client(self.url, http_client=client) as streams:
                    async with ClientSession(*streams, read_timeout_seconds=self.timeout_seconds) as session:
                        await session.initialize()
                        try:
                            value = await operation(session)
                        except ProtocolCallError as exc:
                            # Let both SDK context managers shut down normally. Raising
                            # inside their AnyIO task groups wraps this domain error in
                            # an ExceptionGroup and obscures the tool failure.
                            call_error = exc
            if call_error is not None:
                raise call_error
            return value
        except ProtocolCallError:
            raise
        except TimeoutError as exc:
            raise ProtocolTransportError("MCP request timed out") from exc
        except Exception as exc:
            raise ProtocolTransportError(f"MCP exchange failed: {type(exc).__name__}") from exc
        finally:
            if owns_client:
                await client.aclose()


def _validate_tokens(tokens: Mapping[str, str]) -> dict[str, str]:
    token_map = dict(tokens)
    if set(token_map) != {"operation", "diagnosis"}:
        raise ValueError("MCP tokens must define exactly operation and diagnosis roles")
    if any(not value for value in token_map.values()) or len(set(token_map.values())) != len(token_map):
        raise ValueError("MCP bearer tokens must be non-empty and unique")
    return token_map


def _compile_schemas(
    schemas_by_role: Mapping[str, Sequence[dict[str, Any]]],
) -> tuple[dict[str, list[types.Tool]], dict[str, dict[str, Draft202012Validator]]]:
    tools_by_role: dict[str, list[types.Tool]] = {}
    validators_by_role: dict[str, dict[str, Draft202012Validator]] = {}
    for role in ("operation", "diagnosis"):
        tools: list[types.Tool] = []
        validators: dict[str, Draft202012Validator] = {}
        for schema in schemas_by_role.get(role, []):
            name = schema.get("name")
            parameters = schema.get("parameters")
            if not isinstance(name, str) or not name or not isinstance(parameters, dict):
                raise ValueError(f"Invalid MCP tool schema for role {role!r}")
            if name in validators:
                raise ValueError(f"Duplicate MCP tool {name!r} for role {role!r}")
            try:
                Draft202012Validator.check_schema(parameters)
            except SchemaError as exc:
                raise ValueError(f"Invalid JSON Schema for MCP tool {name!r}") from exc
            validators[name] = Draft202012Validator(parameters)
            tools.append(
                types.Tool(
                    name=name,
                    description=str(schema.get("description", "")),
                    inputSchema=parameters,
                )
            )
        tools_by_role[role] = tools
        validators_by_role[role] = validators
    return tools_by_role, validators_by_role


def _require_role(ctx: ServerRequestContext[Any, Any], tokens: Mapping[str, str]) -> str:
    request = ctx.request
    headers = getattr(request, "headers", None)
    role = role_from_headers(headers, tokens)
    if role is None:
        raise PermissionError("Valid bearer authentication is required")
    return role


def _tool_error(code: str, message: str) -> types.CallToolResult:
    payload = {"error": {"code": code, "message": message}}
    return types.CallToolResult(
        content=[types.TextContent(text=json.dumps(payload, sort_keys=True))],
        structuredContent=payload,
        isError=True,
    )


def _first_text(result: types.CallToolResult) -> str:
    for item in result.content:
        if isinstance(item, types.TextContent):
            return item.text
    return ""
