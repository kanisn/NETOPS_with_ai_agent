"""Small ASGI bearer-token middleware shared by the local protocols."""

from __future__ import annotations

import hmac
from collections.abc import Mapping, Sequence

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class BearerTokenMiddleware:
    """Reject unknown bearer tokens before requests enter a protocol SDK."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        tokens: Mapping[str, str],
        public_paths: Sequence[str] = (),
    ) -> None:
        self.app = app
        self._tokens = dict(tokens)
        self._public_paths = frozenset(public_paths)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path", "") in self._public_paths:
            await self.app(scope, receive, send)
            return

        supplied = _bearer_value(Headers(scope=scope).get("authorization"))
        role = _match_token(supplied, self._tokens)
        if role is None:
            response = JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        scope.setdefault("state", {})["ccs_role"] = role
        await self.app(scope, receive, send)


def role_from_headers(headers: Mapping[str, str] | None, tokens: Mapping[str, str]) -> str | None:
    authorization = headers.get("authorization") if headers is not None else None
    return _match_token(_bearer_value(authorization), tokens)


def _bearer_value(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, separator, value = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer" or not value:
        return None
    return value


def _match_token(supplied: str | None, tokens: Mapping[str, str]) -> str | None:
    if supplied is None:
        return None
    for role, expected in tokens.items():
        if hmac.compare_digest(supplied, expected):
            return role
    return None

