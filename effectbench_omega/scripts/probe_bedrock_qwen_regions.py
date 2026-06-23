#!/usr/bin/env python3
"""List Qwen Bedrock model availability across candidate regions."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from effectbench.clients.bedrock import configure_credentials


DEFAULT_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "ap-south-1",
    "ap-northeast-1",
    "eu-west-1",
    "eu-west-2",
    "eu-south-1",
    "eu-north-1",
    "sa-east-1",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regions", nargs="+", default=DEFAULT_REGIONS)
    parser.add_argument("--out", default="effectbench_omega/models/qwen_bedrock_region_scan.csv")
    parser.add_argument("--credential-source", choices=["ec2-role", "default"], default="ec2-role")
    args = parser.parse_args()

    import boto3

    rows = []
    for region in args.regions:
        configure_credentials(region, args.credential_source)
        try:
            client = boto3.client("bedrock", region_name=region)
            summaries = client.list_foundation_models(byProvider="Qwen").get("modelSummaries", [])
            if not summaries:
                rows.append({"region": region, "model_id": "", "model_name": "", "status": "no_qwen_listed"})
            for summary in summaries:
                rows.append(
                    {
                        "region": region,
                        "model_id": summary.get("modelId", ""),
                        "model_name": summary.get("modelName", ""),
                        "status": "listed",
                    }
                )
        except Exception as exc:
            rows.append({"region": region, "model_id": "", "model_name": "", "status": f"{type(exc).__name__}: {exc}"})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["region", "model_id", "model_name", "status"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

