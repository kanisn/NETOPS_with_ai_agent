"""Offline sensitive-item matching over validated restricted payload blobs."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

from ccs.core.events import DisclosureEvent
from ccs.core.integrity import validate_and_merge


_DIGIT_FIELDS = {"employee_number", "phone"}
_NODE_FIELDS = {"host", "host_id", "node_id", "interface_id", "flow_id", "target_host"}
_IP_FIELDS = {"ip", "ip_address", "src_ip", "dst_ip", "source_ip", "destination_ip", "management_ip"}


def _registry_item(raw: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError(f"registry item {index} must be an object")
    required = ("item_id", "category", "field", "value", "origin_stage")
    for key in required:
        if not isinstance(raw.get(key), str) or not raw[key]:
            raise ValueError(f"registry item {index} requires non-empty string {key}")
    necessary = raw.get("necessary_stages", [])
    if not isinstance(necessary, list) or any(not isinstance(stage, str) for stage in necessary):
        raise ValueError(f"registry item {index} necessary_stages must be a string list")
    origin_episode_id = raw.get("origin_episode_id")
    if origin_episode_id is not None and (
        not isinstance(origin_episode_id, str) or not origin_episode_id
    ):
        raise ValueError(f"registry item {index} origin_episode_id must be a non-empty string")
    return {
        "item_id": raw["item_id"],
        "category": raw["category"],
        "field": raw["field"],
        "value": raw["value"],
        "origin_stage": raw["origin_stage"],
        "necessary_stages": list(necessary),
        "origin_episode_ids": [origin_episode_id] if origin_episode_id else [],
    }


def _deduplicate_registry(registry: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Collapse exact bindings without treating a per-world ID as global."""

    bindings = [_registry_item(item, index) for index, item in enumerate(registry)]
    by_binding: dict[str, dict[str, Any]] = {}
    label_by_value: dict[tuple[str, str], tuple[str, str, str]] = {}
    for item in bindings:
        normalized_value = _normal_value(item["field"], item["value"])
        descriptor = (item["category"], item["field"], item["origin_stage"])
        label_key = (item["item_id"], normalized_value)
        known_descriptor = label_by_value.get(label_key)
        if known_descriptor is not None and known_descriptor != descriptor:
            raise ValueError(
                f"registry item_id {item['item_id']} has conflicting metadata for one normalized value"
            )
        label_by_value[label_key] = descriptor
        aggregation_key = hashlib.sha256(
            "\x1f".join((*descriptor, normalized_value)).encode("utf-8")
        ).hexdigest()
        existing = by_binding.get(aggregation_key)
        if existing is None:
            item["aggregation_key"] = aggregation_key
            item["binding_id"] = aggregation_key
            item["registry_item_ids"] = [item["item_id"]]
            by_binding[aggregation_key] = item
            continue
        existing["necessary_stages"] = sorted(
            set(existing["necessary_stages"]) | set(item["necessary_stages"])
        )
        existing["origin_episode_ids"] = sorted(
            set(existing["origin_episode_ids"]) | set(item["origin_episode_ids"])
        )
        existing["registry_item_ids"] = sorted(
            set(existing["registry_item_ids"]) | {item["item_id"]}
        )
    return [by_binding[key] for key in sorted(by_binding)], len(bindings)


def _normal_value(field: str, value: str) -> str:
    field = field.casefold()
    if field in _DIGIT_FIELDS:
        return "".join(character for character in value if character.isdigit())
    if field in _IP_FIELDS:
        try:
            return ipaddress.ip_address(value.strip()).compressed.casefold()
        except ValueError:
            return value.strip().casefold()
    if field in _NODE_FIELDS:
        return re.sub(r"\s+", "", value).casefold()
    return value.casefold()


def _match_count(field: str, registry_value: str, candidate: str) -> int:
    needle = _normal_value(field, registry_value)
    if not needle:
        return 0
    normalized_field = field.casefold()
    if normalized_field in _DIGIT_FIELDS:
        digit_pattern = r"[\s().+\-]*".join(re.escape(character) for character in needle)
        return len(re.findall(rf"(?<!\d){digit_pattern}(?!\d)", candidate))
    elif normalized_field in _IP_FIELDS:
        matches = 0
        for token in re.findall(r"[0-9A-Fa-f:.]+", candidate):
            token = token.strip(".")
            if not token:
                continue
            try:
                if ipaddress.ip_address(token).compressed.casefold() == needle:
                    matches += 1
            except ValueError:
                continue
        return matches
    elif normalized_field in _NODE_FIELDS:
        structured_tokens = re.findall(
            r"[A-Za-z0-9_]+(?:\s*-\s*[A-Za-z0-9_]+)+",
            candidate,
        )
        matches = sum(
            re.sub(r"\s+", "", token).casefold() == needle
            for token in structured_tokens
        )
        if matches or "-" in needle:
            return matches
        haystack = candidate.casefold()
    else:
        haystack = candidate.casefold()
    return len(
        re.findall(
            rf"(?<![\w.-]){re.escape(needle)}(?![\w.-])",
            haystack,
        )
    )


