#!/usr/bin/env python3
"""Build a Stage 4 scoring split from frozen BASE plus V2 guard rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


PARQUET_FILES = ["traces.parquet", "runtime_logs.parquet", "tool_ledgers.parquet"]
JSONL_FILES = ["api_logs.jsonl", "failures.jsonl"]
BASE_SYSTEM = "BASE"
V2_SYSTEMS = {"PROJ_GUARD_V2", "EFFECTGUARD_V2"}


def _filter_parquet(path: Path, systems: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if "system" not in df.columns:
        raise ValueError(f"{path} has no system column")
    return df[df["system"].astype(str).isin(systems)].copy()


def _iter_filtered_jsonl(path: Path, systems: set[str]) -> tuple[list[str], int]:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    lines: list[str] = []
    seen = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row: dict[str, Any] = json.loads(line)
            if str(row.get("system", "")) in systems:
                lines.append(json.dumps(row, sort_keys=True))
                seen += 1
    return lines, seen


def _check_count(name: str, observed: int, expected: int | None, allow_partial: bool) -> None:
    if expected is None or allow_partial:
        return
    if observed != expected:
        raise ValueError(f"{name} has {observed} rows, expected {expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-split", default="effectbench_omega/outputs/main_mc_postfix_all_local")
    parser.add_argument("--v2-split", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--expected-base-traces", type=int, default=7168)
    parser.add_argument("--expected-v2-traces", type=int, default=14336)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    base_dir = Path(args.base_split)
    v2_dir = Path(args.v2_split)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "base_split": str(base_dir),
        "v2_split": str(v2_dir),
        "out": str(out),
        "base_system": BASE_SYSTEM,
        "v2_systems": sorted(V2_SYSTEMS),
        "allow_partial": bool(args.allow_partial),
        "files": {},
    }

    for filename in PARQUET_FILES:
        base = _filter_parquet(base_dir / filename, {BASE_SYSTEM})
        v2 = _filter_parquet(v2_dir / filename, V2_SYSTEMS)
        if filename == "traces.parquet":
            _check_count("base traces", len(base), args.expected_base_traces, args.allow_partial)
            _check_count("v2 traces", len(v2), args.expected_v2_traces, args.allow_partial)
            duplicate_ids = int(pd.concat([base["trace_id"], v2["trace_id"]]).duplicated().sum())
            if duplicate_ids:
                raise ValueError(f"combined traces contain {duplicate_ids} duplicate trace_ids")
        combined = pd.concat([base, v2], ignore_index=True)
        combined.to_parquet(out / filename, index=False)
        summary["files"][filename] = {
            "base_rows": int(len(base)),
            "v2_rows": int(len(v2)),
            "combined_rows": int(len(combined)),
        }

    for filename in JSONL_FILES:
        base_lines, base_seen = _iter_filtered_jsonl(base_dir / filename, {BASE_SYSTEM})
        v2_lines, v2_seen = _iter_filtered_jsonl(v2_dir / filename, V2_SYSTEMS)
        if filename == "api_logs.jsonl":
            _check_count("base api logs", base_seen, args.expected_base_traces, args.allow_partial)
            _check_count("v2 api logs", v2_seen, args.expected_v2_traces, args.allow_partial)
        with (out / filename).open("w", encoding="utf-8") as handle:
            for line in [*base_lines, *v2_lines]:
                handle.write(line + "\n")
        summary["files"][filename] = {
            "base_lines": int(base_seen),
            "v2_lines": int(v2_seen),
            "combined_lines": int(base_seen + v2_seen),
        }

    traces = pd.read_parquet(out / "traces.parquet")
    summary["trace_count"] = int(len(traces))
    summary["systems"] = sorted(traces["system"].astype(str).unique())
    summary["models"] = sorted(traces["model"].astype(str).unique())
    (out / "guard_v2_merge_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
