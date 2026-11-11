import json
from pathlib import Path

from ccs.web_console import WebConsoleServer


PROJECT = Path(__file__).resolve().parents[1]


def test_old_catalog_is_archived_once_and_never_reused_for_new_runs(tmp_path):
    workspace = tmp_path / "console"
    workspace.mkdir()
    legacy = {"version": 1, "documents": [{"id": "a" * 32, "kind": "memory", "title": "Old domain",
              "content": "legacy evidence", "selected": True}],
              "runs": [{"run_id": "old-domain-run", "status": "COMPLETED"}], "active": None}
    state = workspace / "console-state.json"
    state.write_text(json.dumps(legacy), encoding="utf-8")
    with WebConsoleServer(PROJECT / "configs/system.xml", PROJECT / "configs/ai.example.xml", workspace) as server:
        public = server.console_state()
        assert public["runs"] == []
        assert public["library"]["memory"] == []
        assert public["library"]["runbooks"]
        assert set(public["options"]["faults"]) == {"W1", "W2", "W3", "W4", "W5", "N0"}
        assert all("legacy evidence" not in d["content"] for d in public["library"]["runbooks"])
        archive = Path(server._state["previous_catalog_archive"])
        assert json.loads(archive.read_text(encoding="utf-8")) == legacy
        runbook_ids = [d["id"] for d in public["library"]["runbooks"]]
    with WebConsoleServer(PROJECT / "configs/system.xml", PROJECT / "configs/ai.example.xml", workspace) as server:
        assert [d["id"] for d in server.console_state()["library"]["runbooks"]] == runbook_ids
        assert len(list((workspace / "archive").glob("*.json"))) == 1


def test_legacy_scenario_and_target_are_rejected(tmp_path):
    from ccs.bench.scenarios import create_world
    import pytest
    with pytest.raises(ValueError):
        create_world(tmp_path / "legacy-scenario.sqlite", fault_id="F4")
    with pytest.raises(ValueError):
        create_world(tmp_path / "legacy-target.sqlite", fault_id="W4", target="CELL-001")
