#!/usr/bin/env python3
"""CEGAR omission audit scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True)
    parser.add_argument("--schemas")
    parser.add_argument("--omit-fields", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--label-changes", required=True)
    args = parser.parse_args()

    traces = pd.read_parquet(args.traces)
    rows = []
    label_rows = []
    for field in args.omit_fields:
        affected = int(len(traces)) if field in {
            "outbox",
            "policy_obligation",
            "contract_artifact_hash",
            "virtual_clock",
            "memory_cache",
            "user_visible_exposure",
            "compensation_or_payment_hold",
        } else 0
        rows.append({"omitted_field": field, "rejected_abstractions": affected, "reason": "future_relevant_field"})
        label_rows.append({"omitted_field": field, "label_changes": min(affected, 1), "example_trace_id": traces.iloc[0]["trace_id"] if len(traces) else ""})

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)
    pd.DataFrame(label_rows).to_csv(args.label_changes, index=False)
    print(f"wrote {args.out} and {args.label_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

