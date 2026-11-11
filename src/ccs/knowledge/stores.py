"""SQLite FTS5 stores used by the Operation Agent."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from ccs.contracts import MemoryRecord


_QUERY_TOKEN = re.compile(r"[\w]+(?:[.-][\w]+)*", re.UNICODE)
_CLASSIFICATIONS = {"public", "internal", "restricted"}


def runbook_files(directory: Path) -> list[Path]:
    """List Markdown runbooks, excluding folder README documentation."""
    return sorted(path for path in directory.rglob("*.md") if path.name.casefold() != "readme.md")


def _fts_query(query: str) -> str | None:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    tokens = [token[:64] for token in _QUERY_TOKEN.findall(query.casefold())][:32]
    if not tokens:
        return None
    return " OR ".join(f'"{token}"' for token in tokens)


def _validate_k(k: int) -> None:
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")


def _connect(path: Path) -> sqlite3.Connection:
    if not isinstance(path, Path):
        raise TypeError("db_path must be pathlib.Path")
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def _parse_runbook(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"runbook {path.name} requires YAML-like front matter")
    try:
        closing = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"runbook {path.name} has unterminated front matter") from exc
    metadata: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"runbook {path.name} has invalid metadata line: {line}")
        metadata[key.strip()] = value.strip().strip('"\'')
    required = {"doc_id", "version", "tenant", "classification", "source"}
    missing = sorted(required - metadata.keys())
    if missing:
        raise ValueError(f"runbook {path.name} is missing metadata: {missing}")
    if metadata["classification"] not in _CLASSIFICATIONS:
        raise ValueError(f"runbook {path.name} has invalid classification")
    body = "\n".join(lines[closing + 1 :]).strip()
    if not body:
        raise ValueError(f"runbook {path.name} has no body")
    return metadata, body


def _chunks(doc_id: str, body: str) -> list[tuple[str, str]]:
    """Split at level-two headings while retaining the document title."""

    title_lines: list[str] = []
    chunks: list[list[str]] = []
    current: list[str] = []
    seen_section = False
    for line in body.splitlines():
        if line.startswith("## "):
            if current:
                chunks.append(current)
            current = title_lines.copy() + [line]
            seen_section = True
        elif not seen_section:
            title_lines.append(line)
        else:
            current.append(line)
    if current:
        chunks.append(current)
    if not chunks:
        chunks = [title_lines]
    return [
        (f"{doc_id}:{index:03d}", "\n".join(lines).strip())
        for index, lines in enumerate(chunks, start=1)
        if "\n".join(lines).strip()
    ]


class RunbookStore:
    """Deterministic local BM25 index over the checked-in English runbooks."""

    def __init__(self, db_path: Path, documents_dir: Path):
        if not isinstance(documents_dir, Path):
            raise TypeError("documents_dir must be pathlib.Path")
        if not documents_dir.is_dir():
            raise FileNotFoundError(f"runbook directory does not exist: {documents_dir}")
        self.db_path = db_path
        self.documents_dir = documents_dir
        self.connection = _connect(db_path)
        try:
            self.connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS runbook_chunks USING fts5(
                    chunk_id UNINDEXED,
                    doc_id UNINDEXED,
                    text,
                    meta UNINDEXED,
                    tokenize='porter unicode61'
                )
                """
            )
        except sqlite3.OperationalError as exc:
            self.connection.close()
            raise RuntimeError("SQLite was built without FTS5 support") from exc
        self._rebuild()

    def _rebuild(self) -> None:
        rows: list[tuple[str, str, str, str]] = []
        doc_ids: set[str] = set()
        for path in runbook_files(self.documents_dir):
            metadata, body = _parse_runbook(path)
            doc_id = metadata["doc_id"]
            if doc_id in doc_ids:
                raise ValueError(f"duplicate runbook doc_id: {doc_id}")
            doc_ids.add(doc_id)
            for chunk_id, text in _chunks(doc_id, body):
                rows.append(
                    (
                        chunk_id,
                        doc_id,
                        text,
                        json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                    )
                )
        with self.connection:
            self.connection.execute("DELETE FROM runbook_chunks")
            self.connection.executemany(
                "INSERT INTO runbook_chunks(chunk_id, doc_id, text, meta) VALUES (?, ?, ?, ?)",
                rows,
            )

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        _validate_k(k)
        match = _fts_query(query)
        if match is None:
            return []
        rows = self.connection.execute(
            """
            SELECT chunk_id, doc_id, text, meta, bm25(runbook_chunks) AS score
            FROM runbook_chunks
            WHERE runbook_chunks MATCH ?
            ORDER BY score ASC, doc_id ASC, chunk_id ASC
            LIMIT ?
            """,
            (match, k),
        ).fetchall()
        return [
            {
                "chunk_id": row["chunk_id"],
                "doc_id": row["doc_id"],
                "text": row["text"],
                "meta": json.loads(row["meta"]),
                "score": float(row["score"]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "RunbookStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class MemoryStore:
    """Run-local incident memory shared by sequential episodes.

    D0 deliberately applies no tenant, scope, or expiry filtering at read time.
    That unprotected behavior is measurable, while write eligibility remains a
    baseline safety condition controlled by the runner/operator simulator.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = _connect(db_path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_records(
                record_id TEXT PRIMARY KEY,
                scope_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                purpose TEXT NOT NULL,
                written_at INTEGER NOT NULL,
                expires_at INTEGER,
                source_event_ids_json TEXT NOT NULL,
                verified_outcome TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                items_json TEXT NOT NULL,
                search_text TEXT NOT NULL
            )
            """
        )
        try:
            self.connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    record_id UNINDEXED,
                    search_text,
                    tokenize='porter unicode61'
                )
                """
            )
        except sqlite3.OperationalError as exc:
            self.connection.close()
            raise RuntimeError("SQLite was built without FTS5 support") from exc
        self.connection.commit()

    def write(
        self,
        record: dict[str, Any] | MemoryRecord,
        *,
        verified: bool,
        approved: bool,
    ) -> str:
        if approved is not True:
            raise PermissionError("memory write requires explicit approval")
        if verified is not True:
            raise PermissionError("memory write requires a verified terminal outcome")
        validated = record if isinstance(record, MemoryRecord) else MemoryRecord.model_validate(record)
        if not validated.verified_outcome.strip():
            raise ValueError("verified_outcome must be non-empty")
        return self._insert(validated)

    def import_reference(
        self,
        reference: dict[str, Any],
        *,
        operator_seeded_experimental_context: bool,
    ) -> str:
        """Import an unverified operator reference without weakening normal writes."""

        if operator_seeded_experimental_context is not True:
            raise PermissionError("reference import is limited to operator-seeded experimental context")
        if not isinstance(reference, dict):
            raise TypeError("reference must be a dictionary")
        required = {"id", "title", "content"}
        optional = {"source_kind", "source_run_id"}
        if set(reference) - required - optional or not required <= set(reference):
            raise ValueError("reference requires id, title and content with only supported provenance fields")
        normalized: dict[str, str] = {}
        for key in required | (set(reference) & optional):
            value = reference[key]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"reference {key} must be a non-empty string")
            normalized[key] = value.strip()
        provenance = {
            "origin": "operator-imported-reference",
            "validation_status": "unverified",
            "reference_only": True,
            "source_kind": normalized.get("source_kind", "operator-note"),
            "source_run_id": normalized.get("source_run_id"),
        }
        record = MemoryRecord(
            record_id=normalized["id"],
            scope_id="operator-import",
            tenant_id="experimental-context",
            purpose="P-know",
            written_at=0,
            source_event_ids=[],
            verified_outcome="unverified_operator_reference",
            payload={
                "title": normalized["title"],
                "content": normalized["content"],
                "provenance": provenance,
            },
            items=[normalized["title"], normalized["content"]],
        )
        return self._insert(record)

    def _insert(self, validated: MemoryRecord) -> str:
        payload_json = json.dumps(
            validated.payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        source_json = json.dumps(validated.source_event_ids, ensure_ascii=False, separators=(",", ":"))
        items_json = json.dumps(validated.items, ensure_ascii=False, separators=(",", ":"))
        search_text = " ".join(
            (
                validated.record_id,
                validated.scope_id,
                validated.tenant_id,
                validated.purpose,
                validated.verified_outcome,
                payload_json,
                " ".join(validated.items),
            )
        )
        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT INTO memory_records(
                        record_id, scope_id, tenant_id, purpose, written_at,
                        expires_at, source_event_ids_json, verified_outcome,
                        payload_json, items_json, search_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        validated.record_id,
                        validated.scope_id,
                        validated.tenant_id,
                        validated.purpose,
                        validated.written_at,
                        validated.expires_at,
                        source_json,
                        validated.verified_outcome,
                        payload_json,
                        items_json,
                        search_text,
                    ),
                )
                self.connection.execute(
                    "INSERT INTO memory_fts(record_id, search_text) VALUES (?, ?)",
                    (validated.record_id, search_text),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"duplicate memory record_id: {validated.record_id}") from exc
        return validated.record_id

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        _validate_k(k)
        match = _fts_query(query)
        if match is None:
            return []
        rows = self.connection.execute(
            """
            SELECT m.*, bm25(memory_fts) AS score
            FROM memory_fts
            JOIN memory_records AS m ON m.record_id = memory_fts.record_id
            WHERE memory_fts MATCH ?
            ORDER BY score ASC, m.written_at DESC, m.record_id ASC
            LIMIT ?
            """,
            (match, k),
        ).fetchall()
        return [
            {
                "record_id": row["record_id"],
                "scope_id": row["scope_id"],
                "tenant_id": row["tenant_id"],
                "purpose": row["purpose"],
                "written_at": row["written_at"],
                "expires_at": row["expires_at"],
                "source_event_ids": json.loads(row["source_event_ids_json"]),
                "verified_outcome": row["verified_outcome"],
                "payload": json.loads(row["payload_json"]),
                "items": json.loads(row["items_json"]),
                "score": float(row["score"]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
