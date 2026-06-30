from pathlib import Path

def test_required_artifact_files_exist():
    root = Path(__file__).resolve().parents[1]
    for rel in ['tables/main_results.csv','tables/direct_baselines.csv','metrics/claim_registry.csv','outputs/final_paired_control/certificates.parquet']:
        assert (root / rel).exists()
