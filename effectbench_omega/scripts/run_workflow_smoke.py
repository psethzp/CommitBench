#!/usr/bin/env python3
"""Run a small end-to-end workflow smoke without full experiments."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = str(ROOT / ".venv/bin/python")


def run(cmd: list[str]) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def pipeline(split: str, out: str, limit: int, call_local_model: bool) -> None:
    run(
        [
            PYTHON,
            "effectbench_omega/scripts/run_online.py",
            "--config",
            "effectbench_omega/configs/minimal_plus.yaml",
            "--manifest",
            "effectbench_omega/manifests/tasks_minimal_plus.csv",
            "--split",
            split,
            "--systems",
            "BASE",
            "PROJ_GUARD",
            "EFFECTGUARD",
            "--models",
            "qwen3_30b_a3b_local",
            "--regimes",
            "FULL",
            "MEMORY_REVISE",
            "ADV_EFFECT",
            "--out",
            out,
            "--limit",
            str(limit),
            *(["--call-local-model"] if call_local_model else ["--dry-run"]),
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/kernel/verifier.py",
            "--traces",
            f"{out}/traces.parquet",
            "--schemas",
            "effectbench_omega/schemas",
            "--out",
            f"{out}/kernel",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/audit/no_oracle_report.py",
            "--runtime-logs",
            f"{out}/runtime_logs.parquet",
            "--out",
            f"effectbench_omega/tables/no_oracle_{split}.csv",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/baselines/project.py",
            "--traces",
            f"{out}/traces.parquet",
            "--certificates",
            f"{out}/kernel/certificates.parquet",
            "--baselines",
            "FINAL_STATE",
            "CORE_DFA",
            "MINISCOPE_PERMISSION",
            "CONTRACT_MENU_CMTF",
            "REVISABILITY",
            "MODERNSTACK_PROJECTION",
            "KERNEL_FULL",
            "--out",
            f"effectbench_omega/tables/projection_loss_{split}.csv",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/audit/cegar.py",
            "--traces",
            f"{out}/traces.parquet",
            "--schemas",
            "effectbench_omega/schemas",
            "--omit-fields",
            "outbox",
            "policy_obligation",
            "contract_artifact_hash",
            "virtual_clock",
            "memory_cache",
            "user_visible_exposure",
            "compensation_or_payment_hold",
            "--out",
            f"effectbench_omega/tables/cegar_rejections_{split}.csv",
            "--label-changes",
            f"effectbench_omega/tables/cegar_label_changes_{split}.csv",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/metrics/lattice_sensitivity.py",
            "--certificates",
            f"{out}/kernel/certificates.parquet",
            "--lattices",
            "effectbench_omega/configs/lattices",
            "--out",
            f"effectbench_omega/tables/lattice_sensitivity_{split}.csv",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/metrics/bootstrap.py",
            "--certificates",
            f"{out}/kernel/certificates.parquet",
            "--group-by",
            "task_id",
            "model",
            "seed",
            "family",
            "--methods",
            "paired_bootstrap",
            "task_cluster",
            "hierarchical",
            "--out",
            f"effectbench_omega/tables/uncertainty_{split}.csv",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/audit/replay_bundles.py",
            "--certificates",
            f"{out}/kernel/certificates.parquet",
            "--traces",
            f"{out}/traces.parquet",
            "--sample",
            "strict_excess=3",
            "minimal=3",
            "--out",
            f"effectbench_omega/witness_bundles/{split}",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/audit/replay_certificates.py",
            "--bundle-dir",
            f"effectbench_omega/witness_bundles/{split}",
            "--out",
            f"effectbench_omega/reports/certificate_replay_{split}.md",
            "--strict",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/metrics/cost_audit.py",
            "--logs",
            f"{out}/api_logs.jsonl",
            "--out",
            f"effectbench_omega/reports/{split}_cost.md",
        ]
    )
    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/metrics/aggregate.py",
            "--main-certificates",
            f"{out}/kernel/certificates.parquet",
            "--projection-loss",
            f"effectbench_omega/tables/projection_loss_{split}.csv",
            "--cost-logs",
            f"{out}/api_logs.jsonl",
            "--out-tables",
            f"effectbench_omega/tables/{split}",
            "--out-figures",
            f"effectbench_omega/figures/{split}",
            "--claim-registry",
            f"effectbench_omega/metrics/claim_registry_{split}.csv",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-limit", type=int, default=15)
    parser.add_argument("--local-model-limit", type=int, default=3)
    parser.add_argument("--skip-local-model", action="store_true")
    args = parser.parse_args()

    run(
        [
            PYTHON,
            "effectbench_omega/effectbench/families/build_manifest.py",
            "--out",
            "effectbench_omega/manifests/tasks_minimal_plus.csv",
        ]
    )
    pipeline("workflow_smoke_dry", "effectbench_omega/outputs/workflow_smoke_dry", args.dry_limit, False)
    if not args.skip_local_model:
        pipeline(
            "workflow_smoke_local_qwen",
            "effectbench_omega/outputs/workflow_smoke_local_qwen",
            args.local_model_limit,
            True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
