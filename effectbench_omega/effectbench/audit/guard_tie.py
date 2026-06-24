#!/usr/bin/env python3
"""Explain PROJ_GUARD vs EFFECTGUARD near-ties."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def _action_names(payload: str) -> list[str]:
    try:
        return [str(item.get("action", "")) for item in json.loads(payload)]
    except Exception:
        return []


def _join(traces: pd.DataFrame, certs: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "trace_id",
        "task_id",
        "family",
        "regime",
        "seed",
        "model",
        "system",
        "scenario",
        "policy_obligation",
        "actions",
        "guard_decisions",
        "model_proposed_actions",
        "model_proposal_parse_status",
        "model_proposal_repair_log",
        "added_user_turns",
    ]
    merged = certs.merge(traces[cols], on=["trace_id", "task_id", "family", "regime", "seed", "model", "system"], how="left")
    merged["action_names"] = merged["actions"].apply(_action_names)
    merged["strict_excess"] = merged["verdict"].eq("strict_excess")
    return merged


def _unit_diff(merged: pd.DataFrame, pair: list[str]) -> pd.DataFrame:
    subset = merged[merged["system"].isin(pair)].copy()
    index = ["task_id", "family", "regime", "seed", "model", "scenario", "policy_obligation"]
    rows: list[dict[str, Any]] = []
    for key, group in subset.groupby(index, dropna=False, sort=False):
        by_system = {row.system: row for row in group.itertuples(index=False)}
        if not all(system in by_system for system in pair):
            continue
        proj = by_system[pair[0]]
        effect = by_system[pair[1]]
        rows.append(
            {
                **dict(zip(index, key)),
                "left_system": pair[0],
                "right_system": pair[1],
                "proj_trace_id": proj.trace_id,
                "effect_trace_id": effect.trace_id,
                "proj_verdict": proj.verdict,
                "effect_verdict": effect.verdict,
                "proj_strict": bool(proj.strict_excess),
                "effect_strict": bool(effect.strict_excess),
                "same_verdict": proj.verdict == effect.verdict,
                "same_effect_vector": proj.effect_vector == effect.effect_vector,
                "same_actions": proj.action_names == effect.action_names,
                "proj_actions": "|".join(proj.action_names),
                "effect_actions": "|".join(effect.action_names),
                "proj_added_user_turns": int(proj.added_user_turns),
                "effect_added_user_turns": int(effect.added_user_turns),
                "proj_parse_status": proj.model_proposal_parse_status,
                "effect_parse_status": effect.model_proposal_parse_status,
                "proj_guard_decisions": proj.guard_decisions,
                "effect_guard_decisions": effect.guard_decisions,
            }
        )
    return pd.DataFrame(rows)


def _rate_table(units: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "group": "overall",
                "key": "all",
                "units": int(len(units)),
                "proj_strict_rate": float(units["proj_strict"].mean()),
                "effect_strict_rate": float(units["effect_strict"].mean()),
                "proj_minus_effect_strict_rate": float((units["proj_strict"].astype(int) - units["effect_strict"].astype(int)).mean()),
                "same_actions_rate": float(units["same_actions"].mean()),
                "same_effect_vector_rate": float(units["same_effect_vector"].mean()),
                "same_verdict_rate": float(units["same_verdict"].mean()),
            }
        ]
    )


def _group_rates(units: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    for key, group in units.groupby(column, dropna=False):
        rows.append(
            {
                "group": column,
                "key": key,
                "units": int(len(group)),
                "proj_strict_rate": float(group["proj_strict"].mean()),
                "effect_strict_rate": float(group["effect_strict"].mean()),
                "proj_minus_effect_strict_rate": float((group["proj_strict"].astype(int) - group["effect_strict"].astype(int)).mean()),
                "same_actions_rate": float(group["same_actions"].mean()),
                "same_effect_vector_rate": float(group["same_effect_vector"].mean()),
                "same_verdict_rate": float(group["same_verdict"].mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--systems", nargs=2, default=["PROJ_GUARD", "EFFECTGUARD"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--details-out")
    args = parser.parse_args()

    traces = pd.read_parquet(args.traces)
    certs = pd.read_parquet(args.certificates)
    merged = _join(traces, certs)
    units = _unit_diff(merged, args.systems)
    rates = pd.concat(
        [
            _rate_table(units),
            _group_rates(units, "model"),
            _group_rates(units, "family"),
            _group_rates(units, "regime"),
            _group_rates(units, "policy_obligation"),
        ],
        ignore_index=True,
    )
    details_out = Path(args.details_out) if args.details_out else Path(args.out).with_suffix(".details.csv")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    details_out.parent.mkdir(parents=True, exist_ok=True)
    rates.to_csv(args.out, index=False)
    units[~units["same_verdict"] | ~units["same_actions"]].to_csv(details_out, index=False)

    overall = rates.iloc[0]
    verdict_diff = int((~units["same_verdict"]).sum())
    action_diff = int((~units["same_actions"]).sum())
    report_path = Path(args.out).with_suffix(".md")
    report_path.write_text(
        "\n".join(
            [
                f"# {args.systems[0]} vs {args.systems[1]} Tie Audit",
                "",
                f"paired_units: {int(overall['units'])}",
                f"proj_strict_rate: {overall['proj_strict_rate']:.6f}",
                f"effect_strict_rate: {overall['effect_strict_rate']:.6f}",
                f"proj_minus_effect_strict_rate: {overall['proj_minus_effect_strict_rate']:.6f}",
                f"same_actions_rate: {overall['same_actions_rate']:.6f}",
                f"same_effect_vector_rate: {overall['same_effect_vector_rate']:.6f}",
                f"same_verdict_rate: {overall['same_verdict_rate']:.6f}",
                f"verdict_diff_units: {verdict_diff}",
                f"action_diff_units: {action_diff}",
                "",
                "Interpretation: near-tie means both guards usually collapse to the same lower-effect suffix in the current local policy implementation. Inspect the details CSV for the few units where decisions diverge.",
                "",
            ]
        )
    )
    print(f"wrote {args.out}, {details_out}, and {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
