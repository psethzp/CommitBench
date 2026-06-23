#!/usr/bin/env python3
"""Bootstrap placeholder with deterministic local smoke intervals."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--group-by", nargs="*")
    parser.add_argument("--methods", nargs="*")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    certs = pd.read_parquet(args.certificates)
    strict = float((certs["verdict"] == "strict_excess").mean()) if len(certs) else 0.0
    rows = [
        {
            "comparison": "BASE_raw_vs_kernel_local_smoke",
            "method": method,
            "estimate": strict,
            "ci_low": max(0.0, strict - 0.05),
            "ci_high": min(1.0, strict + 0.05),
        }
        for method in (args.methods or ["paired_bootstrap"])
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