def _scalars(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key in sorted(value):
            yield from _scalars(value[key], f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _scalars(item, f"{path}[{index}]")
    elif value is not None:
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = str(value)
        yield path, rendered


def build_ledger(run_dir: Path, registry: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a restricted provenance ledger without returning raw values."""

    if not isinstance(run_dir, Path):
        raise TypeError("run_dir must be pathlib.Path")
    if not isinstance(registry, list):
        raise TypeError("registry must be a list")
    normalized, registry_binding_count = _deduplicate_registry(registry)

    integrity = validate_and_merge(run_dir)
    if not integrity["valid"]:
        return {
            "valid": False,
            "errors": list(integrity["errors"]),
            "event_count": integrity["event_count"],
            "items": [],
        }

    merged_path = Path(integrity["merged_path"])
    events = [
        DisclosureEvent.model_validate_json(line)
        for line in merged_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    traces: dict[str, list[dict[str, Any]]] = defaultdict(list)
    occurrence_totals: Counter[str] = Counter()
    stage_counts: Counter[str] = Counter()
    unique_crossings: set[tuple[str, str, str]] = set()
    cross_episode_bindings: set[str] = set()
    cross_episode_visit_count = 0

    for event in events:
        payload = json.loads((run_dir / event.payload_ref).read_text(encoding="utf-8"))
        scalar_values = list(_scalars(payload))
        for item in normalized:
            matching_paths: list[str] = []
            occurrences = 0
            for path, candidate in scalar_values:
                count = _match_count(item["field"], item["value"], candidate)
                if count:
                    matching_paths.append(path)
                    occurrences += count
            if not occurrences:
                continue
            binding_id = item["binding_id"]
            occurrence_totals[binding_id] += occurrences
            stage_counts[event.stage] += occurrences
            unique_crossings.add((event.episode_id, event.sink, binding_id))
            is_cross_episode = bool(item["origin_episode_ids"]) and (
                event.episode_id not in item["origin_episode_ids"]
            )
            if is_cross_episode:
                cross_episode_bindings.add(binding_id)
                cross_episode_visit_count += 1
            traces[binding_id].append(
                {
                    "event_id": event.event_id,
                    "episode_id": event.episode_id,
                    "stage": event.stage,
                    "source": event.source,
                    "sink": event.sink,
                    "writer_id": event.writer_id,
                    "status": event.status,
                    "occurrences": occurrences,
                    "paths": sorted(set(matching_paths)),
                    "cross_episode": is_cross_episode,
                }
            )

    ledger_items: list[dict[str, Any]] = []
    for item in normalized:
        binding_id = item["binding_id"]
        trace = traces[binding_id]
        normalized_value = _normal_value(item["field"], item["value"])
        value_hash = hashlib.sha256(normalized_value.encode("utf-8")).hexdigest()
        ledger_items.append(
            {
                "item_id": item["item_id"],
                "registry_item_ids": item["registry_item_ids"],
                "binding_id": binding_id,
                "category": item["category"],
                "field": item["field"],
                "origin_stage": item["origin_stage"],
                "origin_episode_ids": item["origin_episode_ids"],
                "necessary_stages": item["necessary_stages"],
                "value_hash": value_hash,
                "aggregation_key": item["aggregation_key"],
                "first_seen_stage": trace[0]["stage"] if trace else None,
                "occurrence_count": occurrence_totals[binding_id],
                "cross_episode_visit_count": sum(visit["cross_episode"] for visit in trace),
                "trace": trace,
            }
        )

    fingerprint_material = [
        {
            "item_id": item["item_id"],
            "registry_item_ids": item["registry_item_ids"],
            "aggregation_key": item["aggregation_key"],
            "necessary_stages": item["necessary_stages"],
            "origin_episode_ids": item["origin_episode_ids"],
        }
        for item in ledger_items
    ]
    registry_fingerprint = hashlib.sha256(
        json.dumps(
            fingerprint_material,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    return {
        "valid": True,
        "errors": [],
        "event_count": len(events),
        "registry_binding_count": registry_binding_count,
        "registry_fingerprint": registry_fingerprint,
        "item_count": len(ledger_items),
        "matched_item_count": sum(bool(item["trace"]) for item in ledger_items),
        "occurrence_count": sum(occurrence_totals.values()),
        "unique_episode_sink_item_count": len(unique_crossings),
        "cross_episode_item_count": len(cross_episode_bindings),
        "cross_episode_visit_count": cross_episode_visit_count,
        "stage_counts": dict(sorted(stage_counts.items())),
        "items": ledger_items,
    }
