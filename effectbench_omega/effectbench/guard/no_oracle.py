"""No-oracle runtime guard helpers."""

from __future__ import annotations


FORBIDDEN_RUNTIME_FIELDS = {
    "future_user_turns",
    "gold_terminal_state",
    "offline_terminal_frontier_id",
    "evaluator_label",
    "final_outcome",
    "posthoc_witness_bundle",
}


def assert_no_oracle(context: dict[str, object]) -> None:
    present = sorted(FORBIDDEN_RUNTIME_FIELDS.intersection(context))
    if present:
        raise RuntimeError(f"oracle fields present at runtime: {present}")


def strip_oracle_fields(context: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in context.items() if key not in FORBIDDEN_RUNTIME_FIELDS}

