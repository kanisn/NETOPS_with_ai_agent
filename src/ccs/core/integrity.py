"""Offline artifact integrity gate and deterministic causal merge."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .events import DisclosureEvent, STAGE_ORDER


_TERMINAL_STATUSES = {
    "closed",
    "completed",
    "failed",
    "cancelled",
    "canceled",
    "timeout",
    "budget_exceeded",
    "failed_llm_schema",
}


def _load_terminal_episodes(run_dir: Path, events: list[DisclosureEvent], errors: list[str]) -> set[str]:
    terminal = {
        event.episode_id
        for event in events
        if event.metadata.get("episode_terminal") is True
    }
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return terminal
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest.json is unreadable: {exc}")
        return terminal
    if not isinstance(manifest, dict):
        errors.append("manifest.json must contain an object")
        return terminal

    all_episode_ids = {event.episode_id for event in events}
    if manifest.get("terminal") is True or str(manifest.get("status", "")).lower() in _TERMINAL_STATUSES:
        terminal.update(all_episode_ids)
    episodes = manifest.get("episodes", [])
    if episodes is not None and not isinstance(episodes, list):
        errors.append("manifest episodes must be a list")
        return terminal
    for episode in episodes or []:
        if not isinstance(episode, dict) or not isinstance(episode.get("episode_id"), str):
            errors.append("manifest episode entries require episode_id")
            continue
        if episode.get("terminal") is True or str(episode.get("status", "")).lower() in _TERMINAL_STATUSES:
            terminal.add(episode["episode_id"])
    return terminal


def _event_sort_key(event: DisclosureEvent) -> tuple[Any, ...]:
    return (event.episode_seq, event.ts_logical, event.writer_id, event.local_seq, event.event_id)


def _topological_order(
    events: list[DisclosureEvent],
    dependencies: dict[str, set[str]],
) -> list[DisclosureEvent] | None:
    by_id = {event.event_id: event for event in events}
    children: dict[str, set[str]] = defaultdict(set)
    indegree = {event.event_id: 0 for event in events}
    for child, parents in dependencies.items():
        for parent in parents:
            if parent in by_id and child in by_id and child not in children[parent]:
                children[parent].add(child)
                indegree[child] += 1

    ready = sorted((by_id[event_id] for event_id, degree in indegree.items() if degree == 0), key=_event_sort_key)
    ordered: list[DisclosureEvent] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for child_id in sorted(children[current.event_id]):
            indegree[child_id] -= 1
            if indegree[child_id] == 0:
                ready.append(by_id[child_id])
                ready.sort(key=_event_sort_key)
    return ordered if len(ordered) == len(events) else None


def _validate_terminal_pairs(
    events: list[DisclosureEvent], terminal_episodes: set[str], errors: list[str]
) -> None:
    response_stage = {"G4.call": "G4.ret", "G5.req": "G5.res"}
    children: dict[str, list[DisclosureEvent]] = defaultdict(list)
    by_id = {event.event_id: event for event in events}
    for event in events:
        if event.causation_event_id:
            children[event.causation_event_id].append(event)
            expected_request = {"G4.ret": "G4.call", "G5.res": "G5.req"}.get(event.stage)
            if expected_request:
                parent = by_id.get(event.causation_event_id)
                if parent is not None and parent.stage != expected_request:
                    errors.append(
                        f"{event.stage} event {event.event_id} is caused by {parent.stage}, expected {expected_request}"
                    )

    for event in events:
        expected = response_stage.get(event.stage)
        if not expected or event.episode_id not in terminal_episodes or event.status == "duplicate":
            continue
        paired = [
            child
            for child in children[event.event_id]
            if child.stage == expected and child.status != "duplicate"
        ]
        if len(paired) != 1:
            errors.append(
                f"terminal {event.episode_id} requires exactly one {expected} for {event.event_id}; found {len(paired)}"
            )


def _validate_events(run_dir: Path, *, materialize_merge: bool) -> dict[str, Any]:
    """Validate event artifacts, optionally creating ``events_merged.jsonl``."""

    if not isinstance(run_dir, Path):
        raise TypeError("run_dir must be pathlib.Path")
    errors: list[str] = []
    events: list[DisclosureEvent] = []
    event_ids: set[str] = set()
    span_ids: set[str] = set()
    writer_sequences: set[tuple[str, int]] = set()
    payload_refs: Counter[str] = Counter()
    shard_sequences: dict[str, list[int]] = defaultdict(list)
    episode_sequences: dict[str, set[int]] = defaultdict(set)

    events_dir = run_dir / "events"
    shard_paths = sorted(events_dir.glob("*.jsonl")) if events_dir.exists() else []
    for shard_path in shard_paths:
        try:
            lines = shard_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"cannot read shard {shard_path.name}: {exc}")
            continue
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                errors.append(f"blank event line in {shard_path.name}:{line_number}")
                continue
            try:
                raw = json.loads(line)
                event = DisclosureEvent.model_validate(raw)
            except (json.JSONDecodeError, ValidationError) as exc:
                errors.append(f"invalid event {shard_path.name}:{line_number}: {exc}")
                continue
            if event.writer_id != shard_path.stem:
                errors.append(
                    f"writer_id {event.writer_id} does not own shard {shard_path.name}"
                )
            if event.event_id in event_ids:
                errors.append(f"duplicate event_id: {event.event_id}")
            event_ids.add(event.event_id)
            if event.span_id in span_ids:
                errors.append(f"duplicate span_id: {event.span_id}")
            span_ids.add(event.span_id)
            writer_sequence = (event.writer_id, event.local_seq)
            if writer_sequence in writer_sequences:
                errors.append(f"duplicate writer sequence: {writer_sequence}")
            writer_sequences.add(writer_sequence)
            shard_sequences[event.writer_id].append(event.local_seq)
            episode_sequences[event.episode_id].add(event.episode_seq)
            payload_refs[event.payload_ref] += 1
            events.append(event)

    run_ids = {event.run_id for event in events}
    if len(run_ids) > 1:
        errors.append(f"events contain multiple run_id values: {sorted(run_ids)}")
    for writer_id, sequences in shard_sequences.items():
        if sequences != list(range(1, len(sequences) + 1)):
            errors.append(f"writer {writer_id} local_seq is not contiguous from 1: {sequences}")
    for episode_id, sequences in episode_sequences.items():
        if len(sequences) != 1:
            errors.append(
                f"episode {episode_id} has conflicting episode_seq values: {sorted(sequences)}"
            )

    by_id: dict[str, DisclosureEvent] = {}
    by_span: dict[str, DisclosureEvent] = {}
    for event in events:
        by_id.setdefault(event.event_id, event)
        by_span.setdefault(event.span_id, event)

    dependencies: dict[str, set[str]] = defaultdict(set)
    for event in events:
        if event.causation_event_id:
            parent = by_id.get(event.causation_event_id)
            if parent is None:
                errors.append(
                    f"event {event.event_id} has missing causation_event_id {event.causation_event_id}"
                )
            else:
                dependencies[event.event_id].add(parent.event_id)
                if parent.trace_id != event.trace_id:
                    errors.append(f"causal trace mismatch: {parent.event_id} -> {event.event_id}")
        if event.parent_span_id:
            parent = by_span.get(event.parent_span_id)
            if parent is None:
                errors.append(
                    f"event {event.event_id} has missing parent_span_id {event.parent_span_id}"
                )
            else:
                dependencies[event.event_id].add(parent.event_id)
                if parent.trace_id != event.trace_id:
                    errors.append(f"span trace mismatch: {parent.event_id} -> {event.event_id}")

    blobs_dir = run_dir / "blobs"
    actual_blobs = {
        path.relative_to(run_dir).as_posix(): path
        for path in blobs_dir.glob("*.json")
    } if blobs_dir.exists() else {}
    for payload_ref, count in payload_refs.items():
        if count != 1:
            errors.append(f"payload_ref {payload_ref} is referenced {count} times")
        blob_path = actual_blobs.get(payload_ref)
        if blob_path is None:
            errors.append(f"missing blob: {payload_ref}")
            continue
        try:
            blob_bytes = blob_path.read_bytes()
            json.loads(blob_bytes)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"invalid blob {payload_ref}: {exc}")
            continue
        event = next((candidate for candidate in events if candidate.payload_ref == payload_ref), None)
        if event is None:
            continue
        digest = hashlib.sha256(blob_bytes).hexdigest()
        if digest != event.payload_digest:
            errors.append(f"blob digest mismatch: {payload_ref}")
        if len(blob_bytes) != event.payload_size:
            errors.append(f"blob size mismatch: {payload_ref}")
    for payload_ref in sorted(set(actual_blobs) - set(payload_refs)):
        errors.append(f"orphan blob: {payload_ref}")

    terminal_episodes = _load_terminal_episodes(run_dir, events, errors)
    if terminal_episodes and not events:
        errors.append("terminal run has no events")
    _validate_terminal_pairs(events, terminal_episodes, errors)

    ordered: list[DisclosureEvent]
    if len(by_id) != len(events):
        ordered = []
    else:
        causal_order = _topological_order(events, dependencies)
        if causal_order is None:
            errors.append("causal graph contains a cycle")
            ordered = []
        else:
            ordered = causal_order

    merged_path = run_dir / "events_merged.jsonl"
    if materialize_merge and errors:
        if merged_path.exists():
            merged_path.unlink()
    elif materialize_merge:
        merged_path.parent.mkdir(parents=True, exist_ok=True)
        writing_path = run_dir / "events_merged.writing.jsonl"
        try:
            with writing_path.open("x", encoding="utf-8", newline="\n") as handle:
                for event in ordered:
                    handle.write(event.model_dump_json() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(writing_path, merged_path)
        finally:
            if writing_path.exists():
                writing_path.unlink()

    present_stages = {event.stage for event in events}
    stages = [stage for stage in STAGE_ORDER if stage in present_stages]
    return {
        "valid": not errors,
        "event_count": len(events),
        "stages": stages,
        "errors": errors,
        "merged_path": str(merged_path) if materialize_merge and not errors else None,
    }


def validate_events(run_dir: Path) -> dict[str, Any]:
    """Validate event artifacts without creating, replacing, or deleting files."""

    return _validate_events(run_dir, materialize_merge=False)


def validate_and_merge(run_dir: Path) -> dict[str, Any]:
    """Validate event artifacts and create ``events_merged.jsonl`` when valid."""

    return _validate_events(run_dir, materialize_merge=True)
