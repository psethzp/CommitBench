#!/usr/bin/env python3
"""Audit runtime logs for forbidden oracle fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-logs")
    parser.add_argument("--traces")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = args.runtime_logs or args.traces
    df = pd.read_parquet(source)
    failures = 0
    if "forbidden_oracle_fields_seen" in df:
        failures = int(df["forbidden_oracle_fields_seen"].astype(str).ne("[]").sum())
    summary = {
        "rows_checked": int(len(df)),
        "oracle_failures": failures,
        "no_oracle_sentinel_pass_rate": 1.0 if failures == 0 else 0.0,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix == ".csv":
        pd.DataFrame([summary]).to_csv(out, index=False)
    else:
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

