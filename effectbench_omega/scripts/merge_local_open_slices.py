#!/usr/bin/env python3
"""Merge per-model local-open slice outputs into one Stage 3 input directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DEFAULT_MODELS = [
    "mistral_small_3_2_24b_local",
    "qwen3_6_35b_a3b_local",
    "llama3_3_70b_awq_local",
    "gemma3_27b_it_local",
]

PARQUET_FILES = ["traces.parquet", "tool_ledgers.parquet", "runtime_logs.parquet"]
JSONL_FILES = ["api_logs.jsonl", "failures.jsonl"]


def _read_parquet(path: Path, model: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if "model" in df.columns:
        observed = set(df["model"].astype(str).unique())
        if observed != {model}:
            raise ValueError(f"{path} has model values {sorted(observed)}, expected only {model}")
    return df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-prefix", default="effectbench_omega/outputs/main_mc_postfix")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--out", default="effectbench_omega/outputs/main_mc_postfix_all_local")
    parser.add_argument("--expected-rows-per-model", type=int, default=5376)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {
        "input_prefix": args.input_prefix,
        "models": args.models,
        "expected_rows_per_model": args.expected_rows_per_model,
        "allow_partial": bool(args.allow_partial),
        "per_model": {},
    }

    model_dirs = {model: Path(f"{args.input_prefix}_{model}") for model in args.models}
    usable_models: list[str] = []
    for model, directory in model_dirs.items():
        missing = [name for name in PARQUET_FILES + JSONL_FILES if not (directory / name).exists()]
        if missing:
            if args.allow_partial:
                summary["per_model"][model] = {"status": "skipped_missing", "missing": missing}
                continue
            raise FileNotFoundError(f"{directory} is incomplete; missing {missing}")
        usable_models.append(model)

    if not usable_models:
        raise RuntimeError("no complete model slices found")

    for filename in PARQUET_FILES:
        frames = []
        for model in usable_models:
            path = model_dirs[model] / filename
            df = _read_parquet(path, model)
            if filename == "traces.parquet" and len(df) != args.expected_rows_per_model:
                raise ValueError(
                    f"{path} has {len(df)} rows, expected {args.expected_rows_per_model}; "
                    "use --expected-rows-per-model to override"
                )
            frames.append(df)
            summary["per_model"].setdefault(model, {})[filename.replace(".parquet", "_rows")] = int(len(df))
        pd.concat(frames, ignore_index=True).to_parquet(out / filename, index=False)

    for filename in JSONL_FILES:
        line_count = 0
        with (out / filename).open("w") as merged:
            for model in usable_models:
                path = model_dirs[model] / filename
                lines = path.read_text().splitlines()
                if filename == "api_logs.jsonl" and len(lines) != args.expected_rows_per_model:
                    raise ValueError(
                        f"{path} has {len(lines)} lines, expected {args.expected_rows_per_model}; "
                        "use --expected-rows-per-model to override"
                    )
                summary["per_model"].setdefault(model, {})[filename.replace(".jsonl", "_lines")] = len(lines)
                for line in lines:
                    if line.strip():
                        merged.write(line.rstrip() + "\n")
                        line_count += 1
        summary[filename.replace(".jsonl", "_lines")] = line_count

    traces = pd.read_parquet(out / "traces.parquet")
    summary["trace_count"] = int(len(traces))
    summary["models_merged"] = usable_models
    summary["models_merged_count"] = len(usable_models)
    summary["failure_count"] = sum(
        int(summary["per_model"].get(model, {}).get("failures_lines", 0)) for model in usable_models
    )
    (out / "merge_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
