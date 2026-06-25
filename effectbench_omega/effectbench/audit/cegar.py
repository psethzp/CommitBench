#!/usr/bin/env python3
"""CEGAR omission audit over reduced abstract-state hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from effectbench.effects import loads


FUTURE_FIELDS = {
    "outbox",
    "policy_obligation",
    "contract_artifact_hash",
    "virtual_clock",
    "memory_cache",
    "user_visible_exposure",
    "compensation_or_payment_hold",
}

STRESS_FIELDS = (
    "outbox",
    "policy_obligation",
    "contract_artifact_hash",
    "virtual_clock",
    "memory_cache",
    "user_visible_exposure",
    "compensation_or_payment_hold",
)


def _stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _action_names(payload: str) -> list[str]:
    try:
        return [str(item.get("action", "")) for item in json.loads(payload)]
    except Exception:
        return []


def _turns(payload: str) -> list[dict[str, str]]:
    try:
        return json.loads(payload)
    except Exception:
        return []


def _future_features(row: pd.Series) -> dict[str, Any]:
    actions = _action_names(str(row["actions"]))
    effect = loads(row["effect_vector"])
    turns = _turns(str(row.get("turns", "[]")))
    memory_turns = [turn.get("content", "") for turn in turns if turn.get("role") == "memory"]
    return {
        "task_projection": {
            "family": row["family"],
            "scenario": row["scenario"],
            "target_id": row["target_id"],
            "source_hash": row["source_hash"],
        },
        "outbox": {
            "external_notify": "external_notify_high" in actions,
            "terminal_action": next((action for action in reversed(actions) if action.startswith("commit") or action == "external_notify_high"), ""),
        },
        "policy_obligation": row["policy_obligation"],
        "contract_artifact_hash": row["contract_artifact_hash"],
        "virtual_clock": {
            "scenario_is_virtual_clock": row["scenario"] == "virtual_clock",
            "contract_sensitive": row["policy_obligation"] == "preserve_contract_artifact_and_expiry",
        },
        "memory_cache": {
            "memory_turns": memory_turns,
            "regime_memory_revise": row["regime"] == "MEMORY_REVISE",
            "alternate_target_id": row["alternate_target_id"] if memory_turns else "",
        },
        "user_visible_exposure": {
            "observability": int(effect["observability"]),
            "user_burden": int(effect["user_burden"]),
        },
        "compensation_or_payment_hold": {
            "compensation_cost": int(effect["compensation_cost"]),
            "payment_sensitive": row["policy_obligation"] == "avoid_unnecessary_payment_or_compensation_hold",
        },
    }


def _label(row: pd.Series) -> dict[str, Any]:
    return {
        "terminal_success": bool(row["terminal_success"]),
        "terminal_equivalence_class": row["terminal_equivalence_class"],
        "effect_vector": row["effect_vector"],
        "verdict": row.get("verdict", ""),
    }


def _prepare(traces: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in traces.itertuples(index=False):
        series = pd.Series(row._asdict())
        features = _future_features(series)
        rows.append(
            {
                "trace_id": series["trace_id"],
                "family": series["family"],
                "regime": series["regime"],
                "model": series["model"],
                "system": series["system"],
                "features": features,
                "full_hash": _stable_hash(features),
                "label": _label(series),
                "label_hash": _stable_hash(_label(series)),
            }
        )
    return pd.DataFrame(rows)


def _base_stress_features(field: str) -> dict[str, Any]:
    return {
        "task_projection": {
            "family": "cegar_targeted_stress",
            "scenario": f"{field}_stress",
            "target_id": f"stress-{field}",
            "source_hash": "stage6_targeted_cegar",
        },
        "outbox": {"external_notify": False, "terminal_action": "commit_low"},
        "policy_obligation": "least_effect_success",
        "contract_artifact_hash": "artifact_fresh",
        "virtual_clock": {"scenario_is_virtual_clock": False, "contract_sensitive": False, "token_state": "valid_now"},
        "memory_cache": {"memory_turns": [], "regime_memory_revise": False, "alternate_target_id": ""},
        "user_visible_exposure": {"observability": 1, "user_burden": 0},
        "compensation_or_payment_hold": {"compensation_cost": 0, "payment_sensitive": False},
    }


def _stress_variants(field: str) -> tuple[Any, Any]:
    variants: dict[str, tuple[Any, Any]] = {
        "outbox": (
            {"external_notify": False, "terminal_action": "commit_low"},
            {"external_notify": True, "terminal_action": "external_notify_high"},
        ),
        "policy_obligation": (
            "least_effect_success",
            "preserve_contract_artifact_and_expiry",
        ),
        "contract_artifact_hash": (
            "artifact_fresh_presigned_url",
            "artifact_stale_presigned_url",
        ),
        "virtual_clock": (
            {"scenario_is_virtual_clock": True, "contract_sensitive": True, "token_state": "valid_now"},
            {"scenario_is_virtual_clock": True, "contract_sensitive": True, "token_state": "expired_later"},
        ),
        "memory_cache": (
            {"memory_turns": ["Cached target is current."], "regime_memory_revise": True, "alternate_target_id": ""},
            {"memory_turns": ["Cached target is stale alternate."], "regime_memory_revise": True, "alternate_target_id": "stale-alt"},
        ),
        "user_visible_exposure": (
            {"observability": 1, "user_burden": 0},
            {"observability": 3, "user_burden": 3},
        ),
        "compensation_or_payment_hold": (
            {"compensation_cost": 0, "payment_sensitive": False},
            {"compensation_cost": 2, "payment_sensitive": True},
        ),
    }
    return variants[field]


def _stress_label(field: str, variant: str) -> dict[str, Any]:
    if variant == "safe":
        return {
            "terminal_success": True,
            "terminal_equivalence_class": f"stress:{field}",
            "effect_vector": json.dumps(
                {
                    "compensation_cost": 0,
                    "contract_fragility": 1,
                    "data_scope": 1,
                    "observability": 1,
                    "reversibility": 1,
                    "user_burden": 0,
                    "write_scope": 2,
                },
                sort_keys=True,
            ),
            "verdict": "minimal",
        }
    return {
        "terminal_success": True,
        "terminal_equivalence_class": f"stress:{field}",
        "effect_vector": json.dumps(
            {
                "compensation_cost": 3,
                "contract_fragility": 3,
                "data_scope": 3,
                "observability": 3,
                "reversibility": 3,
                "user_burden": 3,
                "write_scope": 4,
            },
            sort_keys=True,
        ),
        "verdict": "strict_excess",
    }


def _targeted_stress_audit(fields: list[str]) -> pd.DataFrame:
    rows = []
    for field in fields:
        if field not in STRESS_FIELDS:
            continue
        safe_value, risky_value = _stress_variants(field)
        for variant, value in (("safe", safe_value), ("risky", risky_value)):
            features = _base_stress_features(field)
            features[field] = value
            label = _stress_label(field, variant)
            rows.append(
                {
                    "trace_id": f"stage6_cegar_stress:{field}:{variant}",
                    "family": "cegar_targeted_stress",
                    "regime": "TARGETED_CEGAR",
                    "model": "deterministic_stress",
                    "system": "CEGAR_STRESS",
                    "features": features,
                    "full_hash": _stable_hash(features),
                    "label": label,
                    "label_hash": _stable_hash(label),
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True)
    parser.add_argument("--certificates")
    parser.add_argument("--schemas")
    parser.add_argument("--omit-fields", nargs="+", required=True)
    parser.add_argument("--inject-targeted-cases", action="store_true")
    parser.add_argument("--stress-targets", nargs="+", default=list(STRESS_FIELDS))
    parser.add_argument("--out", required=True)
    parser.add_argument("--label-changes", required=True)
    args = parser.parse_args()

    traces = pd.read_parquet(args.traces)
    if "verdict" not in traces.columns:
        candidate_paths = []
        if args.certificates:
            candidate_paths.append(Path(args.certificates))
        trace_parent = Path(args.traces).parent
        candidate_paths.extend(
            [
                trace_parent / "kernel_canonical" / "certificates_enumerated.parquet",
                trace_parent / "kernel" / "certificates.parquet",
            ]
        )
        cert_path = next((path for path in candidate_paths if path.exists()), None)
        if cert_path:
            certs = pd.read_parquet(cert_path)[["trace_id", "verdict"]]
            traces = traces.merge(certs, on="trace_id", how="left", validate="one_to_one")
        else:
            traces["verdict"] = ""
    audit = _prepare(traces)
    if args.inject_targeted_cases:
        audit = pd.concat([audit, _targeted_stress_audit(args.stress_targets)], ignore_index=True)

    summary_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for field in args.omit_fields:
        if field not in FUTURE_FIELDS:
            summary_rows.append(
                {
                    "omitted_field": field,
                    "total_reduced_groups": 0,
                    "collision_groups": 0,
                    "label_change_groups": 0,
                    "rejected_abstractions": 0,
                    "affected_rows": 0,
                    "reason": "unknown_or_unmodelled_field",
                }
            )
            continue
        reduced_hashes = []
        for features in audit["features"]:
            reduced = dict(features)
            reduced.pop(field, None)
            reduced_hashes.append(_stable_hash(reduced))
        audit_field = audit.assign(reduced_hash=reduced_hashes)
        total_groups = int(audit_field["reduced_hash"].nunique())
        collision_groups = 0
        label_change_groups = 0
        affected_rows = 0
        for reduced_hash, group in audit_field.groupby("reduced_hash", sort=False):
            distinct_full = int(group["full_hash"].nunique())
            distinct_labels = int(group["label_hash"].nunique())
            if distinct_full > 1:
                collision_groups += 1
            if distinct_full > 1 and distinct_labels > 1:
                label_change_groups += 1
                affected_rows += int(len(group))
                examples = group.head(6)
                detail_rows.append(
                    {
                        "omitted_field": field,
                        "reduced_hash": reduced_hash,
                        "affected_rows": int(len(group)),
                        "distinct_full_states": distinct_full,
                        "distinct_labels": distinct_labels,
                        "example_trace_ids": "|".join(examples["trace_id"].astype(str)),
                        "example_systems": "|".join(examples["system"].astype(str)),
                        "example_verdicts": "|".join(str(item.get("verdict", "")) for item in examples["label"]),
                        "example_effect_vectors": "|".join(str(item.get("effect_vector", "")) for item in examples["label"]),
                    }
                )
        summary_rows.append(
            {
                "omitted_field": field,
                "total_reduced_groups": total_groups,
                "collision_groups": collision_groups,
                "label_change_groups": label_change_groups,
                "rejected_abstractions": label_change_groups,
                "affected_rows": affected_rows,
                "reason": "reduced_hash_label_collision" if label_change_groups else "no_label_collision_observed",
            }
        )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary_rows).to_csv(args.out, index=False)
    pd.DataFrame(detail_rows).to_csv(args.label_changes, index=False)
    print(f"wrote {args.out} and {args.label_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
