from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_effectkernelbench_artifact_core_files_exist():
    required = [
        "EffectKernelBench_artifact/README.md",
        "EffectKernelBench_artifact/outputs/model_proposals_final_no_system/raw_model_outputs.parquet",
        "EffectKernelBench_artifact/outputs/final_paired_control/certificates.parquet",
        "EffectKernelBench_artifact/tables/direct_baselines.csv",
        "EffectKernelBench_artifact/metrics/claim_registry.csv",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel


def test_effectkernelbench_artifact_expected_row_counts():
    proposals = pd.read_parquet(
        ROOT / "EffectKernelBench_artifact/outputs/model_proposals_final_no_system/raw_model_outputs.parquet"
    )
    certs = pd.read_parquet(ROOT / "EffectKernelBench_artifact/outputs/final_paired_control/certificates.parquet")
    assert len(proposals) == 7168
    assert len(certs) == 21504
    assert proposals["raw_model_text"].astype(str).ne("").all()


def test_direct_baselines_include_review_required_rows():
    baselines = pd.read_csv(ROOT / "EffectKernelBench_artifact/tables/direct_baselines.csv")
    required = {
        "FINAL_STATE",
        "PROGENT_DSL_LITE",
        "CMTF_CONTRACT",
        "RACG_LITE",
        "TOOLPRIV_DETECTOR",
        "CORDON_LITE",
        "REVISABILITY_ONLY",
        "MODERN_PROJECTION_STACK",
        "KERNEL_FULL",
    }
    assert required.issubset(set(baselines["system"]))
