"""Isolated output paths and config fixtures for filesystem-writing tests."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET


def work_root(*, legacy_env: str | None = None) -> Path:
    """Return the selected test-output root, creating it outside the repository."""

    configured = os.environ.get("CCS_TEST_WORKING_ROOT")
    if not configured and legacy_env:
        configured = os.environ.get(legacy_env)
    root = Path(configured).expanduser() if configured else Path(tempfile.gettempdir()) / "ccs-testbed-tests"
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def workspace_for(module_name: str, *, legacy_env: str | None = None) -> Path:
    """Create and return one module-specific directory under the selected root."""

    if not isinstance(module_name, str) or not module_name or module_name in {".", ".."}:
        raise ValueError("module_name must be a non-empty directory name")
    if Path(module_name).name != module_name or "/" in module_name or "\\" in module_name:
        raise ValueError("module_name must be a single directory name")

    root = work_root(legacy_env=legacy_env)
    workspace = root / module_name
    workspace.mkdir(parents=True, exist_ok=True)
    resolved = workspace.resolve()
    if resolved.parent != root:
        raise ValueError("test workspace must stay directly under the configured test root")
    return resolved


def isolated_ai_config(module_name: str) -> Path:
    """Copy the public AI example with a cost ledger inside a module work folder."""

    workspace = workspace_for(module_name)
    source = Path(__file__).resolve().parents[1] / "configs" / "ai.example.xml"
    destination = workspace / "ai.test.xml"
    tree = ET.parse(source)
    budget = tree.getroot().find("budget")
    if budget is None:
        raise ValueError("AI example configuration is missing its budget section")
    budget.set("ledger_path", str((workspace / "cost-ledger.sqlite").resolve()))
    tree.write(destination, encoding="utf-8", xml_declaration=True)
    return destination
