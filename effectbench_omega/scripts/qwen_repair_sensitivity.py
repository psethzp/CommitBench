#!/usr/bin/env python3
"""Prepare and summarize the Qwen same-prompt repair sensitivity rerun."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from effectbench.kernel.verifier import verify


QWEN_MODEL = "qwen3_6_35b_a3b_local"
ORIGINAL_SPLIT = "main_mc_postfix_all_local"
ORIGINAL_QWEN_SPLIT = "main_mc_postfix_qwen3_6_35b_a3b_local"
KEY_COLS = ["task_id", "regime", "seed", "model", "system"]


def _repair_nonempty(value: Any) -> bool:
    try:
        return len(json.loads(value)) > 0
    except Exception:
        return str(value) not in {"", "[]", "nan", "None"}


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _affected_traces(original_traces: pd.DataFrame) -> pd.DataFrame:
    qwen = original_traces[original_traces["model"].eq(QWEN_MODEL)].copy()
    return qwen[qwen["model_proposal_repair_log"].map(_repair_nonempty)].copy()


def prepare(args: argparse.Namespace) -> int:
    original_traces = pd.read_parquet(args.original_traces)
    manifest = pd.read_csv(args.source_manifest, dtype=str)
    affected = _affected_traces(original_traces)
    affected_keys = set(map(tuple, affected[KEY_COLS].astype(str).to_numpy()))
    manifest_keys = list(map(tuple, manifest[KEY_COLS].astype(str).to_numpy()))
    selected = manifest[[key in affected_keys for key in manifest_keys]].copy()

    if len(selected) != len(affected):
        raise RuntimeError(f"selected {len(selected)} manifest rows, expected {len(affected)} affected traces")

    out = Path(args.manifest_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(out, index=False)

    summary = {
        "model": QWEN_MODEL,
        "affected_rows": int(len(affected)),
        "repair_fallback_rows": int(affected["model_proposal_parse_status"].astype(str).str.contains("repair_fallback").sum()),
        "text_scan_rows": int(affected["model_proposal_parse_status"].astype(str).eq("text_scan").sum()),
        "systems": affected["system"].value_counts().sort_index().to_dict(),
        "regimes": affected["regime"].value_counts().sort_index().to_dict(),
        "manifest_out": str(out),
    }
    summary_out = Path(args.summary_out) if args.summary_out else out.with_suffix(".summary.json")
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _merge_parquet_by_trace_id(original_path: Path, rerun_path: Path, affected_ids: set[str], out_path: Path) -> pd.DataFrame:
    original = pd.read_parquet(original_path)
    rerun = pd.read_parquet(rerun_path)
    merged = pd.concat([original[~original["trace_id"].isin(affected_ids)], rerun], ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    return merged


def _api_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    model = str(row.get("logical_model") or row.get("model_id") or "")
    return (
        str(row.get("task_id")),
        str(row.get("regime")),
        str(row.get("seed")),
        model,
        str(row.get("system")),
    )


def _write_merged_jsonl(original_path: Path, rerun_path: Path, affected_keys: set[tuple[str, ...]], out_path: Path) -> None:
    original = [row for row in _jsonl_rows(original_path) if _api_key(row) not in affected_keys]
    rerun = _jsonl_rows(rerun_path)
    _write_jsonl(out_path, [*original, *rerun])


def _write_kernel_outputs(traces: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    certs, frontiers, prune_log, summary = verify(traces)
    out_dir.mkdir(parents=True, exist_ok=True)
    certs.to_parquet(out_dir / "certificates.parquet", index=False)
    frontiers.to_parquet(out_dir / "frontiers.parquet", index=False)
    prune_log.to_parquet(out_dir / "prune_log.parquet", index=False)
    pd.DataFrame(columns=["abstract_hash", "reason", "field"]).to_parquet(
        out_dir / "rejected_abstractions.parquet",
        index=False,
    )
    (out_dir / "verifier_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return certs


def _strict_rate(certs: pd.DataFrame, mask: pd.Series | None = None) -> float:
    subset = certs if mask is None else certs[mask]
    if subset.empty:
        return 0.0
    return float(subset["verdict"].eq("strict_excess").mean())


def _rate_delta_pp(new: float, old: float) -> float:
    return (new - old) * 100.0


def report(args: argparse.Namespace) -> int:
    original_dir = Path(args.original_dir)
    rerun_dir = Path(args.rerun_dir)
    merged_dir = Path(args.merged_out)
    table_out = Path(args.table_out)
    report_out = Path(args.report_out)

    original_traces = pd.read_parquet(original_dir / "traces.parquet")
    affected = _affected_traces(original_traces)
    affected_ids = set(affected["trace_id"].astype(str))
    affected_keys = set(map(tuple, affected[KEY_COLS].astype(str).to_numpy()))

    rerun_traces = pd.read_parquet(rerun_dir / "traces.parquet")
    rerun_ids = set(rerun_traces["trace_id"].astype(str))
    missing_ids = sorted(affected_ids - rerun_ids)
    extra_ids = sorted(rerun_ids - affected_ids)
    if missing_ids or extra_ids:
        raise RuntimeError(f"rerun trace-id mismatch: missing={len(missing_ids)} extra={len(extra_ids)}")

    merged_traces = _merge_parquet_by_trace_id(
        original_dir / "traces.parquet",
        rerun_dir / "traces.parquet",
        affected_ids,
        merged_dir / "traces.parquet",
    )
    _merge_parquet_by_trace_id(
        original_dir / "tool_ledgers.parquet",
        rerun_dir / "tool_ledgers.parquet",
        affected_ids,
        merged_dir / "tool_ledgers.parquet",
    )
    _merge_parquet_by_trace_id(
        original_dir / "runtime_logs.parquet",
        rerun_dir / "runtime_logs.parquet",
        affected_ids,
        merged_dir / "runtime_logs.parquet",
    )
    _write_merged_jsonl(
        original_dir / "api_logs.jsonl",
        rerun_dir / "api_logs.jsonl",
        affected_keys,
        merged_dir / "api_logs.jsonl",
    )
    _write_jsonl(merged_dir / "failures.jsonl", _jsonl_rows(rerun_dir / "failures.jsonl"))

    original_certs = pd.read_parquet(original_dir / "kernel" / "certificates.parquet")
    sensitivity_certs = _write_kernel_outputs(merged_traces, merged_dir / "kernel")

    original_by_trace = original_traces.set_index("trace_id")
    rerun_by_trace = rerun_traces.set_index("trace_id")
    original_affected_certs = original_certs[original_certs["trace_id"].isin(affected_ids)].set_index("trace_id")
    rerun_affected_certs = sensitivity_certs[sensitivity_certs["trace_id"].isin(affected_ids)].set_index("trace_id")

    original_qwen_mask = original_certs["model"].eq(QWEN_MODEL)
    sensitivity_qwen_mask = sensitivity_certs["model"].eq(QWEN_MODEL)
    original_overall_strict = _strict_rate(original_certs)
    sensitivity_overall_strict = _strict_rate(sensitivity_certs)
    original_qwen_strict = _strict_rate(original_certs, original_qwen_mask)
    sensitivity_qwen_strict = _strict_rate(sensitivity_certs, sensitivity_qwen_mask)

    proposal_changed = 0
    effect_changed = 0
    verdict_changed = 0
    for trace_id in sorted(affected_ids):
        if original_by_trace.loc[trace_id, "model_proposed_actions"] != rerun_by_trace.loc[trace_id, "model_proposed_actions"]:
            proposal_changed += 1
        if original_by_trace.loc[trace_id, "effect_vector"] != rerun_by_trace.loc[trace_id, "effect_vector"]:
            effect_changed += 1
        if original_affected_certs.loc[trace_id, "verdict"] != rerun_affected_certs.loc[trace_id, "verdict"]:
            verdict_changed += 1

    rerun_repair_nonempty = int(rerun_traces["model_proposal_repair_log"].map(_repair_nonempty).sum())
    rerun_repair_fallback = int(
        rerun_traces["model_proposal_parse_status"].astype(str).str.contains("repair_fallback").sum()
    )
    original_repair_fallback = int(
        affected["model_proposal_parse_status"].astype(str).str.contains("repair_fallback").sum()
    )

    payload = {
        "affected_rows": int(len(affected)),
        "rerun_rows": int(len(rerun_traces)),
        "original_repair_nonempty_rows": int(len(affected)),
        "rerun_repair_nonempty_rows": rerun_repair_nonempty,
        "original_repair_fallback_rows": original_repair_fallback,
        "rerun_repair_fallback_rows": rerun_repair_fallback,
        "proposal_changed_rows": proposal_changed,
        "effect_vector_changed_rows": effect_changed,
        "verdict_changed_rows": verdict_changed,
        "original_overall_strict_rate": original_overall_strict,
        "sensitivity_overall_strict_rate": sensitivity_overall_strict,
        "overall_strict_delta_pp": _rate_delta_pp(sensitivity_overall_strict, original_overall_strict),
        "original_qwen_strict_rate": original_qwen_strict,
        "sensitivity_qwen_strict_rate": sensitivity_qwen_strict,
        "qwen_strict_delta_pp": _rate_delta_pp(sensitivity_qwen_strict, original_qwen_strict),
        "rerun_parse_status_counts": rerun_traces["model_proposal_parse_status"].value_counts().sort_index().to_dict(),
        "merged_out": str(merged_dir),
        "same_prompt_note": (
            "Rerun used the existing run_online action-proposal prompt path with model_controls_policy, "
            "model_proposal_mode=actions, temperature=0, and the same logical rows/split trace IDs."
        ),
    }

    table_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([payload]).to_csv(table_out, index=False)

    lines = [
        "# Qwen Repair Sensitivity",
        "",
        f"affected_rows: {payload['affected_rows']}",
        f"rerun_rows: {payload['rerun_rows']}",
        f"original_repair_fallback_rows: {payload['original_repair_fallback_rows']}",
        f"rerun_repair_fallback_rows: {payload['rerun_repair_fallback_rows']}",
        f"proposal_changed_rows: {payload['proposal_changed_rows']}",
        f"effect_vector_changed_rows: {payload['effect_vector_changed_rows']}",
        f"verdict_changed_rows: {payload['verdict_changed_rows']}",
        f"overall_strict_delta_pp: {payload['overall_strict_delta_pp']:.6f}",
        f"qwen_strict_delta_pp: {payload['qwen_strict_delta_pp']:.6f}",
        "",
        payload["same_prompt_note"],
        "",
        "## Rerun Parse Status Counts",
        "",
        pd.Series(payload["rerun_parse_status_counts"], name="count").to_frame().to_markdown(),
        "",
        "## Outputs",
        "",
        f"- merged split: `{merged_dir}`",
        f"- table: `{table_out}`",
    ]
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--original-traces", default=f"effectbench_omega/outputs/{ORIGINAL_SPLIT}/traces.parquet")
    prep.add_argument("--source-manifest", default="effectbench_omega/manifests/tasks_local_open.csv")
    prep.add_argument("--manifest-out", default="effectbench_omega/manifests/qwen_repair_rows.csv")
    prep.add_argument("--summary-out", default="effectbench_omega/reports/qwen_repair_manifest_summary.json")
    prep.set_defaults(func=prepare)

    rep = sub.add_parser("report")
    rep.add_argument("--original-dir", default=f"effectbench_omega/outputs/{ORIGINAL_SPLIT}")
    rep.add_argument("--rerun-dir", default="effectbench_omega/outputs/qwen_repair_sensitivity_rerun")
    rep.add_argument("--merged-out", default="effectbench_omega/outputs/qwen_repair_sensitivity_merged")
    rep.add_argument("--table-out", default="effectbench_omega/tables/qwen_repair_sensitivity.csv")
    rep.add_argument("--report-out", default="effectbench_omega/reports/qwen_repair_sensitivity.md")
    rep.set_defaults(func=report)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
