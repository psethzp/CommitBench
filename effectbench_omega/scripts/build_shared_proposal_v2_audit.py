#!/usr/bin/env python3
"""Build a shared-proposal V2 guard audit split from frozen BASE proposals."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from effectbench.agents.systems import run_system
from effectbench.effects import dumps
from effectbench.util import stable_hash, write_jsonl


DEFAULT_SYSTEMS = ["BASE", "PROJ_GUARD_V2", "EFFECTGUARD_V2"]
DERIVED_COLUMNS = {
    "trace_id",
    "split",
    "terminal_success",
    "raw_success",
    "terminal_equivalence_class",
    "effect_vector",
    "actions",
    "guard_decisions",
    "added_user_turns",
    "false_denial",
    "model_raw_output",
    "model_proposed_actions",
    "model_proposal_parse_status",
    "model_proposal_repair_log",
}
SHARED_COLUMNS = {
    "shared_proposal_source_trace_id",
    "shared_proposal_source_system",
    "shared_proposal_source_split",
    "shared_proposal_source_parse_status",
    "shared_proposal_source_actions",
    "shared_proposal_policy",
    "proposal_prompt_caveat",
}


def _json_loads_or_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _base_fields(row: pd.Series) -> dict[str, Any]:
    data = row.to_dict()
    for column in [*DERIVED_COLUMNS, *SHARED_COLUMNS]:
        data.pop(column, None)
    if "turns" in data:
        data["turns"] = _json_loads_or_value(data["turns"])
    return data


def _trace_row(
    source: pd.Series,
    row: dict[str, Any],
    system: str,
    split: str,
    episode: Any,
    shared_proposal_policy: str,
    proposal_prompt_caveat: str,
) -> dict[str, Any]:
    trace_id = stable_hash(
        {
            "task_id": row["task_id"],
            "model": row["model"],
            "system": system,
            "split": split,
            "shared_proposal_source_trace_id": source["trace_id"],
        }
    )
    output = {
        **{key: value for key, value in row.items() if key != "turns"},
        "system": system,
        "trace_id": trace_id,
        "split": split,
        "terminal_success": episode.terminal_success,
        "raw_success": episode.terminal_success,
        "terminal_equivalence_class": episode.terminal_equivalence_class,
        "effect_vector": dumps(episode.effect_vector),
        "actions": episode.actions_json(),
        "guard_decisions": episode.guard_json(),
        "added_user_turns": episode.added_user_turns,
        "false_denial": episode.false_denial,
        "model_raw_output": source.get("model_raw_output"),
        "model_proposed_actions": json.dumps(episode.model_proposed_actions, sort_keys=True),
        "model_proposal_parse_status": episode.model_proposal_parse_status,
        "model_proposal_repair_log": json.dumps(episode.model_proposal_repair_log, sort_keys=True),
        "turns": json.dumps(row.get("turns", []), sort_keys=True),
        "shared_proposal_source_trace_id": source["trace_id"],
        "shared_proposal_source_system": source["system"],
        "shared_proposal_source_split": source["split"],
        "shared_proposal_source_parse_status": source.get("model_proposal_parse_status", ""),
        "shared_proposal_source_actions": source.get("model_proposed_actions", ""),
        "shared_proposal_policy": shared_proposal_policy,
        "proposal_prompt_caveat": proposal_prompt_caveat,
    }
    if episode.native_metadata:
        output.update(
            {
                "native_execution": True,
                "native_state_before_hash": episode.native_metadata.get("state_before_hash", ""),
                "native_state_after_hash": episode.native_metadata.get("state_after_hash", ""),
                "native_success_reason": episode.native_metadata.get("success_reason", ""),
                "native_replay_status": episode.native_metadata.get("replay_status", ""),
                "native_failure_possible": bool(episode.native_metadata.get("failure_possible", False)),
                "native_state_delta_ledger": json.dumps(
                    episode.native_metadata.get("state_delta_ledger", []),
                    sort_keys=True,
                ),
            }
        )
    return output


def _ledger_rows(trace_row: dict[str, Any]) -> list[dict[str, Any]]:
    actions = json.loads(trace_row["actions"])
    rows = []
    for action in actions:
        rows.append(
            {
                "trace_id": trace_row["trace_id"],
                "task_id": trace_row["task_id"],
                "family": trace_row["family"],
                "regime": trace_row["regime"],
                "seed": trace_row["seed"],
                "model": trace_row["model"],
                "system": trace_row["system"],
                "step": action["step"],
                "action": action["action"],
                "target_id": action["target_id"],
                "effect_vector": action["effect_vector"],
                "rationale": action["rationale"],
                "shared_proposal_source_trace_id": trace_row["shared_proposal_source_trace_id"],
            }
        )
    return rows


def _runtime_row(trace_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": trace_row["trace_id"],
        "system": trace_row["system"],
        "task_id": trace_row["task_id"],
        "forbidden_oracle_fields_seen": [],
        "guard_decisions": trace_row["guard_decisions"],
        "model_proposed_actions": json.loads(trace_row["model_proposed_actions"]),
        "model_proposal_parse_status": trace_row["model_proposal_parse_status"],
        "shared_proposal_source_trace_id": trace_row["shared_proposal_source_trace_id"],
        "shared_proposal_policy": trace_row["shared_proposal_policy"],
    }


def _api_row(trace_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": 0,
        "provider": "offline_shared_proposal_replay",
        "model_id": trace_row["model"],
        "logical_model": trace_row["model"],
        "region": "local_artifact",
        "request_id": "",
        "retry_count": 0,
        "batch_or_on_demand": "offline_replay",
        "raw_input_tokens": 0,
        "cached_input_tokens": 0,
        "billable_input_tokens": 0,
        "output_tokens": 0,
        "input_rate": 0,
        "cached_input_rate": 0,
        "output_rate": 0,
        "cost_usd": 0,
        "status": "replayed_from_frozen_base_proposal",
        "error_type": "",
        "latency_s": 0,
        "raw_output": trace_row["model_raw_output"],
        "system": trace_row["system"],
        "task_id": trace_row["task_id"],
        "family": trace_row["family"],
        "regime": trace_row["regime"],
        "seed": trace_row["seed"],
        "shared_proposal_source_trace_id": trace_row["shared_proposal_source_trace_id"],
    }


def _summarize(
    traces: pd.DataFrame,
    failures: list[dict[str, Any]],
    residual_caveat: str,
) -> dict[str, Any]:
    systems = sorted(traces["system"].astype(str).unique())
    key_cols = ["task_id", "base_task_id", "family", "regime", "seed", "model"]
    group_count = int(traces[key_cols].drop_duplicates().shape[0])
    expected_shared = int(group_count * len(systems))
    source_counts = traces.groupby("shared_proposal_source_trace_id")["system"].nunique()
    proposal_actions_equal = 0
    for _, group in traces.groupby(key_cols):
        signatures = set(group["model_proposed_actions"].astype(str).tolist())
        if len(signatures) == 1:
            proposal_actions_equal += 1
    parse_counts = (
        traces.groupby(["system", "model_proposal_parse_status"])
        .size()
        .reset_index(name="rows")
        .sort_values(["system", "model_proposal_parse_status"])
        .to_dict(orient="records")
    )
    source_parse_counts = Counter(traces["shared_proposal_source_parse_status"].astype(str))
    return {
        "split_trace_count": int(len(traces)),
        "group_count": group_count,
        "systems": systems,
        "expected_shared_rows": expected_shared,
        "complete_shared_source_groups": int((source_counts == len(systems)).sum()),
        "incomplete_shared_source_groups": int((source_counts != len(systems)).sum()),
        "proposal_actions_equal_groups": int(proposal_actions_equal),
        "proposal_actions_unequal_groups": int(group_count - proposal_actions_equal),
        "failures": int(len(failures)),
        "parse_counts": parse_counts,
        "source_parse_counts": dict(sorted(source_parse_counts.items())),
        "gpu_used": False,
        "new_model_calls": 0,
        "prompt_fix_for_future_runs": "run_online.py no longer includes system=... in proposal user content",
        "residual_caveat": residual_caveat,
    }


def _write_reports(summary: dict[str, Any], out: Path, table_out: Path, report_out: Path) -> None:
    pd.DataFrame(
        [
            {
                "metric": key,
                "value": json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value,
            }
            for key, value in summary.items()
        ]
    ).to_csv(table_out, index=False)
    lines = [
        "# Shared-Proposal V2 Audit",
        "",
        "This audit replays every V2 system from the exact same frozen BASE model proposal for each task/model/regime/seed.",
        "It is an offline paired-control audit: no GPU and no new model calls were used.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Trace rows | {summary['split_trace_count']:,} |",
        f"| Shared groups | {summary['group_count']:,} |",
        f"| Complete source groups | {summary['complete_shared_source_groups']:,} |",
        f"| Proposal-action equality groups | {summary['proposal_actions_equal_groups']:,} |",
        f"| Failures | {summary['failures']:,} |",
        f"| New model calls | {summary['new_model_calls']:,} |",
        "",
        "## Systems",
        "",
        ", ".join(f"`{system}`" for system in summary["systems"]),
        "",
        "## Parse Counts",
        "",
        "| System | Parse status | Rows |",
        "|---|---|---:|",
    ]
    for row in summary["parse_counts"]:
        lines.append(f"| `{row['system']}` | `{row['model_proposal_parse_status']}` | {row['rows']:,} |")
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            summary["residual_caveat"],
            "",
            f"Split artifact: `{out}`.",
        ]
    )
    report_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-split", default="effectbench_omega/outputs/guard_v2_main_with_base_all_local")
    parser.add_argument("--out", default="effectbench_omega/outputs/shared_proposal_v2_audit_all_local")
    parser.add_argument("--split", default="shared_proposal_v2_audit_all_local")
    parser.add_argument("--systems", nargs="+", default=DEFAULT_SYSTEMS)
    parser.add_argument("--table-out", default="effectbench_omega/tables/shared_proposal_v2_audit.csv")
    parser.add_argument("--report-out", default="effectbench_omega/reports/shared_proposal_v2_audit.md")
    parser.add_argument(
        "--shared-proposal-policy",
        default="frozen_BASE_model_raw_output_replayed_to_all_systems",
    )
    parser.add_argument(
        "--proposal-prompt-caveat",
        default=(
            "source BASE proposal came from the legacy pre-2026-06-26 prompt that included system=BASE; "
            "this audit removes between-system proposal-distribution differences but is not a no-system-prompt rerun"
        ),
    )
    parser.add_argument(
        "--residual-caveat",
        default=(
            "The audit replays BASE proposals generated before the no-system prompt fix, so it tests guard-comparison "
            "proposal sharing rather than the distribution of a fresh no-system prompt."
        ),
    )
    args = parser.parse_args()

    base_split = Path(args.base_split)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    Path(args.table_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)

    source_df = pd.read_parquet(base_split / "traces.parquet")
    base_rows = source_df[source_df["system"].astype(str) == "BASE"].copy()
    if base_rows.empty:
        raise SystemExit(f"no BASE rows found in {base_split}/traces.parquet")

    traces: list[dict[str, Any]] = []
    ledgers: list[dict[str, Any]] = []
    runtime_logs: list[dict[str, Any]] = []
    api_logs: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for _, source in base_rows.iterrows():
        source_advice = source.get("model_raw_output")
        for system in args.systems:
            row = _base_fields(source)
            row["system"] = system
            try:
                episode = run_system(row, model_advice=source_advice)
                trace_row = _trace_row(
                    source,
                    row,
                    system,
                    args.split,
                    episode,
                    args.shared_proposal_policy,
                    args.proposal_prompt_caveat,
                )
                traces.append(trace_row)
                ledgers.extend(_ledger_rows(trace_row))
                runtime_logs.append(_runtime_row(trace_row))
                api_logs.append(_api_row(trace_row))
            except Exception as exc:
                failures.append(
                    {
                        "source_trace_id": source.get("trace_id"),
                        "task_id": source.get("task_id"),
                        "model": source.get("model"),
                        "system": system,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )

    traces_df = pd.DataFrame(traces)
    traces_df.to_parquet(out / "traces.parquet", index=False)
    pd.DataFrame(ledgers).to_parquet(out / "tool_ledgers.parquet", index=False)
    pd.DataFrame(runtime_logs).to_parquet(out / "runtime_logs.parquet", index=False)
    write_jsonl(out / "api_logs.jsonl", api_logs)
    write_jsonl(out / "failures.jsonl", failures)

    summary = _summarize(traces_df, failures, args.residual_caveat)
    (out / "shared_proposal_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_reports(summary, out, Path(args.table_out), Path(args.report_out))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
