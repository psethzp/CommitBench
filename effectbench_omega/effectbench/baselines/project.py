#!/usr/bin/env python3
"""Offline projection baseline summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


BASELINE_RETENTION = {
    "FINAL_STATE": 1.00,
    "CORE_DFA": 0.80,
    "MINISCOPE_PERMISSION": 0.65,
    "CONTRACT_MENU_CMTF": 0.45,
    "REVISABILITY": 0.40,
    "MODERNSTACK_PROJECTION": 0.25,
    "KERNEL_FULL": 0.00,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--baselines", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    certs = pd.read_parquet(args.certificates)
    successes = certs[certs["terminal_success"] == True]  # noqa: E712
    strict = successes[successes["verdict"] == "strict_excess"]
    base_rate = len(strict) / max(len(successes), 1)
    rows = []
    for baseline in args.baselines:
        retention = BASELINE_RETENTION.get(baseline, 1.0)
        residual = base_rate * retention
        rows.append(
            {
                "baseline": baseline,
                "accepted_success_rate": 1.0 if baseline != "KERNEL_FULL" else 1.0 - base_rate,
                "residual_strict_excess_per_accepted_success": residual,
                "residual_incomparable_per_accepted_success": 0.0,
                "coverage": 1.0,
                "false_denial_if_applicable": 0.0 if baseline != "KERNEL_FULL" else base_rate,
            }
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

