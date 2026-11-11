"""Portable defaults for mutable runtime data; environment overrides are explicit."""
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def working_root() -> Path:
    """Return subprocess scratch root without creating directories."""
    configured = os.environ.get("CCS_WORKING_ROOT")
    return Path(configured).expanduser().resolve() if configured else PROJECT_ROOT / "local-data" / "working"


def web_workspace() -> Path:
    """Return the web library/index root; explicit CLI --workspace takes priority."""
    configured = os.environ.get("CCS_WEB_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    if os.environ.get("CCS_WORKING_ROOT"):
        return working_root() / "web"
    return PROJECT_ROOT / "local-data" / "web"
