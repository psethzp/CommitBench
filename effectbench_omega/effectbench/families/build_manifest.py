#!/usr/bin/env python3
"""Build deterministic manifests for the minimal-plus suite."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from effectbench.families.catalog import build_base_tasks
from effectbench.util import stable_hash


DEFAULT_REGIMES = ["FULL", "CONCAT", "SHARDED", "SNOWBALL", "REVISE", "MEMORY_REVISE", "ADV_EFFECT"]
DEFAULT_SEEDS = [13, 47]
DEFAULT_MODELS = [
    "mistral_small_3_2_24b_local",
    "qwen3_6_35b_a3b_local",
    "gemma3_27b_it_local",
    "llama3_3_70b_awq_local",
]
DEFAULT_SYSTEMS = ["BASE", "PROJ_GUARD", "EFFECTGUARD"]


def build_rows(
    regimes: list[str] | None = None,
    seeds: list[int] | None = None,
    models: list[str] | None = None,
    systems: list[str] | None = None,
    limit_base_tasks: int | None = None,
) -> list[dict[str, str | int]]:
    regimes = regimes or DEFAULT_REGIMES
    seeds = seeds or DEFAULT_SEEDS
    models = models or DEFAULT_MODELS
    systems = systems or DEFAULT_SYSTEMS
    base_tasks = build_base_tasks()
    if limit_base_tasks is not None:
        base_tasks = base_tasks[:limit_base_tasks]

    rows: list[dict[str, str | int]] = []
    for task in base_tasks:
        for regime in regimes:
            for seed in seeds:
                task_hash = stable_hash({"task": task.to_dict(), "regime": regime, "seed": seed})
                for model in models:
                    for system in systems:
                        rows.append(
                            {
                                "task_id": f"{task.base_task_id}:{regime}:s{seed}",
                                "base_task_id": task.base_task_id,
                                "family": task.family,
                                "source_benchmark": task.source_benchmark,
                                "source_commit": task.source_commit,
                                "scenario": task.scenario,
                                "regime": regime,
                                "seed": seed,
                                "model": model,
                                "system": system,
                                "task_hash": task_hash,
                                "policy_hash": stable_hash(task.policy_obligation),
                                "tool_schema_hash": stable_hash({"tool_schema": "minimal_plus_v1"}),
                                "effect_schema_hash": stable_hash({"effect_schema": "seven_dim_v1"}),
                                "terminal_equivalence_hash": task.terminal_equivalence_hash,
                                "target_id": task.target_id,
                                "alternate_target_id": task.alternate_target_id,
                                "user_goal": task.user_goal,
                                "policy_obligation": task.policy_obligation,
                                "contract_artifact_hash": task.contract_artifact_hash,
                                "source_native_id": task.source_native_id,
                                "source_path": task.source_path,
                                "source_hash": task.source_hash,
                                "native_instruction": task.native_instruction,
                                "expected_action_names": task.expected_action_names,
                                "expected_actions_hash": task.expected_actions_hash,
                                "adapter_status": task.adapter_status,
                            }
                        )
    return rows


def write_manifest(rows: list[dict[str, str | int]], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--out", required=True)
    parser.add_argument("--regimes", nargs="+", default=DEFAULT_REGIMES)
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--systems", nargs="+", default=DEFAULT_SYSTEMS)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--limit-base-tasks", type=int)
    args = parser.parse_args()

    rows = build_rows(
        regimes=args.regimes,
        seeds=args.seeds,
        models=args.models,
        systems=args.systems,
        limit_base_tasks=args.limit_base_tasks,
    )
    write_manifest(rows, args.out)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
