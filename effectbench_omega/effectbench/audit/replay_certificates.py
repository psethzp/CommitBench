#!/usr/bin/env python3
"""Replay generated certificate bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from effectbench.effects import dumps, loads
from effectbench.native import execute_native_episode, is_native_row


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _actions_from_trace(trace: dict[str, object]) -> list[str]:
    payload = trace.get("actions", "[]")
    if isinstance(payload, str):
        actions = json.loads(payload or "[]")
    else:
        actions = payload
    return [str(action.get("action", "")) for action in actions if isinstance(action, dict)]


def _native_replay_failures(payload: dict[str, object]) -> list[str]:
    failures: list[str] = []
    trace = payload.get("model_trace", {})
    cert = payload.get("certificate", {})
    if not isinstance(trace, dict) or not isinstance(cert, dict) or not is_native_row(trace):
        return failures

    result = execute_native_episode(trace, _actions_from_trace(trace))
    expected_success = _as_bool(trace.get("terminal_success", False))
    if result.terminal_success != expected_success:
        failures.append("native_model_trace_terminal_success_mismatch")
    if dumps(result.effect_vector) != dumps(loads(str(cert.get("effect_vector", trace.get("effect_vector", "{}"))))):
        failures.append("native_model_trace_effect_mismatch")

    witness_trace = payload.get("lower_effect_witness_trace")
    witness_candidate = payload.get("lower_effect_witness_candidate")
    if isinstance(witness_trace, dict) and witness_trace:
        witness_result = execute_native_episode(witness_trace, _actions_from_trace(witness_trace))
        if not witness_result.terminal_success:
            failures.append("native_witness_trace_terminal_failure")
    elif isinstance(witness_candidate, dict) and witness_candidate:
        candidate_actions = [str(action) for action in witness_candidate.get("actions", [])]
        candidate_result = execute_native_episode(trace, candidate_actions)
        if not candidate_result.terminal_success:
            failures.append("native_witness_candidate_terminal_failure")
        expected_effect = str(witness_candidate.get("effect_vector") or cert.get("witness_effect_vector") or "")
        if expected_effect and dumps(candidate_result.effect_vector) != dumps(loads(expected_effect)):
            failures.append("native_witness_candidate_effect_mismatch")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", required=True)
    parser.add_argument("--out")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir)
    bundles = [path for path in bundle_dir.glob("*.json") if path.name != "verifier_summary.json"]
    failures = []
    native_replays = 0
    for path in bundles:
        payload = json.loads(path.read_text())
        cert = payload.get("certificate", {})
        if not cert.get("trace_id") or not payload.get("model_trace"):
            failures.append(str(path))
        if (
            cert.get("verdict") == "strict_excess"
            and not payload.get("lower_effect_witness_trace")
            and not payload.get("lower_effect_witness_candidate")
        ):
            failures.append(str(path))
        native_failures = _native_replay_failures(payload)
        if native_failures:
            failures.append(f"{path}: {','.join(native_failures)}")
        elif isinstance(payload.get("model_trace"), dict) and is_native_row(payload["model_trace"]):
            native_replays += 1

    report = f"bundles_checked: {len(bundles)}\nnative_replays_checked: {native_replays}\nfailures: {len(failures)}\n"
    if failures:
        report += "failed_bundles:\n" + "\n".join(failures) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report)
    print(report, end="")
    return 1 if failures and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
