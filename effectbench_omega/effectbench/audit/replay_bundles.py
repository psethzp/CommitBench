#!/usr/bin/env python3
"""Create reviewer-readable witness bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def _parse_sample(values: list[str]) -> dict[str, int | None]:
    result: dict[str, int | None] = {}
    for value in values:
        key, count = value.split("=", 1)
        result[key] = None if count == "all" else int(count)
    return result


def _subset(certs: pd.DataFrame, selector: str) -> pd.DataFrame:
    verdict = certs["verdict"].astype(str)
    if "strict_excess" in selector:
        return certs[verdict.eq("strict_excess")]
    if "incomparable" in selector:
        reason = certs.get("incomparability_reason")
        if reason is None:
            return certs[verdict.str.contains("incomparable", regex=False)]
        return certs[verdict.str.contains("incomparable", regex=False) | reason.astype(str).ne("")]
    if "necessary_high" in selector:
        reason = certs.get("necessary_high_reason")
        if reason is None:
            return certs.head(0)
        return certs[reason.astype(str).ne("")]
    if "minimal" in selector:
        return certs[verdict.str.startswith("minimal")]
    return certs[verdict.str.contains(selector, regex=False)]


def _select_records(certs: pd.DataFrame, sample: dict[str, int | None]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for selector, count in sample.items():
        subset = _subset(certs, selector)
        if count is not None:
            subset = subset.head(count)
        for record in subset.to_dict("records"):
            selected.setdefault(str(record["trace_id"]), record)
    return list(selected.values())


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
    selected = _select_records(certs, sample)

    index_rows = []
    for record in selected:
        trace = traces.loc[record["trace_id"]].to_dict()
        bundle_path = out / f"{record['trace_id']}.json"
        witness_trace = None
        witness_candidate = None
        witness_trace_id = record.get("witness_trace_id")
        if witness_trace_id in traces.index:
            witness_trace = traces.loc[witness_trace_id].to_dict()
        elif record.get("witness_actions"):
            witness_candidate = {
                "candidate_id": record.get("witness_candidate_id") or witness_trace_id,
                "actions": str(record.get("witness_actions", "")).split("|"),
                "effect_vector": record.get("witness_effect_vector", ""),
                "admissibility_proof": record.get("admissibility_proof", ""),
            }
        payload = {
            "certificate": record,
            "model_trace": trace,
            "lower_effect_witness_trace": witness_trace,
            "lower_effect_witness_candidate": witness_candidate,
            "terminal_equivalence_proof": record["terminal_equivalence_class"],
            "effect_vectors": {
                "trace": record["effect_vector"],
                "witness": record.get("witness_effect_vector", ""),
            },
            "dominance_relation": record["dominance_relation"],
            "verifier_log": record.get("verifier_version", "minimal_plus_v1"),
        }
        bundle_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
        index_rows.append({"trace_id": record["trace_id"], "bundle": str(bundle_path), "verdict": record["verdict"]})

    pd.DataFrame(index_rows).to_csv(out / "reviewer_index.csv", index=False)
    print(f"wrote {len(index_rows)} bundles to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
