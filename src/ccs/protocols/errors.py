"""Stable exceptions exposed by the protocol adapters."""


class ProtocolError(RuntimeError):
    """Base class for wire-protocol failures."""


class ProtocolAuthenticationError(ProtocolError):
    """The remote endpoint rejected the configured bearer token."""


class ProtocolCallError(ProtocolError):
    """A remote MCP tool returned an explicit tool error."""


class ProtocolTransportError(ProtocolError):
    """The protocol exchange could not complete."""


class A2ATaskError(ProtocolError):
    """An A2A task reached a non-success terminal state."""

