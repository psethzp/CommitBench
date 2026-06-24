#!/usr/bin/env python3
"""Cost audit for API logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_jsonl(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    rows = []
    with p.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", nargs="+", required=True)
    parser.add_argument("--project-full", action="store_true")
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    rows = [row for path in args.logs for row in _read_jsonl(path)]
    df = pd.DataFrame(rows)
    total = float(df["cost_usd"].sum()) if len(df) and "cost_usd" in df else 0.0
    unpriced_bedrock = 0
    if len(df) and "provider" in df:
        cost_series = df["cost_usd"] if "cost_usd" in df else 0
        unpriced_bedrock = int(((df["provider"] == "bedrock") & (cost_series == 0)).sum())
    summary = {
        "request_count": int(len(df)),
        "total_cost_usd": total,
        "projected_full_cost_usd": total if not args.project_full else total * 20,
        "unpriced_bedrock_request_count": unpriced_bedrock,
        "pricing_note": "Bedrock rows need configured rate cards or AWS billing export for exact dollar accounting."
        if unpriced_bedrock
        else "",
        "status": "ok",
    }
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
