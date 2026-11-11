"""Repository documentation must not become Agent runbook input."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from ccs.knowledge.stores import RunbookStore, runbook_files
from ccs.paths import working_root, web_workspace
from ccs.runner import snapshot_runbooks
from ccs.web_console import WebConsoleServer

PROJECT = Path(__file__).resolve().parents[1]


def test_readme_is_excluded_from_discovery_snapshot_and_search(tmp_path):
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "README.md").write_text("# Human-only documentation\nUnrelated index text", encoding="utf-8")
    nested = catalog / "nested"
    nested.mkdir()
    (nested / "readme.md").write_text("# Another folder guide", encoding="utf-8")
    runbook = nested / "recovery.md"
    runbook.write_text("---\ndoc_id: RB-TEST\nversion: 1\ntenant: synthetic-tenant\nclassification: internal\nsource: test\n---\n# Recovery\nRestore bandwidth after verification.\n", encoding="utf-8")
    assert runbook_files(catalog) == [runbook]
    snapshots = snapshot_runbooks(catalog, tmp_path / "snapshot")
    assert [item["path"] for item in snapshots] == ["nested/recovery.md"]
    store = RunbookStore(tmp_path / "runbooks.sqlite", catalog)
    try:
        assert len(store.search("bandwidth")) == 1
        assert store.search("Human-only") == []
    finally:
        store.close()


def test_web_catalog_loads_six_runbooks_with_folder_readme(tmp_path):
    tree = ET.parse(PROJECT / "configs/system.example.xml")
    tree.find("paths").set("output_root", str(tmp_path / "runs"))
    config = tmp_path / "system.xml"
    tree.write(config, encoding="utf-8")
    workspace = tmp_path / "web"
    WebConsoleServer(config, PROJECT / "configs/ai.example.xml", workspace)
    state = json.loads((workspace / "console-state.json").read_text(encoding="utf-8"))
    books = [item for item in state["documents"] if item["kind"] == "runbooks"]
    assert len(books) == 6
    assert all(item["source_name"].casefold() != "readme.md" for item in books)


def test_runtime_paths_use_explicit_environment_without_creating_files(tmp_path, monkeypatch):
    monkeypatch.setenv("CCS_WORKING_ROOT", str(tmp_path / "work"))
    monkeypatch.delenv("CCS_WEB_WORKSPACE", raising=False)
    assert working_root() == tmp_path / "work"
    assert web_workspace() == tmp_path / "work" / "web"
    monkeypatch.setenv("CCS_WEB_WORKSPACE", str(tmp_path / "separate-web"))
    assert web_workspace() == tmp_path / "separate-web"
    assert not (tmp_path / "work").exists()
