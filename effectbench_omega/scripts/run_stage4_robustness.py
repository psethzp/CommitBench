#!/usr/bin/env python3
"""Run offline leave-one robustness audits for rebuttal Stage 4."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class SplitSpec:
    name: str
    role: str
    traces: str
    certificates: str
    base_system: str = "BASE"
    proj_system: str = "PROJ_GUARD_V2"
    effect_system: str = "EFFECTGUARD_V2"
    projection_required: bool = True
    optional: bool = False


SPLITS = [
    SplitSpec(
        name="main_controlled_legacy_guards",
        role="main_gap_reference",
        traces="effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet",
        certificates="effectbench_omega/outputs/main_mc_postfix_all_local/kernel_canonical/certificates_enumerated.parquet",
        proj_system="PROJ_GUARD",
        effect_system="EFFECTGUARD",
        projection_required=False,
    ),
    SplitSpec(
        name="corrected_guard_v2",
        role="corrected_online_guard",
        traces="effectbench_omega/outputs/guard_v2_main_with_base_all_local/traces.parquet",
        certificates="effectbench_omega/outputs/guard_v2_main_with_base_all_local/kernel_canonical/certificates_enumerated.parquet",
    ),
    SplitSpec(
        name="shared_proposal_v2",
        role="paired_proposal_control",
        traces="effectbench_omega/outputs/shared_proposal_v2_audit_all_local/traces.parquet",
        certificates="effectbench_omega/outputs/shared_proposal_v2_audit_all_local/kernel_canonical/certificates_enumerated.parquet",
    ),
    SplitSpec(
        name="shared_proposal_v3_nosystem",
        role="paired_proposal_control_fresh_no_system_prompt",
        traces="effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/traces.parquet",
        certificates="effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/kernel_canonical/certificates_enumerated.parquet",
        optional=True,
    ),
    SplitSpec(
        name="native_validation",
        role="native_validation",
        traces="effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet",
        certificates="effectbench_omega/outputs/native_subset_v1_all_local/kernel_canonical/certificates_enumerated.parquet",
        projection_required=False,
    ),
]


def _read_split(spec: SplitSpec) -> tuple[pd.DataFrame, pd.DataFrame]:
    traces_path = ROOT / spec.traces
    certs_path = ROOT / spec.certificates
    if not traces_path.exists() or not certs_path.exists():
        if spec.optional:
            return pd.DataFrame(), pd.DataFrame()
        missing = [str(path) for path in [traces_path, certs_path] if not path.exists()]
        raise FileNotFoundError(f"missing required split files for {spec.name}: {missing}")
    traces = pd.read_parquet(traces_path)
    certs = pd.read_parquet(certs_path)
    return traces, certs


def _families(traces: pd.DataFrame) -> list[str]:
    return sorted(str(value) for value in traces["family"].dropna().astype(str).unique())


def _models(traces: pd.DataFrame) -> list[str]:
    return sorted(str(value) for value in traces["model"].dropna().astype(str).unique())


def _subsets(traces: pd.DataFrame) -> Iterable[tuple[str, str, pd.Series]]:
    yield "none", "all", pd.Series([True] * len(traces), index=traces.index)
    for model in _models(traces):
        yield "drop_model", model, traces["model"].astype(str).ne(model)
    for family in _families(traces):
        yield "drop_family", family, traces["family"].astype(str).ne(family)


def _metrics_for_system(traces: pd.DataFrame, certs: pd.DataFrame, system: str) -> dict[str, object]:
    st = traces[traces["system"].astype(str).eq(system)]
    sc = certs[certs["system"].astype(str).eq(system)]
    trajectories = int(len(st))
    successes = int(st["terminal_success"].sum()) if trajectories else 0
    strict = int(sc["verdict"].astype(str).eq("strict_excess").sum())
    minimal = int(sc["verdict"].astype(str).eq("minimal").sum())
    incomparable = int(sc["verdict"].astype(str).eq("minimal_with_incomparables").sum())
    kernel_successes = successes - strict
    return {
        "system": system,
        "trajectories": trajectories,
        "terminal_successes": successes,
        "raw_success_rate": successes / trajectories if trajectories else 0.0,
        "strict_excess": strict,
        "strict_excess_per_success": strict / successes if successes else 0.0,
        "minimal": minimal,
        "minimal_with_incomparables": incomparable,
        "kernel_successes": kernel_successes,
        "kernel_success_per_success": kernel_successes / successes if successes else 0.0,
        "kernel_success_rate_all_trajectories": kernel_successes / trajectories if trajectories else 0.0,
    }


def _gate_row(spec: SplitSpec, metric_rows: list[dict[str, object]], exclusion_type: str, dropped_value: str) -> dict[str, object]:
    by_system = {str(row["system"]): row for row in metric_rows}
    base = by_system.get(spec.base_system, {})
    proj = by_system.get(spec.proj_system, {})
    effect = by_system.get(spec.effect_system, {})
    base_gap_pp = 100.0 * float(base.get("strict_excess_per_success", 0.0))
    proj_strict = float(proj.get("strict_excess_per_success", 0.0))
    effect_strict = float(effect.get("strict_excess_per_success", 0.0))
    base_raw = float(base.get("raw_success_rate", 0.0))
    effect_raw = float(effect.get("raw_success_rate", 0.0))
    raw_retention = effect_raw / base_raw if base_raw else 0.0
    return {
        "split": spec.name,
        "role": spec.role,
        "exclusion_type": exclusion_type,
        "dropped_value": dropped_value,
        "base_gap_pp": base_gap_pp,
        "base_gap_ge_10pp": base_gap_pp >= 10.0,
        "projection_residual_strict_rate": proj_strict,
        "projection_residual_nonzero": proj_strict > 0.0 if spec.projection_required else "not_required",
        "effectguard_strict_rate": effect_strict,
        "effectguard_zero_strict": effect_strict == 0.0,
        "effectguard_raw_retention_vs_base": raw_retention,
        "effectguard_retains_ge_90pct_base_raw": raw_retention >= 0.9,
        "projection_required": spec.projection_required,
    }


def _write_report(path: Path, gate: pd.DataFrame, metrics: pd.DataFrame, stress_summary: dict[str, object]) -> None:
    lines = [
        "# Stage 4 Leave-One Robustness",
        "",
        "This audit is fully offline. It uses saved traces and canonical enumerated-frontier certificates only.",
        "",
        "## Gate Summary",
        "",
        "| Split | Drop type | Failing base-gap slices | Failing projection slices | Failing EffectGuard-zero slices |",
        "|---|---|---:|---:|---:|",
    ]
    for (split, exclusion_type), group in gate.groupby(["split", "exclusion_type"], dropna=False):
        fail_base = int((group["base_gap_ge_10pp"] == False).sum())  # noqa: E712
        proj_values = group["projection_residual_nonzero"]
        fail_proj = int((proj_values == False).sum())  # noqa: E712
        fail_effect = int((group["effectguard_zero_strict"] == False).sum())  # noqa: E712
        lines.append(f"| `{split}` | `{exclusion_type}` | {fail_base} | {fail_proj} | {fail_effect} |")

    lines.extend(
        [
            "",
            "## Stress Summary",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]
    )
    for key, value in stress_summary.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "Detailed per-system metrics are in `effectbench_omega/tables/stage4_leave_one_metrics.csv`.",
            "Detailed gate rows are in `effectbench_omega/tables/stage4_leave_one_gates.csv`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stress_summary() -> dict[str, object]:
    traces_path = ROOT / "effectbench_omega/outputs/stage3_stress_all_local/traces.parquet"
    certs_path = ROOT / "effectbench_omega/outputs/stage3_stress_all_local/kernel_canonical/certificates_enumerated.parquet"
    if not traces_path.exists() or not certs_path.exists():
        return {"available": False}
    traces = pd.read_parquet(traces_path)
    certs = pd.read_parquet(certs_path)
    effect = traces[traces["system"].astype(str).eq("EFFECTGUARD_V2")]
    return {
        "available": True,
        "trace_count": int(len(traces)),
        "canonical_strict_excess": int(certs["verdict"].astype(str).eq("strict_excess").sum()),
        "necessary_high_effectguard_decisions": int(effect["guard_decisions"].str.contains("necessary_high").sum()),
        "incomparable_effectguard_decisions": int(effect["guard_decisions"].str.contains("incomparable").sum()),
        "minimal_with_incomparables": int(certs["verdict"].astype(str).eq("minimal_with_incomparables").sum()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-out", default="effectbench_omega/tables/stage4_leave_one_metrics.csv")
    parser.add_argument("--gates-out", default="effectbench_omega/tables/stage4_leave_one_gates.csv")
    parser.add_argument("--summary-out", default="effectbench_omega/reports/stage4_leave_one_robustness.md")
    args = parser.parse_args()

    metric_rows: list[dict[str, object]] = []
    gate_rows: list[dict[str, object]] = []
    for spec in SPLITS:
        traces, certs = _read_split(spec)
        if traces.empty and certs.empty and spec.optional:
            continue
        for exclusion_type, dropped_value, mask in _subsets(traces):
            subset_traces = traces[mask].copy()
            trace_ids = set(subset_traces["trace_id"].astype(str))
            subset_certs = certs[certs["trace_id"].astype(str).isin(trace_ids)].copy()
            systems = sorted(str(value) for value in subset_traces["system"].dropna().astype(str).unique())
            rows = []
            for system in systems:
                row = {
                    "split": spec.name,
                    "role": spec.role,
                    "exclusion_type": exclusion_type,
                    "dropped_value": dropped_value,
                    **_metrics_for_system(subset_traces, subset_certs, system),
                }
                rows.append(row)
                metric_rows.append(row)
            gate_rows.append(_gate_row(spec, rows, exclusion_type, dropped_value))

    metrics = pd.DataFrame(metric_rows)
    gates = pd.DataFrame(gate_rows)
    stress_summary = _stress_summary()

    metrics_out = ROOT / args.metrics_out
    gates_out = ROOT / args.gates_out
    summary_out = ROOT / args.summary_out
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    gates_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(metrics_out, index=False)
    gates.to_csv(gates_out, index=False)
    (summary_out.with_suffix(".json")).write_text(
        json.dumps(
            {
                "metric_rows": int(len(metrics)),
                "gate_rows": int(len(gates)),
                "splits": sorted(metrics["split"].unique().tolist()),
                "stress_summary": stress_summary,
                "base_gap_failures": int((gates["base_gap_ge_10pp"] == False).sum()),  # noqa: E712
                "projection_failures_required_slices": int(
                    ((gates["projection_required"] == True) & (gates["projection_residual_nonzero"] == False)).sum()  # noqa: E712
                ),
                "effectguard_zero_failures": int((gates["effectguard_zero_strict"] == False).sum()),  # noqa: E712
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_report(summary_out, gates, metrics, stress_summary)
    print(json.dumps(json.loads(summary_out.with_suffix(".json").read_text()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
