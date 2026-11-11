"""Explicit contract failures raised by NetworkBackend implementations."""


class BackendError(RuntimeError):
    """Base class for backend failures."""


class ContractError(BackendError, ValueError):
    """A tool call did not satisfy its declared schema."""


class UnknownToolError(ContractError):
    """The requested tool is outside the stable tool contract."""


class NotFoundError(BackendError):
    """A requested network entity, preview, change, or ticket does not exist."""


class VersionConflictError(BackendError):
    """A preview or rollback was based on stale network state."""


class IdempotencyConflictError(BackendError):
    """An idempotency key was reused for a different request."""


class ChangeConflictError(BackendError):
    """A valid object cannot be changed in its current lifecycle state."""
