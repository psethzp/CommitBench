#!/usr/bin/env python3
"""Local setup sanity checks that do not run paid experiments."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path


REQUIRED_MODULES = [
    "boto3",
    "pandas",
    "pyarrow",
    "duckdb",
    "polars",
    "numpy",
    "scipy",
    "sklearn",
    "networkx",
    "pydantic",
    "jsonschema",
    "tqdm",
    "tenacity",
    "pytest",
    "vllm",
    "transformers",
    "accelerate",
    "sentencepiece",
    "openai",
    "anthropic",
    "huggingface_hub",
]


def _module_versions() -> dict[str, str]:
    versions = {}
    for name in REQUIRED_MODULES:
        importlib.import_module(name)
        package_name = "scikit-learn" if name == "sklearn" else name
        try:
            versions[name] = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "installed"
    return versions


def _gpu_summary() -> list[str]:
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader",
            ],
            text=True,
        )
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    if args.local_only:
        os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

    payload = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "modules": _module_versions(),
        "gpus": _gpu_summary(),
        "bedrock_main_experiments_launched": False,
        "repo_root": str(Path.cwd()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
