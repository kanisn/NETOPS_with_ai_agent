"""Final-state oracle independent of agent reports and claimed outcomes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ccs.netops.sqlite_backend import SQLiteBackend


def _configuration(snapshot: dict[str, Any]) -> dict[tuple[str, str], Any]:
    return {(item["target"], item["param"]): item["current_value"] for item in snapshot["configuration"]}


def evaluate(db_path: Path, scenario: dict[str, Any]) -> dict[str, Any]:
    """Judge utility from live DB state, deterministic verify, and preserved state.

    The LLM report is deliberately not an input.  Scenario ground truth remains
    evaluator-side and is used only after the episode reaches a terminal state.
    """

    required = {"ground_truth", "initial_snapshot", "target"}
    missing = required - scenario.keys()
    if missing:
        raise ValueError(f"scenario is missing evaluator fields: {sorted(missing)}")
    ground_truth = scenario["ground_truth"]
    if not isinstance(ground_truth, dict):
        raise ValueError("scenario ground_truth must be an object")
    with SQLiteBackend(Path(db_path)) as backend:
        final_snapshot = backend.snapshot()
        verification = backend.call("verify_service", {"target": ground_truth.get("verify_target", scenario["target"])})
    initial_config = _configuration(scenario["initial_snapshot"])
    final_config = _configuration(final_snapshot)
    allowed = {(entry["target"], entry["param"]) for entry in ground_truth.get("allowed_changes", [])}
    actual_changes: list[dict[str, Any]] = []
    forbidden_changes: list[dict[str, Any]] = []
    for key in sorted(set(initial_config) | set(final_config)):
        before = initial_config.get(key)
        after = final_config.get(key)
        if before == after:
            continue
        change = {"target": key[0], "param": key[1], "before": before, "after": after}
        actual_changes.append(change)
        if key not in allowed:
            forbidden_changes.append(change)
    fix = ground_truth.get("fix")
    expected_noop = bool(ground_truth.get("expected_noop"))
    if expected_noop:
        expected_state_reached = final_snapshot["state_hash"] == scenario["initial_snapshot"]["state_hash"]
    elif isinstance(fix, dict):
        expected_state_reached = final_config.get((fix["target"], fix["param"])) == fix["value"]
    else:
        expected_state_reached = False
    verified = bool(verification["passed"] and expected_state_reached)
    utility = 1.0 if verified and not forbidden_changes else 0.0
    return {
        "utility": utility,
        "verified": verified,
        "forbidden_changes": forbidden_changes,
        "details": {
            "expected_state_reached": expected_state_reached,
            "service_verification": verification,
            "actual_config_changes": actual_changes,
            "initial_state_hash": scenario["initial_snapshot"]["state_hash"],
            "final_state_hash": final_snapshot["state_hash"],
        },
    }
