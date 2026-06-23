#!/usr/bin/env python3
"""Check that a claim registry exists and is nonempty."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper")
    parser.add_argument("--registry", required=True)
    args = parser.parse_args()

    path = Path(args.registry)
    if not path.exists():
        raise SystemExit(f"missing claim registry: {path}")
    df = pd.read_csv(path)
    if len(df) == 0:
        raise SystemExit("empty claim registry")
    print(f"claim registry rows: {len(df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

