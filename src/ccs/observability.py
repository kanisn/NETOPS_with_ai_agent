"""Append-only realtime activity stream for human operators.

The activity stream is deliberately separate from the disclosure audit log.  It
contains only values that callers intentionally choose to display and never
copies provider responses or provider reasoning objects.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import threading
from typing import Any, Iterable
import uuid

from ccs.pacing import control_path_for_run, wait_after_event


_SAFE_WRITER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
_STATUS = {"started", "succeeded", "failed", "waiting", "skipped", "info"}
_SECRET_FIELD = re.compile(
    r"(?:^|_)(?:api_key|secret|password|authorization|credential|access_token|refresh_token|token)(?:$|_)",
    re.IGNORECASE,
)
_HIDDEN_PROVIDER_FIELD = re.compile(
    r"(?:^|_)(?:raw_response|encrypted_content|hidden_thinking|reasoning_content|thinking)(?:$|_)",
    re.IGNORECASE,
)
_KEY_PATTERN = re.compile(r"\b(?:sk|sk-ant)-[A-Za-z0-9_-]{12,}\b")
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{8,}=*")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_writer_id(writer_id: str) -> str:
    if not writer_id:
        raise ValueError("writer_id must be non-empty")
    if _SAFE_WRITER.fullmatch(writer_id):
        return writer_id
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", writer_id).strip(".-") or "writer"
    digest = hashlib.sha256(writer_id.encode("utf-8")).hexdigest()[:8]
    return f"{stem[:86]}-{digest}"


def _configured_secrets() -> tuple[str, ...]:
    names = {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "CCS_OPERATION_TOKEN",
        "CCS_DIAGNOSIS_TOKEN",
        "CCS_A2A_TOKEN",
    }
    values = [os.environ.get(name, "") for name in names]
    return tuple(sorted({value for value in values if len(value) >= 8}, key=len, reverse=True))


def _scrub(value: Any, secrets: tuple[str, ...]) -> Any:
    """Return JSON-safe activity data with credentials removed.

    This is a final safety net.  Callers remain responsible for passing only
    intentional operator-visible payloads rather than raw provider objects.
    """

    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            cleaned[text_key] = (
                "[REDACTED]"
                if _SECRET_FIELD.search(text_key) or _HIDDEN_PROVIDER_FIELD.search(text_key)
                else _scrub(item, secrets)
            )
        return cleaned
    if isinstance(value, (list, tuple, set)):
        return [_scrub(item, secrets) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str):
        cleaned = value
        for secret in secrets:
            cleaned = cleaned.replace(secret, "[REDACTED]")
        cleaned = _KEY_PATTERN.sub("[REDACTED]", cleaned)
        return _BEARER_PATTERN.sub("Bearer [REDACTED]", cleaned)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


class ActivityLog:
    """Write one flushed JSONL shard owned by a single process/writer."""

    def __init__(
        self,
        run_dir: Path,
        writer_id: str,
        episode_id: str = "",
        mode: str | None = None,
        *,
        secrets: Iterable[str] | None = None,
    ):
        if not isinstance(run_dir, Path):
            raise TypeError("run_dir must be pathlib.Path")
        self.run_dir = run_dir
        self.run_id = run_dir.name
        self.writer_id = _safe_writer_id(writer_id)
        self.episode_id = episode_id
        self.mode = mode
        self._lock = threading.Lock()
        supplied = tuple(str(value) for value in (secrets or ()) if value and len(str(value)) >= 8)
        self._secrets = tuple(sorted(set(_configured_secrets()) | set(supplied), key=len, reverse=True))
        self._delay_control_path = control_path_for_run(run_dir)
        activity_dir = run_dir / "activity"
        activity_dir.mkdir(parents=True, exist_ok=True)
        self.shard_path = activity_dir / f"{self.writer_id}.jsonl"
        self._local_seq = self._resume_sequence()

    def _resume_sequence(self) -> int:
        if not self.shard_path.exists():
            return 0
        latest = 0
        with self.shard_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"cannot resume invalid activity shard {self.shard_path.name}:{line_number}"
                    ) from exc
                if event.get("writer_id") != self.writer_id or event.get("run_id") != self.run_id:
                    raise ValueError("existing activity shard belongs to a different writer or run")
                latest = max(latest, int(event.get("local_seq", 0)))
        return latest

    def emit(
        self,
        component: str,
        action: str,
        status: str,
        summary: str,
        *,
        details: Any = None,
        operation_id: str | None = None,
        trace_id: str | None = None,
        delay_after: bool = True,
        **extra: Any,
    ) -> str:
        if not component or not action or not summary:
            raise ValueError("component, action, and summary must be non-empty")
        if status not in _STATUS:
            raise ValueError(f"unsupported activity status: {status}")
        with self._lock:
            event_id = str(uuid.uuid4())
            self._local_seq += 1
            event = {
                "event_id": event_id,
                "ts_utc": _utc_now(),
                "run_id": self.run_id,
                "episode_id": self.episode_id,
                "writer_id": self.writer_id,
                "local_seq": self._local_seq,
                "component": component,
                "action": action,
                "status": status,
                "summary": summary,
                "details": _scrub(details, self._secrets),
                "operation_id": operation_id or event_id,
                "mode": self.mode,
            }
            if trace_id is not None:
                event["trace_id"] = trace_id
            event.update(_scrub(extra, self._secrets))
            event = _scrub(event, self._secrets)
            line = json.dumps(event, ensure_ascii=False, allow_nan=False, separators=(",", ":"), default=str)
            with self.shard_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        if delay_after and self._delay_control_path is not None:
            wait_after_event(
                self.run_dir,
                self.writer_id,
                event_id,
                self._delay_control_path,
            )
        return event_id


def activity_for_episode(
    path: Path,
    role: str,
    mode: str | None = None,
    *,
    secrets: Iterable[str] | None = None,
) -> ActivityLog:
    """Create a collision-free activity writer from a run or episode path."""

    location = Path(path)
    if location.parent.name == "episodes":
        run_dir = location.parents[1]
        episode_id = location.name
    else:
        run_dir = location
        episode_id = ""
    writer_id = role if role == "runner" or not episode_id else f"{role}-{episode_id}"
    return ActivityLog(run_dir, writer_id, episode_id=episode_id, mode=mode, secrets=secrets)
