"""LAN mode retains the token, peer-network, Host and Origin boundaries."""
import ipaddress
from pathlib import Path
from types import SimpleNamespace

import pytest

from ccs.web_console import WebConsoleServer, _ConsoleHandler

PROJECT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("host,networks", [
    ("0.0.0.0", ("192.168.1.0/24",)),
    ("192.168.1.10", ()),
    ("192.168.1.10", ("0.0.0.0/0",)),
    ("10.20.30.40", ("10.0.0.0/8",)),
    ("169.254.1.2", ("169.254.1.0/24",)),
])
def test_lan_requires_specific_host_and_narrow_allowlist(tmp_path, host, networks):
    with pytest.raises(ValueError):
        WebConsoleServer(PROJECT/'configs/system.xml', PROJECT/'configs/ai.example.xml',
                         tmp_path, host=host, allowed_networks=networks)


def handler(peer="192.168.1.40", host="192.168.1.10:8123", token="test-capability", origin=None):
    h=object.__new__(_ConsoleHandler)
    h.console=SimpleNamespace(host="192.168.1.10", allowed_networks=(ipaddress.IPv4Network("192.168.1.0/24"),),
                              _token="test-capability", _server=SimpleNamespace(server_address=("192.168.1.10",8123)))
    h.client_address=(peer,23456)
    h.path="/api/console?token="+token
    h.headers={"Host":host}
    if origin is not None:h.headers["Origin"]=origin
    h.errors=[]
    h._error=lambda status,kind,message:h.errors.append((int(status),kind))
    return h


def test_lan_peer_and_exact_token_host_are_all_required():
    h=handler(); assert h._parsed() is not None and not h.errors
    for options,kind in [({"peer":"192.168.2.40"},"client_network"),
                         ({"host":"evil.example:8123"},"invalid_host"),
                         ({"token":"wrong"},"forbidden")]:
        h=handler(**options); assert h._parsed() is None
        assert h.errors==[(403,kind)]


def test_lan_post_requires_its_own_origin():
    h=handler(origin="http://evil.example")
    h.do_POST(); assert h.errors==[(403,"invalid_origin")]
    h=handler(origin="http://127.0.0.1:8123")
    h.do_POST(); assert h.errors==[(403,"invalid_origin")]
    h=handler(origin="http://192.168.1.10:8123")
    # Stop at the body reader: proves the legitimate origin passes that boundary.
    reached=[]
    h._read_payload=lambda:reached.append(True)
    h.do_POST(); assert reached==[True] and not h.errors

