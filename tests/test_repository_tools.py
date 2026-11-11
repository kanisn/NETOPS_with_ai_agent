"""Publication checks must examine Git's actual index and preserve private files."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repository_checker(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    spec = importlib.util.spec_from_file_location("publication_check", PROJECT / "tools/check_repository.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    return checker, tmp_path


def test_public_candidates_exclude_private_configuration(repository_checker):
    checker, root = repository_checker
    (root / ".gitignore").write_text("configs/ai.local.xml\nruns/\n", encoding="utf-8")
    (root / "README.md").write_text("# Public source\n", encoding="utf-8")
    (root / "configs").mkdir()
    private = root / "configs/ai.local.xml"
    private.write_text("private content", encoding="utf-8")
    before = private.read_bytes()
    result = checker.audit()
    assert result["passed"]
    assert private.read_bytes() == before
    assert "configs/ai.local.xml" not in checker.git_files()


def test_staged_blob_is_scanned_even_after_working_file_is_cleaned(repository_checker):
    checker, root = repository_checker
    fake_key = "sk-proj-" + "A" * 48
    path = root / "README.md"
    path.write_text("# Test sentinel\n" + fake_key, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True, capture_output=True)
    path.write_text("# Sanitized working copy\n", encoding="utf-8")
    result = checker.audit(staged=True)
    assert not result["passed"]
    assert any(item["kind"] == "possible_openai_or_anthropic_key" for item in result["issues"])
    assert fake_key not in json.dumps(result)
    assert checker.audit()["passed"]


def test_link_to_an_ignored_local_file_is_not_publishable(repository_checker):
    checker, root = repository_checker
    (root / ".gitignore").write_text("configs/ai.local.xml\n", encoding="utf-8")
    (root / "configs").mkdir()
    (root / "configs/ai.local.xml").write_text("private content", encoding="utf-8")
    (root / "README.md").write_text("# Guide\n[local settings](configs/ai.local.xml)\n", encoding="utf-8")
    result = checker.audit()
    assert any(item["kind"] == "markdown_link_not_in_public_files" for item in result["issues"])
