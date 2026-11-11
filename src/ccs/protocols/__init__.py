"""Public wire-protocol adapters."""

from ccs.protocols.a2a import A2AClient, build_a2a_app
from ccs.protocols.errors import (
    A2ATaskError,
    ProtocolAuthenticationError,
    ProtocolCallError,
    ProtocolError,
    ProtocolTransportError,
)
from ccs.protocols.mcp import MCPClient, build_mcp_app

__all__ = [
    "A2AClient",
    "A2ATaskError",
    "MCPClient",
    "ProtocolAuthenticationError",
    "ProtocolCallError",
    "ProtocolError",
    "ProtocolTransportError",
    "build_a2a_app",
    "build_mcp_app",
]
