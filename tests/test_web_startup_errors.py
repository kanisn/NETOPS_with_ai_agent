"""CLI messages for web-listener failures must distinguish bind from setup."""

from __future__ import annotations

from pathlib import Path

import pytest

import ccs.cli as cli
import ccs.web_console as web_console
from ccs.web_console import WebConsoleBindError, WebConsoleServer


PROJECT = Path(__file__).resolve().parents[1]


_windows_bind_denied = OSError(13, "private sentinel")
_windows_bind_denied.winerror = 10013


@pytest.mark.parametrize(
    ("os_error", "expected"),
    [
        (OSError(10048, "private sentinel"), "address already in use"),
        (_windows_bind_denied, "binding denied; the port may already be in use or reserved"),
        (OSError(98, "private sentinel"), "address already in use"),
        (PermissionError(13, "private sentinel"), "permission denied"),
    ],
)
def test_start_converts_only_listener_bind_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, os_error: OSError, expected: str
) -> None:
    server = WebConsoleServer(
        PROJECT / "configs/system.xml",
        PROJECT / "configs/ai.example.xml",
        tmp_path / "workspace",
        port=49690,
    )

    def fail_bind(*_args: object, **_kwargs: object) -> None:
        raise os_error

    monkeypatch.setattr(web_console, "_ConsoleHTTPServer", fail_bind)
    with pytest.raises(WebConsoleBindError) as caught:
        server.start()

    assert caught.value.reason == expected
    assert (caught.value.host, caught.value.port) == ("127.0.0.1", 49690)
    assert "private sentinel" not in str(caught.value)


def test_workspace_permission_error_is_not_a_bind_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def denied_workspace(_path: Path, *_args: object, **_kwargs: object) -> Path:
        raise PermissionError(13, "workspace denied")

    monkeypatch.setattr(web_console, "_safe_directory", denied_workspace)
    with pytest.raises(PermissionError, match="workspace denied"):
        WebConsoleServer(
            PROJECT / "configs/system.xml",
            PROJECT / "configs/ai.example.xml",
            tmp_path / "workspace",
            port=49690,
        )


@pytest.mark.parametrize("port", [49690, 0])
def test_cli_reports_bind_failure_without_fallback_or_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], port: int
) -> None:
    requested: list[tuple[str, int]] = []

    class FakeServer:
        def __init__(self, *_args: object, port: int, host: str, **_kwargs: object):
            requested.append((host, port))

        def start(self) -> None:
            raise WebConsoleBindError(
                "127.0.0.1", port, OSError(10048, "secret-token-sentinel")
            )

    monkeypatch.setattr(web_console, "WebConsoleServer", FakeServer)
    status = cli.main(
        [
            "web",
            "--workspace",
            str(tmp_path / "workspace"),
            "--port",
            str(port),
            "--no-browser",
        ]
    )

    output = capsys.readouterr().out
    assert status == 1
    assert requested == [("127.0.0.1", port)]
    assert f"127.0.0.1:{port}" in output
    assert "address already in use" in output
    assert "socket error 10048" in output
    assert "secret-token-sentinel" not in output
    if port:
        assert "--port 0" in output
    else:
        assert "another free port" in output

