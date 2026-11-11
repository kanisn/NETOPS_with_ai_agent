"""Backend-neutral interface used by Network Tools handlers."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class NetworkBackend(Protocol):
    """Stateful backend contract; concrete storage is deliberately hidden."""

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]: ...

    def snapshot(self) -> dict[str, Any]: ...

    def close(self) -> None: ...
