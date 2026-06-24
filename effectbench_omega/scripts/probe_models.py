#!/usr/bin/env python3
"""Capped provider/model probes.

This script intentionally refuses to run paid calls unless --allow-paid-probe is
set. It never launches main experiments and writes a compact model snapshot.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from effectbench.clients.bedrock import (
    MODEL_CANDIDATES,
    available_invocable_ids,
    converse_text,
    identity,
    select_region_and_model,
)


DEFAULT_MODELS = [
    "qwen3_30b_a3b_local",
    "qwen3_235b_a22b_2507_bedrock",
    "qwen3_coder_480b_a35b_bedrock",
    "deepseek_v3_2_bedrock",
    "gpt_5_4_bedrock",
    "gpt_5_5_bedrock",
    "claude_opus_4_8_bedrock",
]

def _probe_local() -> dict[str, object]:
    import requests

    url = "http://localhost:8001/v1/models"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        ids = [item["id"] for item in data.get("data", [])]
        return {
            "model": "qwen3_30b_a3b_local",
            "provider": "local_vllm",
            "status": "available" if "qwen3_30b_a3b_local" in ids else "not_listed",
            "region": "localhost",
            "provider_model_id": "qwen3_30b_a3b_local",
            "paid_call_made": False,
            "cost_cap_usd": 0,
            "notes": json.dumps(data)[:500],
        }
    except Exception as exc:
        return {
            "model": "qwen3_30b_a3b_local",
            "provider": "local_vllm",
            "status": "error",
            "region": "localhost",
            "provider_model_id": "qwen3_30b_a3b_local",
            "paid_call_made": False,
            "cost_cap_usd": 0,
            "notes": f"{type(exc).__name__}: {exc}",
        }


def _bedrock_list(region: str, credential_source: str) -> tuple[bool, str]:
    try:
        count = len(available_invocable_ids(region, credential_source))
        return True, f"list_invocable_ids_ok count={count}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _bedrock_tiny_call(
    model_name: str,
    region: str,
    credential_source: str,
    strict_expected: bool,
    max_tokens: int,
) -> dict[str, object]:
    try:
        result = converse_text(
            model_name,
            "Reply with OK only.",
            region=region,
            credential_source=credential_source,
            max_tokens=max_tokens,
            temperature=0.0,
            strict_expected=strict_expected,
        )
        usage = result["usage"]
        return {
            "model": model_name,
            "provider": "bedrock",
            "status": "available",
            "region": result["region"],
            "provider_model_id": result["model_id"],
            "model_resolution": result["model_resolution"],
            "paid_call_made": True,
            "cost_cap_usd": "",
            "input_tokens": usage.get("inputTokens", 0),
            "output_tokens": usage.get("outputTokens", 0),
            "latency_s": round(result["latency_s"], 3),
            "notes": result["text"][:200],
        }
    except Exception as exc:
        try:
            region, model_id, resolution = select_region_and_model(
                model_name, region, credential_source, strict_expected
            )
        except Exception:
            model_id, resolution = "", "selection_failed"
        return {
            "model": model_name,
            "provider": "bedrock",
            "status": "error",
            "region": region,
            "provider_model_id": model_id,
            "model_resolution": resolution,
            "paid_call_made": True,
            "cost_cap_usd": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_s": "",
            "notes": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-cost-usd", type=float, default=5.0)
    parser.add_argument("--allow-paid-probe", action="store_true")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--regions", nargs="+", default=["us-east-1", "us-west-2", "us-east-2", "ap-southeast-2"])
    parser.add_argument("--max-paid-calls-per-model", type=int, default=1)
    parser.add_argument("--probe-max-tokens", type=int, default=96)
    parser.add_argument("--credential-source", choices=["ec2-role", "default"], default="ec2-role")
    parser.add_argument("--strict-expected-model-id", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    if "qwen3_30b_a3b_local" in args.models:
        rows.append(_probe_local())

    if any(model.endswith("_bedrock") for model in args.models) and not args.allow_paid_probe:
        for model in args.models:
            if model.endswith("_bedrock"):
                rows.append(
                    {
                        "model": model,
                        "provider": "bedrock",
                        "status": "skipped_paid_probe_not_allowed",
                        "region": "",
                        "provider_model_id": MODEL_CANDIDATES.get(model, [(model, "literal")])[0][0],
                        "model_resolution": "not_probed",
                        "paid_call_made": False,
                        "cost_cap_usd": args.max_cost_usd,
                        "notes": "rerun with --allow-paid-probe for a capped tiny sanity call",
                    }
                )
    elif args.allow_paid_probe:
        if args.max_cost_usd > 5:
            raise SystemExit("--max-cost-usd must stay <= 5 for sanity probes")
        try:
            who = identity(args.regions[0], args.credential_source)
            identity_note = f"caller={who.get('Arn', '')}"
        except Exception as exc:
            identity_note = f"identity_error={type(exc).__name__}: {exc}"
        for model in args.models:
            if model == "qwen3_30b_a3b_local":
                continue
            if model not in MODEL_CANDIDATES:
                rows.append(
                    {
                        "model": model,
                        "provider": "bedrock",
                        "status": "missing_model_id_mapping",
                        "region": "",
                        "provider_model_id": "",
                        "model_resolution": "",
                        "paid_call_made": False,
                        "cost_cap_usd": args.max_cost_usd,
                        "notes": "model family probe only or mapping unavailable",
                    }
                )
                continue
            selected_region = ""
            list_note = ""
            for region in args.regions:
                ok, note = _bedrock_list(region, args.credential_source)
                if ok:
                    selected_region = region
                    list_note = note
                    break
                list_note = note
            if not selected_region:
                rows.append(
                    {
                        "model": model,
                        "provider": "bedrock",
                        "status": "error",
                        "region": "",
                        "provider_model_id": MODEL_CANDIDATES[model][0][0],
                        "model_resolution": "not_selected",
                        "paid_call_made": False,
                        "cost_cap_usd": args.max_cost_usd,
                        "notes": f"{identity_note}; {list_note}",
                    }
                )
                continue
            selected_region, model_id, resolution = select_region_and_model(
                model,
                selected_region,
                args.credential_source,
                args.strict_expected_model_id,
            )
            if args.max_paid_calls_per_model <= 0:
                rows.append(
                    {
                        "model": model,
                        "provider": "bedrock",
                        "status": "bedrock_list_ok_no_paid_call",
                        "region": selected_region,
                        "provider_model_id": model_id,
                        "model_resolution": resolution,
                        "paid_call_made": False,
                        "cost_cap_usd": args.max_cost_usd,
                        "notes": f"{identity_note}; {list_note}",
                    }
                )
            else:
                row = _bedrock_tiny_call(
                    model,
                    selected_region,
                    args.credential_source,
                    args.strict_expected_model_id,
                    args.probe_max_tokens,
                )
                row["cost_cap_usd"] = args.max_cost_usd
                row["notes"] = f"{identity_note}; " + str(row.get("notes", ""))
                rows.append(row)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} probe rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
