#!/usr/bin/env python3
"""Build the Stage 5 native-fidelity subset manifest."""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from pathlib import Path

from effectbench.families.catalog import TaskTemplate, build_base_tasks
from effectbench.util import stable_hash


DEFAULT_REGIMES = ["FULL", "SHARDED", "MEMORY_REVISE", "ADV_EFFECT"]
DEFAULT_SEEDS = [13, 47]
DEFAULT_MODELS = [
    "mistral_small_3_2_24b_local",
    "qwen3_6_35b_a3b_local",
    "gemma3_27b_it_local",
    "llama3_3_70b_awq_local",
]
DEFAULT_SYSTEMS = ["BASE", "PROJ_GUARD_V2", "EFFECTGUARD_V2"]
SOURCE_TO_NATIVE = {
    "tau_retail": "tau_retail_native",
    "tau_airline": "tau_airline_native",
    "telecom": "tau2_telecom_native",
    "toolsandbox_contract": "toolsandbox_contract_native",
}


def _native_task(task: TaskTemplate, native_family: str, native_index: int) -> TaskTemplate:
    payload = {
        "native_family": native_family,
        "source_native_id": task.source_native_id,
        "source_hash": task.source_hash,
        "target_id": task.target_id,
        "policy_obligation": task.policy_obligation,
    }
    return replace(
        task,
        base_task_id=f"{native_family}_{native_index:03d}",
        family=native_family,
        terminal_equivalence_hash=stable_hash({"native_terminal": payload}),
    )


def _select_tasks(counts: dict[str, int]) -> list[TaskTemplate]:
    base_tasks = build_base_tasks()
    grouped: dict[str, list[TaskTemplate]] = {family: [] for family in SOURCE_TO_NATIVE}
    for task in base_tasks:
        if task.family in grouped:
            grouped[task.family].append(task)

    selected: list[TaskTemplate] = []
    for source_family, count in counts.items():
        native_family = SOURCE_TO_NATIVE[source_family]
        candidates = grouped.get(source_family, [])
        if len(candidates) < count:
            raise ValueError(f"family {source_family} has {len(candidates)} source tasks, needs {count}")
        for index, task in enumerate(candidates[:count]):
            selected.append(_native_task(task, native_family, index))
    return selected


def build_rows(
    tau_retail: int,
    tau_airline: int,
    telecom: int,
    toolsandbox_contract: int,
    regimes: list[str],
    seeds: list[int],
    models: list[str],
    systems: list[str],
) -> list[dict[str, str | int | bool]]:
    tasks = _select_tasks(
        {
            "tau_retail": tau_retail,
            "tau_airline": tau_airline,
            "telecom": telecom,
            "toolsandbox_contract": toolsandbox_contract,
        }
    )
    rows: list[dict[str, str | int | bool]] = []
    for task in tasks:
        for regime in regimes:
            for seed in seeds:
                task_hash = stable_hash(
                    {
                        "task": task.to_dict(),
                        "regime": regime,
                        "seed": seed,
                        "native_execution": True,
                    }
                )
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
                                "tool_schema_hash": stable_hash({"tool_schema": "native_subset_v1"}),
                                "effect_schema_hash": stable_hash({"effect_schema": "state_delta_v1"}),
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
                                "native_execution": True,
                                "native_wrapper": task.family,
                                "native_success_predicate": "final_state_or_expected_action_criteria_v1",
                                "native_effect_ledger_source": "state_delta",
                            }
                        )
    return rows


def write_manifest(rows: list[dict[str, str | int | bool]], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--tau-retail", type=int, default=16)
    parser.add_argument("--tau-airline", type=int, default=16)
    parser.add_argument("--telecom", type=int, default=8)
    parser.add_argument("--toolsandbox-contract", type=int, default=8)
    parser.add_argument("--regimes", nargs="+", default=DEFAULT_REGIMES)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--systems", nargs="+", default=DEFAULT_SYSTEMS)
    args = parser.parse_args()

    rows = build_rows(
        tau_retail=args.tau_retail,
        tau_airline=args.tau_airline,
        telecom=args.telecom,
        toolsandbox_contract=args.toolsandbox_contract,
        regimes=args.regimes,
        seeds=args.seeds,
        models=args.models,
        systems=args.systems,
    )
    write_manifest(rows, args.out)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
