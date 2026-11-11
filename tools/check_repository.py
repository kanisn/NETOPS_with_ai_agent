"""Read-only Git publication preflight. Findings never print credential values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".ps1", ".xml", ".toml", ".lock", ".yml", ".yaml", ".json", ".txt", ".js", ".css", ".html"}
PRIVATE_PARTS = {"__pycache__", ".pytest_cache", ".venv", "venv", "local-data", "runs", "outputs", "logs", "build", "dist", ".idea", ".vs"}
PRIVATE_NAMES = {"ai.local.xml", "system.xml", ".ccs-python"}
PATTERNS = {
    "possible_openai_or_anthropic_key": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}\b"),
    "possible_github_token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{25,}|gh[pousr]_[A-Za-z0-9]{25,})\b"),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "live_local_capability_url": re.compile(r"https?://(?:127\.0\.0\.1|localhost):\d+/[^\s]*[?&]token=[A-Za-z0-9_-]{24,}"),
}
LINK = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+\"[^\"]*\")?\)")


def git_files(staged: bool = False) -> list[str]:
    """List only Git-eligible paths, without staging or changing any file."""
    args = ["git", "-C", str(ROOT), "ls-files", "-z", "--cached"]
    if not staged:
        args += ["--others", "--exclude-standard"]
    process = subprocess.run(args, capture_output=True, check=False)
    if process.returncode:
        raise RuntimeError("Git repository information is unavailable; run this inside a clone or initialized repository")
    return sorted(set(value for value in process.stdout.decode("utf-8", "surrogateescape").split("\0") if value))


def markdown_without_code(text: str) -> str:
    return re.sub(r"(?ms)^\s*```.*?^\s*```\s*$", "", text)


def markdown_anchors(text: str) -> set[str]:
    """Recognize explicit IDs and the common GitHub heading-slug convention."""
    result = set(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)', text))
    counts = {}
    for line in markdown_without_code(text).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        label = re.sub(r"<[^>]+>", "", match.group(1))
        slug = re.sub(r"[^\w\-\s]", "", label.lower()).strip().replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f"-{count}" if count else ""))
    return result


def audit(staged: bool = False) -> dict:
    files = git_files(staged)
    available = set(files)
    issues = []
    warnings = []
    text_cache = {}

    def content(relative: str) -> bytes:
        if staged:
            result = subprocess.run(["git", "-C", str(ROOT), "show", ":" + relative], capture_output=True, check=False)
            if result.returncode:
                raise OSError("Index content unavailable")
            return result.stdout
        return (ROOT / relative).read_bytes()

    def finding(kind: str, path: str, line: int | None = None, detail: str | None = None) -> None:
        item = {"kind": kind, "path": path}
        if line is not None:
            item["line"] = line
        if detail is not None:
            item["detail"] = detail
        issues.append(item)

    for relative in files:
        path = ROOT / relative
        if not staged and (not path.exists() or not path.is_file()):
            finding("missing_or_nonfile_candidate", relative)
            continue
        if not path.resolve().is_relative_to(ROOT.resolve()):
            finding("candidate_escapes_repository", relative)
            continue
        name = path.name.casefold()
        if any(part.casefold() in PRIVATE_PARTS for part in path.relative_to(ROOT).parts) or name in PRIVATE_NAMES or name.endswith(".local.xml") or (name.startswith(".env") and name not in {".env.example", ".env.template"}):
            finding("private_or_generated_file_is_git_eligible", relative)
            # Do not open a credential file, even if it was accidentally staged.
            continue
        if path.suffix.lower() in {".sqlite", ".sqlite3", ".db", ".pem", ".pfx", ".p12", ".key", ".pyc", ".log", ".pid"} or name.endswith(".writing") or re.search(r"\.(?:db|sqlite\d*)(?:-(?:wal|shm|journal))$", name):
            finding("runtime_or_sensitive_file_is_git_eligible", relative)
            continue
        try:
            raw = content(relative)
        except OSError:
            finding("candidate_unreadable", relative)
            continue
        if len(raw) > 10 * 1024 * 1024:
            warnings.append({"kind": "large_candidate_over_10MiB", "path": relative})
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".gitignore", ".gitattributes"}:
            continue
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            finding("non_utf8_text_file", relative)
            continue
        text_cache[relative] = text
        for number, line in enumerate(text.splitlines(), 1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    finding(name, relative, number)
            if re.search(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", line):
                finding("personal_machine_path", relative, number)
        if path.suffix.lower() == ".xml":
            try:
                tree = ET.fromstring(text)
            except ET.ParseError:
                finding("invalid_example_xml", relative)
            else:
                if any((node.text or "").strip() for node in tree.iter("api_key")):
                    finding("nonempty_api_key_in_public_xml", relative)

    link_count = 0
    for relative, text in text_cache.items():
        if not relative.lower().endswith(".md"):
            continue
        for match in LINK.finditer(markdown_without_code(text)):
            raw = match.group(1) or match.group(2)
            target = unquote(raw)
            if urlsplit(target).scheme in {"https", "http", "mailto"}:
                continue
            link_count += 1
            path_text, _, fragment = target.partition("#")
            if re.match(r"^[A-Za-z]:", path_text) or path_text.startswith(("file:", "\\\\")):
                finding("absolute_local_markdown_link", relative, detail="Use a repository-relative link")
                continue
            target_path = (ROOT / relative).parent / path_text if path_text else ROOT / relative
            target_path = target_path.resolve()
            if not target_path.is_relative_to(ROOT.resolve()):
                finding("markdown_link_outside_repository", relative, detail=path_text)
                continue
            if target_path.is_dir():
                target_path /= "README.md"
            target_relative = target_path.relative_to(ROOT).as_posix()
            if target_relative not in available:
                finding("markdown_link_not_in_public_files", relative, detail=target_relative)
                continue
            if fragment:
                if re.fullmatch(r"L\d+(?:-L\d+)?", fragment):
                    numbers = [int(value) for value in re.findall(r"\d+", fragment)]
                    lines = text_cache.get(target_relative, content(target_relative).decode("utf-8-sig")).splitlines()
                    if min(numbers) < 1 or max(numbers) > len(lines):
                        finding("source_line_link_out_of_range", relative, detail=target_relative + "#" + fragment)
                elif target_path.suffix.lower() == ".md":
                    anchors = markdown_anchors(text_cache.get(target_relative, content(target_relative).decode("utf-8-sig")))
                    if fragment not in anchors:
                        finding("markdown_anchor_missing", relative, detail=target_relative + "#" + fragment)
    folders = {Path(relative).parent for relative in files}
    for folder in sorted(folders, key=str):
        if folder == Path("."):
            continue
        expected = (folder / "README.md").as_posix()
        if expected not in available:
            finding("folder_readme_missing", expected)
    return {"passed": not issues, "candidate_files": len(files), "markdown_links_checked": link_count,
            "issues": issues, "warnings": warnings, "staged_only": staged,
            "scope": "Read-only heuristic publication checks; not a complete secret/security proof"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect tracked/index paths instead of untracked candidates")
    parser.add_argument("--json-out", type=Path, help="Optional private validation report path")
    args = parser.parse_args()
    try:
        result = audit(args.staged)
    except RuntimeError as exc:
        print(str(exc))
        return 2
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
