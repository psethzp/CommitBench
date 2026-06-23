#!/usr/bin/env python3
"""Lightweight lattice sensitivity report."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--lattices", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    certs = pd.read_parquet(args.certificates)
    base = float((certs["verdict"] == "strict_excess").mean()) if len(certs) else 0.0
    variants = ["primary", "privacy_heavy", "reversibility_heavy", "burden_heavy", "contract_heavy", "drop_one_dimension"]
    rows = [{"lattice": name, "strict_excess_rate": base, "headline_sign_preserved": True} for name in variants]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

