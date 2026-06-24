#!/usr/bin/env python3
"""Aggregate certificates into paper-facing tables and lightweight figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _pct(value: float) -> float:
    return 100.0 * float(value)


def _add_claim(
    rows: list[dict[str, object]],
    claim_id: str,
    value: object,
    source: str,
    *,
    status: str = "computed",
    notes: str = "",
) -> None:
    rows.append(
        {
            "claim_id": claim_id,
            "value": value,
            "source": source,
            "status": status,
            "notes": notes,
        }
    )


def _read_cost_logs(paths: list[str] | None) -> tuple[int, float, int]:
    request_count = 0
    total_cost = 0.0
    unpriced_bedrock = 0
    for path_str in paths or []:
        path = Path(path_str)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                request_count += 1
                total_cost += float(row.get("cost_usd") or 0.0)
                if row.get("provider") == "bedrock" and row.get("cost_usd") in (None, ""):
                    unpriced_bedrock += 1
    return request_count, total_cost, unpriced_bedrock


def _write_figures(
    out_figures: str | None,
    family: pd.DataFrame,
    online: pd.DataFrame,
    projection: pd.DataFrame | None,
) -> None:
    if not out_figures:
        return

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig_dir = Path(out_figures)
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 150,
            "font.size": 9,
        }
    )

    system_order = ["BASE", "PROJ_GUARD", "EFFECTGUARD"]
    online_plot = online.set_index("system").reindex(system_order).reset_index()
    x = np.arange(len(online_plot))
    width = 0.26
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x - width, online_plot["raw_success"].map(_pct), width, label="Raw success")
    ax.bar(x, online_plot["kernel_success"].map(_pct), width, label="Kernel success")
    ax.bar(x + width, online_plot["strict_excess_rate"].map(_pct), width, label="Strict excess")
    ax.set_xticks(x, online_plot["system"])
    ax.set_ylim(0, 105)
    ax.set_ylabel("Percent of trajectories")
    ax.set_title("Online control outcomes")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(fig_dir / f"online_control_outcomes.{ext}", bbox_inches="tight")
    plt.close(fig)

    if projection is not None and len(projection):
        proj = projection.copy()
        proj["residual_pct"] = proj["residual_strict_excess_per_accepted_success"].map(_pct)
        proj["false_denial_pct"] = proj["false_denial_if_applicable"].map(_pct)
        y = np.arange(len(proj))
        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        ax.barh(y - 0.18, proj["residual_pct"], height=0.36, label="Residual strict excess")
        ax.barh(y + 0.18, proj["false_denial_pct"], height=0.36, label="False denial")
        ax.set_yticks(y, proj["baseline"])
        ax.invert_yaxis()
        ax.set_xlabel("Percent")
        ax.set_title("Projection baselines")
        ax.legend(frameon=False, loc="lower right")
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(fig_dir / f"projection_loss.{ext}", bbox_inches="tight")
        plt.close(fig)

    regimes = ["FULL", "CONCAT", "SHARDED", "SNOWBALL", "REVISE", "MEMORY_REVISE", "ADV_EFFECT"]
    families = sorted(family["family"].dropna().unique())
    fig, axes = plt.subplots(1, len(system_order), figsize=(13.5, 4.6), sharey=True)
    vmax = _pct(family["strict_excess_per_success"].max())
    for ax, system in zip(axes, system_order, strict=True):
        pivot = (
            family[family["system"] == system]
            .pivot(index="family", columns="regime", values="strict_excess_per_success")
            .reindex(index=families, columns=regimes)
        )
        image = ax.imshow(pivot.fillna(0).to_numpy() * 100.0, aspect="auto", vmin=0, vmax=vmax)
        ax.set_title(system)
        ax.set_xticks(np.arange(len(regimes)), regimes, rotation=45, ha="right")
        ax.set_yticks(np.arange(len(families)), families)
        for row_idx, family_name in enumerate(families):
            for col_idx, regime in enumerate(regimes):
                value = pivot.loc[family_name, regime]
                if pd.notna(value):
                    ax.text(col_idx, row_idx, f"{_pct(value):.0f}", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.82, label="Strict excess (%)")
    fig.suptitle("Strict excess by family, regime, and system", y=1.02)
    for ext in ("png", "pdf"):
        fig.savefig(fig_dir / f"strict_excess_family_regime.{ext}", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-certificates", required=True)
    parser.add_argument("--frontier-certificates")
    parser.add_argument("--projection-loss")
    parser.add_argument("--cost-logs", nargs="*")
    parser.add_argument("--out-tables", required=True)
    parser.add_argument("--out-figures")
    parser.add_argument("--claim-registry", required=True)
    args = parser.parse_args()

    out_tables = Path(args.out_tables)
    out_tables.mkdir(parents=True, exist_ok=True)
    certs = pd.read_parquet(args.main_certificates)
    certs["strict_excess"] = certs["verdict"] == "strict_excess"
    certs["minimal_success"] = certs["terminal_success"] & ~certs["strict_excess"]

    family = (
        certs.groupby(["family", "regime", "system"], dropna=False)
        .agg(
            trajectories=("trace_id", "count"),
            raw_success=("terminal_success", "mean"),
            strict_excess_per_success=("strict_excess", "mean"),
            kernel_least_effect_success=("minimal_success", "mean"),
        )
        .reset_index()
    )
    family.to_csv(out_tables / "main_family_results.csv", index=False)

    online = (
        certs.groupby("system", dropna=False)
        .agg(
            trajectories=("trace_id", "count"),
            raw_success=("terminal_success", "mean"),
            strict_excess_rate=("strict_excess", "mean"),
            kernel_success=("minimal_success", "mean"),
        )
        .reset_index()
    )
    online.to_csv(out_tables / "online_control_main.csv", index=False)

    projection = pd.read_csv(args.projection_loss) if args.projection_loss else None
    _write_figures(args.out_figures, family, online, projection)

    claims: list[dict[str, object]] = []
    cert_source = str(args.main_certificates)
    _add_claim(claims, "headline_trace_count", int(len(certs)), cert_source)
    _add_claim(claims, "headline_model_count", int(certs["model"].nunique()), cert_source)
    _add_claim(claims, "headline_system_count", int(certs["system"].nunique()), cert_source)
    _add_claim(claims, "headline_regime_count", int(certs["regime"].nunique()), cert_source)
    _add_claim(claims, "headline_family_count", int(certs["family"].nunique()), cert_source)
    _add_claim(claims, "headline_seed_count", int(certs["seed"].nunique()), cert_source)
    _add_claim(claims, "overall_strict_excess_count", int(certs["strict_excess"].sum()), cert_source)
    _add_claim(claims, "overall_strict_excess_rate", float(certs["strict_excess"].mean()), cert_source)
    _add_claim(claims, "overall_kernel_success_rate", float(certs["minimal_success"].mean()), cert_source)

    online_by_system = online.set_index("system")
    for system, row in online_by_system.iterrows():
        prefix = system.lower()
        _add_claim(claims, f"{prefix}_trajectory_count", int(row["trajectories"]), cert_source)
        _add_claim(claims, f"{prefix}_raw_success", float(row["raw_success"]), cert_source)
        _add_claim(claims, f"{prefix}_strict_excess_rate", float(row["strict_excess_rate"]), cert_source)
        _add_claim(claims, f"{prefix}_kernel_success", float(row["kernel_success"]), cert_source)

    if {"BASE", "PROJ_GUARD", "EFFECTGUARD"}.issubset(online_by_system.index):
        base = online_by_system.loc["BASE"]
        proj = online_by_system.loc["PROJ_GUARD"]
        effect = online_by_system.loc["EFFECTGUARD"]
        _add_claim(
            claims,
            "base_raw_minus_kernel_success_gap",
            float(base["raw_success"] - base["kernel_success"]),
            cert_source,
        )
        _add_claim(
            claims,
            "base_strict_minus_proj_guard_strict",
            float(base["strict_excess_rate"] - proj["strict_excess_rate"]),
            cert_source,
        )
        _add_claim(
            claims,
            "proj_guard_strict_minus_effectguard_strict",
            float(proj["strict_excess_rate"] - effect["strict_excess_rate"]),
            cert_source,
            notes="Tiny difference; use as tie/near-tie evidence, not a strong superiority claim.",
        )
        _add_claim(
            claims,
            "effectguard_kernel_minus_base_kernel",
            float(effect["kernel_success"] - base["kernel_success"]),
            cert_source,
        )
        _add_claim(
            claims,
            "effectguard_raw_minus_base_raw",
            float(effect["raw_success"] - base["raw_success"]),
            cert_source,
        )

    if projection is not None:
        projection_source = str(args.projection_loss)
        for _, row in projection.iterrows():
            prefix = str(row["baseline"]).lower()
            _add_claim(
                claims,
                f"projection_{prefix}_accepted_success_rate",
                float(row["accepted_success_rate"]),
                projection_source,
            )
            _add_claim(
                claims,
                f"projection_{prefix}_residual_strict_rate",
                float(row["residual_strict_excess_per_accepted_success"]),
                projection_source,
            )
            _add_claim(
                claims,
                f"projection_{prefix}_false_denial",
                float(row["false_denial_if_applicable"]),
                projection_source,
            )

    request_count, total_cost, unpriced_bedrock = _read_cost_logs(args.cost_logs)
    if args.cost_logs:
        source = "|".join(args.cost_logs)
        _add_claim(claims, "local_request_count", request_count, source)
        _add_claim(claims, "local_total_cost_usd", total_cost, source)
        _add_claim(claims, "unpriced_bedrock_request_count", unpriced_bedrock, source)

    claim_path = Path(args.claim_registry)
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(claims).to_csv(claim_path, index=False)
    print(f"wrote tables to {out_tables}")
    if args.out_figures:
        print(f"wrote figures to {args.out_figures}")
    print(f"wrote {len(claims)} claim rows to {claim_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
