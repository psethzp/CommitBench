#!/usr/bin/env python3
"""Check or reproduce the local EffectBench minimal-plus pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv/bin/python"


REQUIRED_LOCAL_FILES = [
    "effectbench_omega/configs/minimal_plus.yaml",
    "effectbench_omega/configs/models.yaml",
    "effectbench_omega/schemas/effect_signature.schema.json",
    "effectbench_omega/schemas/effect_kernel.schema.json",
    "effectbench_omega/manifests/tasks_minimal_plus.csv",
    "effectbench_omega/outputs/workflow_smoke_dry/traces.parquet",
    "effectbench_omega/outputs/workflow_smoke_dry/kernel/certificates.parquet",
    "effectbench_omega/outputs/workflow_smoke_local_qwen/traces.parquet",
    "effectbench_omega/outputs/workflow_smoke_local_qwen/kernel/certificates.parquet",
    "effectbench_omega/tables/no_oracle_workflow_smoke_dry.csv",
    "effectbench_omega/tables/no_oracle_workflow_smoke_local_qwen.csv",
    "effectbench_omega/tables/projection_loss_workflow_smoke_dry.csv",
    "effectbench_omega/tables/projection_loss_workflow_smoke_local_qwen.csv",
    "effectbench_omega/tables/cegar_rejections_workflow_smoke_dry.csv",
    "effectbench_omega/tables/cegar_rejections_workflow_smoke_local_qwen.csv",
    "effectbench_omega/tables/lattice_sensitivity_workflow_smoke_dry.csv",
    "effectbench_omega/tables/lattice_sensitivity_workflow_smoke_local_qwen.csv",
    "effectbench_omega/tables/uncertainty_workflow_smoke_dry.csv",
    "effectbench_omega/tables/uncertainty_workflow_smoke_local_qwen.csv",
    "effectbench_omega/reports/certificate_replay_workflow_smoke_dry.md",
    "effectbench_omega/reports/certificate_replay_workflow_smoke_local_qwen.md",
    "effectbench_omega/metrics/claim_registry_workflow_smoke_dry.csv",
    "effectbench_omega/metrics/claim_registry_workflow_smoke_local_qwen.csv",
]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def check_only() -> int:
    missing = [path for path in REQUIRED_LOCAL_FILES if not (ROOT / path).exists()]
    endpoint_ok = subprocess.run(
        ["curl", "-sS", "--max-time", "5", "http://localhost:8001/v1/models"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = {
        "missing_required_files": missing,
        "local_qwen_endpoint_ok": endpoint_ok.returncode == 0,
        "bedrock_main_experiments_run": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if missing else 0


def reproduce_local(limit: int) -> int:
    run([str(PYTHON), "effectbench_omega/effectbench/families/build_manifest.py", "--out", "effectbench_omega/manifests/tasks_minimal_plus.csv"])
    run(
        [
            str(PYTHON),
            "effectbench_omega/scripts/run_online.py",
            "--config",
            "effectbench_omega/configs/minimal_plus.yaml",
            "--manifest",
            "effectbench_omega/manifests/tasks_minimal_plus.csv",
            "--split",
            "local_qwen_reproduce",
            "--systems",
            "BASE",
            "PROJ_GUARD",
            "EFFECTGUARD",
            "--models",
            "qwen3_30b_a3b_local",
            "--regimes",
            "FULL",
            "CONCAT",
            "SHARDED",
            "SNOWBALL",
            "REVISE",
            "MEMORY_REVISE",
            "ADV_EFFECT",
            "--out",
            "effectbench_omega/outputs/local_qwen_reproduce",
            "--limit",
            str(limit),
            "--call-local-model",
        ]
    )
    run(
        [
            str(PYTHON),
            "effectbench_omega/effectbench/kernel/verifier.py",
            "--traces",
            "effectbench_omega/outputs/local_qwen_reproduce/traces.parquet",
            "--schemas",
            "effectbench_omega/schemas",
            "--out",
            "effectbench_omega/outputs/local_qwen_reproduce/kernel",
        ]
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--local-limit", type=int, default=90)
    args = parser.parse_args()
    if args.check_only:
        return check_only()
    return reproduce_local(args.local_limit)


if __name__ == "__main__":
    raise SystemExit(main())
