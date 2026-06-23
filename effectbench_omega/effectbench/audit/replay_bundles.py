#!/usr/bin/env python3
"""Create reviewer-readable witness bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _parse_sample(values: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key, count = value.split("=", 1)
        result[key] = int(count)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--traces", required=True)
    parser.add_argument("--frontier-certificates")
    parser.add_argument("--sample", nargs="+", default=["strict_excess=10", "minimal=10"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    certs = pd.read_parquet(args.certificates)
    traces = pd.read_parquet(args.traces).set_index("trace_id", drop=False)
    sample = _parse_sample(args.sample)
    selected = []
    for verdict, count in sample.items():
        key = "strict_excess" if "strict_excess" in verdict else "minimal"
        subset = certs[certs["verdict"].str.contains(key, regex=False)].head(count)
        selected.extend(subset.to_dict("records"))

    index_rows = []
    for record in selected:
        trace = traces.loc[record["trace_id"]].to_dict()
        bundle_path = out / f"{record['trace_id']}.json"
        payload = {
            "certificate": record,
            "model_trace": trace,
            "lower_effect_witness_trace": traces.loc[record["witness_trace_id"]].to_dict()
            if record.get("witness_trace_id") in traces.index
            else None,
            "terminal_equivalence_proof": record["terminal_equivalence_class"],
            "effect_vectors": {
                "trace": record["effect_vector"],
                "witness": record.get("witness_effect_vector", ""),
            },
            "dominance_relation": record["dominance_relation"],
            "verifier_log": "minimal_plus_v1",
        }
        bundle_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
        index_rows.append({"trace_id": record["trace_id"], "bundle": str(bundle_path), "verdict": record["verdict"]})

    pd.DataFrame(index_rows).to_csv(out / "reviewer_index.csv", index=False)
    print(f"wrote {len(index_rows)} bundles to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

