#!/usr/bin/env python3
"""Aggregate certificates into paper-facing tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


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

    claims = [
        {
            "claim_id": "local_smoke_trace_count",
            "value": int(len(certs)),
            "source": str(args.main_certificates),
            "status": "computed",
        },
        {
            "claim_id": "local_smoke_strict_excess_count",
            "value": int(certs["strict_excess"].sum()),
            "source": str(args.main_certificates),
            "status": "computed",
        },
    ]
    claim_path = Path(args.claim_registry)
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(claims).to_csv(claim_path, index=False)
    print(f"wrote tables to {out_tables}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

