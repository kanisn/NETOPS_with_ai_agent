"""Append-only, per-process disclosure event bus."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import DisclosureEvent


_WRITER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_NUMBERED_EPISODE = re.compile(r"^episode-(\d+)$")


def canonical_json_bytes(value: Any) -> bytes:
    """Return the exact JSON representation used for blob integrity checks."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class EventBus:
    """Write one JSONL shard and immutable payload blobs for one process.

    A writer ID is a single-writer ownership boundary. Callers may change
    ``episode_id`` between sequential episodes; the bus then advances the
    deterministic ``episode_seq`` used by offline merging.
    """

    def __init__(self, run_dir: Path, writer_id: str, run_id: str, episode_id: str):
        if not isinstance(run_dir, Path):
            raise TypeError("run_dir must be pathlib.Path")
        if not _WRITER_ID.fullmatch(writer_id):
            raise ValueError("writer_id must be a safe shard name")
        if not run_id or not episode_id:
            raise ValueError("run_id and episode_id must be non-empty")

        self.run_dir = run_dir
        self.writer_id = writer_id
        self.run_id = run_id
        self._lock = threading.Lock()
        self._events_dir = run_dir / "events"
        self._blobs_dir = run_dir / "blobs"
        self._events_dir.mkdir(parents=True, exist_ok=True)
        self._blobs_dir.mkdir(parents=True, exist_ok=True)
        self._shard_path = self._events_dir / f"{writer_id}.jsonl"
        self._local_seq = 0
        self._episode_sequences: dict[str, int] = {}
        self._load_existing_shard()
        self._episode_id = episode_id
        if episode_id not in self._episode_sequences:
            match = _NUMBERED_EPISODE.fullmatch(episode_id)
            next_sequence = (
                int(match.group(1))
                if match
                else max(self._episode_sequences.values(), default=-1) + 1
            )
            self._episode_sequences[episode_id] = next_sequence

    @property
    def episode_id(self) -> str:
        return self._episode_id

    @episode_id.setter
    def episode_id(self, value: str) -> None:
        if not value:
            raise ValueError("episode_id must be non-empty")
        with self._lock:
            if value not in self._episode_sequences:
                match = _NUMBERED_EPISODE.fullmatch(value)
                self._episode_sequences[value] = (
                    int(match.group(1))
                    if match
                    else max(self._episode_sequences.values(), default=-1) + 1
                )
            self._episode_id = value

    @property
    def shard_path(self) -> Path:
        return self._shard_path

    def _load_existing_shard(self) -> None:
        if not self._shard_path.exists():
            return
        with self._shard_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    event = DisclosureEvent.model_validate_json(line)
                except Exception as exc:
                    raise ValueError(
                        f"cannot resume invalid shard {self._shard_path.name}:{line_number}: {exc}"
                    ) from exc
                if event.writer_id != self.writer_id or event.run_id != self.run_id:
                    raise ValueError("existing shard belongs to a different writer or run")
                self._local_seq = max(self._local_seq, event.local_seq)
                known = self._episode_sequences.get(event.episode_id)
                if known is not None and known != event.episode_seq:
                    raise ValueError("episode_id has conflicting episode_seq values")
                self._episode_sequences[event.episode_id] = event.episode_seq

    def emit(
        self,
        stage: str,
        payload: Any,
        source: str,
        sink: str,
        *,
        causation_event_id: str | None = None,
        transport: str = "local",
        status: str = "succeeded",
        **metadata: Any,
    ) -> str:
        """Persist a payload and event, returning the new event ID.

        The blob is committed before the JSONL event. A crash can therefore
        leave an orphan blob, which the integrity gate rejects, but cannot
        leave an event that appeared valid before its blob existed.
        """

        if not source or not sink or not transport:
            raise ValueError("source, sink, and transport must be non-empty")
        payload_bytes = canonical_json_bytes(payload)

        with self._lock:
            event_id = str(uuid.uuid4())
            local_seq = self._local_seq + 1
            episode_id = self._episode_id
            episode_seq = self._episode_sequences[episode_id]

            trace_id = metadata.pop(
                "trace_id", str(uuid.uuid5(uuid.NAMESPACE_URL, f"ccs:{self.run_id}:{episode_id}"))
            )
            span_id = metadata.pop("span_id", str(uuid.uuid4()))
            parent_span_id = metadata.pop("parent_span_id", None)
            task_id = metadata.pop("task_id", episode_id)
            attempt = metadata.pop("attempt", 1)
            authenticated_principal = metadata.pop("authenticated_principal", source)
            principal_role = metadata.pop("principal_role", sink)
            purpose = metadata.pop("purpose", None)
            ts_logical = metadata.pop("ts_logical", local_seq)
            gate_id = metadata.pop("gate_id", "null@v0")
            decision = metadata.pop("decision", "allow")

            event = DisclosureEvent(
                event_id=event_id,
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                causation_event_id=causation_event_id,
                run_id=self.run_id,
                episode_id=episode_id,
                episode_seq=episode_seq,
                task_id=task_id,
                writer_id=self.writer_id,
                local_seq=local_seq,
                attempt=attempt,
                stage=stage,
                source=source,
                sink=sink,
                authenticated_principal=authenticated_principal,
                principal_role=principal_role,
                purpose=purpose,
                payload_ref=f"blobs/{event_id}.json",
                payload_digest=hashlib.sha256(payload_bytes).hexdigest(),
                payload_size=len(payload_bytes),
                transport=transport,
                gate_id=gate_id,
                decision=decision,
                status=status,
                ts_logical=ts_logical,
                ts_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                metadata=metadata,
            )

            blob_path = self.run_dir / event.payload_ref
            writing_path = self._blobs_dir / f".{event_id}.writing.json"
            try:
                with writing_path.open("xb") as blob_handle:
                    blob_handle.write(payload_bytes)
                    blob_handle.flush()
                    os.fsync(blob_handle.fileno())
                os.replace(writing_path, blob_path)
                event_line = event.model_dump_json() + "\n"
                with self._shard_path.open("a", encoding="utf-8", newline="\n") as event_handle:
                    event_handle.write(event_line)
                    event_handle.flush()
                    os.fsync(event_handle.fileno())
                self._local_seq = local_seq
            finally:
                if writing_path.exists():
                    writing_path.unlink()
            return event_id
