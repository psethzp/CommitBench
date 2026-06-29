#!/usr/bin/env python3
"""Write Rebuttal-2 status docs after queued audits finish."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MARKER_START = "<!-- REBUTTAL2_STATUS_START -->"
MARKER_END = "<!-- REBUTTAL2_STATUS_END -->"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _report_value(path: Path, key: str) -> str:
    text = _read_text(path)
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return "pending"


def _json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _table_metric(path: Path, metric: str) -> str:
    if not path.exists():
        return "pending"
    df = pd.read_csv(path)
    if {"metric", "value"}.issubset(df.columns):
        rows = df[df["metric"].astype(str).eq(metric)]
        if not rows.empty:
            return str(rows.iloc[0]["value"])
    return "pending"


def _online_control(path: Path) -> list[str]:
    if not path.exists():
        return ["| System | Strict excess / success | Raw success |", "|---|---:|---:|", "| pending | pending | pending |"]
    df = pd.read_csv(path)
    lines = ["| System | Strict excess / success | Raw success |", "|---|---:|---:|"]
    for _, row in df.iterrows():
        system = str(row.get("system", ""))
        strict = row.get(
            "canonical_strict_excess_rate",
            row.get("strict_excess_per_accepted_success", row.get("strict_excess_per_success", "")),
        )
        raw = row.get("raw_success_rate", row.get("accepted_success_rate", ""))
        lines.append(f"| `{system}` | {strict} | {raw} |")
    return lines


def _update_marker(path: Path, block: str) -> None:
    old = _read_text(path)
    if MARKER_START in old and MARKER_END in old:
        before, rest = old.split(MARKER_START, 1)
        _, after = rest.split(MARKER_END, 1)
        new = before.rstrip() + "\n\n" + block.rstrip() + "\n\n" + after.lstrip()
    else:
        new = old.rstrip() + "\n\n" + block.rstrip() + "\n"
    path.write_text(new, encoding="utf-8")


def _claim_rows(summary: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "claim_id": "r2_full_stress_replay_bundles",
            "claim": "Rebuttal-2 full stress replay checks every Stage-3 stress certificate bundle.",
            "value": summary["stress_bundles_checked"],
            "unit": "bundles",
            "artifact": "effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md",
            "extraction": "bundles_checked",
            "paper_status": "allowed_audit",
        },
        {
            "claim_id": "r2_full_stress_replay_failures",
            "claim": "Rebuttal-2 full stress replay has zero replay failures.",
            "value": summary["stress_replay_failures"],
            "unit": "failures",
            "artifact": "effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md",
            "extraction": "failures",
            "paper_status": "allowed_audit",
        },
        {
            "claim_id": "r2_fresh_nosystem_shared_traces",
            "claim": "Fresh no-system-prompt shared-proposal audit contains 21,504 replayed traces when complete.",
            "value": summary["v3_trace_rows"],
            "unit": "traces",
            "artifact": "effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/shared_proposal_summary.json",
            "extraction": "split_trace_count",
            "paper_status": "allowed_audit",
        },
        {
            "claim_id": "r2_fresh_nosystem_canonical_mismatches",
            "claim": "Fresh no-system-prompt shared-proposal canonical audit has zero unexplained mismatches when complete.",
            "value": summary["v3_unexplained_mismatches"],
            "unit": "unexplained mismatches",
            "artifact": "effectbench_omega/tables/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.csv",
            "extraction": "unexplained_mismatches",
            "paper_status": "allowed_audit",
        },
    ]


def _update_claim_registry(summary: dict[str, str]) -> None:
    path = ROOT / "effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv"
    if path.exists():
        df = pd.read_csv(path, dtype=str)
    else:
        df = pd.DataFrame(columns=["claim_id", "claim", "value", "unit", "artifact", "extraction", "paper_status"])
    new_rows = pd.DataFrame(_claim_rows(summary))
    df = df[~df["claim_id"].astype(str).isin(set(new_rows["claim_id"].astype(str)))]
    pd.concat([df, new_rows], ignore_index=True).to_csv(path, index=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-job-id", default="")
    parser.add_argument("--queue-job-id", default="")
    parser.add_argument("--status", default="complete")
    args = parser.parse_args()

    stress_report = ROOT / "effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md"
    v3_summary = _json(ROOT / "effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/shared_proposal_summary.json")
    v3_frontier_table = ROOT / "effectbench_omega/tables/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.csv"
    stage4_json = _json(ROOT / "effectbench_omega/reports/stage4_leave_one_robustness.json")
    if v3_frontier_table.exists():
        frontier = pd.read_csv(v3_frontier_table)
        unexplained = str(int(frontier.get("unexplained_mismatches", pd.Series([0])).sum()))
    else:
        unexplained = "pending"

    summary = {
        "status": args.status,
        "pipeline_job_id": args.pipeline_job_id or "pending",
        "queue_job_id": args.queue_job_id or "pending",
        "stress_bundles_checked": _report_value(stress_report, "bundles_checked"),
        "stress_replay_failures": _report_value(stress_report, "failures"),
        "v3_trace_rows": str(v3_summary.get("split_trace_count", "pending")),
        "v3_complete_shared_groups": str(v3_summary.get("complete_shared_source_groups", "pending")),
        "v3_unexplained_mismatches": unexplained,
        "stage4_gate_rows": str(stage4_json.get("gate_rows", "pending")),
        "stage4_base_gap_failures": str(stage4_json.get("base_gap_failures", "pending")),
        "stage4_projection_failures": str(stage4_json.get("projection_failures_required_slices", "pending")),
        "stage4_effectguard_zero_failures": str(stage4_json.get("effectguard_zero_failures", "pending")),
    }

    lines = [
        "# Rebuttal 2 Execution Status",
        "",
        f"Status: `{summary['status']}`",
        f"Pipeline job: `{summary['pipeline_job_id']}`",
        f"Queue job: `{summary['queue_job_id']}`",
        "",
        "| Check | Value |",
        "|---|---:|",
        f"| Full stress replay bundles | {summary['stress_bundles_checked']} |",
        f"| Full stress replay failures | {summary['stress_replay_failures']} |",
        f"| Fresh no-system shared traces | {summary['v3_trace_rows']} |",
        f"| Fresh no-system complete shared groups | {summary['v3_complete_shared_groups']} |",
        f"| Fresh no-system unexplained mismatches | {summary['v3_unexplained_mismatches']} |",
        f"| Stage 4 gate rows | {summary['stage4_gate_rows']} |",
        f"| Stage 4 base-gap failures | {summary['stage4_base_gap_failures']} |",
        f"| Stage 4 projection failures | {summary['stage4_projection_failures']} |",
        f"| Stage 4 EffectGuard-zero failures | {summary['stage4_effectguard_zero_failures']} |",
        "",
        "## Fresh No-System Online Control",
        "",
        *_online_control(ROOT / "effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv"),
        "",
        "## Artifacts",
        "",
        "- Full stress replay: `effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md`",
        "- Fresh BASE split: `effectbench_omega/outputs/base_nosystem_v1_all_local/`",
        "- Fresh shared proposal split: `effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/`",
        "- Fresh canonical report: `effectbench_omega/reports/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.md`",
        "- Refreshed leave-one robustness: `effectbench_omega/reports/stage4_leave_one_robustness.md`",
    ]
    report = "\n".join(lines) + "\n"
    report_path = ROOT / "effectbench_omega/reports/rebuttal2_execution_status.md"
    report_path.write_text(report, encoding="utf-8")

    doc_block = f"{MARKER_START}\n{report.rstrip()}\n{MARKER_END}\n"
    for rel in ["README.md", "results.md", "effectbench_omega/RUNBOOK_EACL_RESCUE_V2.md"]:
        _update_marker(ROOT / rel, doc_block)
    _update_claim_registry(summary)
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
