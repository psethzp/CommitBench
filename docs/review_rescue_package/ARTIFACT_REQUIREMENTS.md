# ARTIFACT_REQUIREMENTS.md — exact final artifact contents

## Required top-level layout

```text
EffectKernelBench_artifact/
  README.md
  LICENSE
  environment.lock
  configs/
    final_paired_control.yaml
    fresh_smoke.yaml
    baselines.yaml
    annotation.yaml
  effectkernelbench/
    __init__.py
    verifier/
    baselines/
    runtime/
    data/
    metrics/
  scripts/
    reproduce.py
    run_online.py
    run_fresh_smoke.py
    build_tables.py
    build_baselines.py
    verify_claim_registry.py
    final_submission_gate.py
    hash_artifact.py
  data/
    task_cards.parquet
    policy_cards.parquet
    effect_lattice.json
    terminal_equivalence_schema.json
  manifests/
    tasks.csv
    model_revisions.csv
    prompt_templates.json
    hardware_manifest.json
    software_manifest.json
  outputs/
    model_proposals_final_no_system/
      raw_model_outputs.parquet
      api_logs.parquet
      parse_failures.csv
      prompt_hashes.csv
      inference_server_logs.jsonl
    final_paired_control/
      ledger.parquet
      certificates.parquet
      summary.json
      kernel_canonical/
        certificates_enumerated.parquet
        frontier.parquet
    native_validation/
      ledger.parquet
      certificates.parquet
      summary.json
    necessary_high_incomparable_stress/
      ledger.parquet
      certificates.parquet
      summary.json
  tables/
    main_results.csv
    direct_baselines.csv
    native_validation.csv
    stress_validation.csv
    human_validation.csv
    uncertainty.csv
    leave_one_robustness.csv
  figures/
    pipeline.pdf
    projection_loss.pdf
    strict_excess_by_family_regime.pdf
  metrics/
    claim_registry.csv
  witness_bundles/
    sampled_review_bundles/
    annotation_bundles/
  annotation/
    annotation_guidelines.md
    annotation_sample.csv
    annotation_results.csv
    annotation_report.md
  tests/
    test_verifier.py
    test_baselines.py
    test_no_oracle.py
    test_reproduce.py
  hashes/
    SHA256SUMS.txt
```

## Required commands

From a clean checkout:

```bash
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_online.py --help
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
python scripts/build_baselines.py --config configs/baselines.yaml
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
pytest -q tests
```

Zip checks:

```bash
zip -T EffectKernelBench_artifact.zip
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
```

## Prohibited review-facing artifacts

Do not include paths, table rows, configs, or labels containing:

```text
minimal_plus
workflow_smoke
legacy
v1
v2
v3
bedrock
openai
anthropic
gemini
api_frontier
old_claim_registry
/home/ubuntu
/mnt/data
nachiket
```

If a prohibited string appears in a dependency lockfile or harmless third-party package name, list it in `FINAL_SUBMISSION_REPORT.md`.

## Claim registry schema

Every row must include:

```text
claim_id
paper_location
claim_text
source_file
source_sha256
filter_predicate
aggregation_script
aggregation_function
random_seed_or_na
ci_method_or_na
expected_value
actual_value
last_verified_utc
```

## Model provenance schema

Every raw model-output row must include:

```text
run_id
timestamp_utc
host_id
hardware_summary
model_id
model_revision_or_local_hash
backend
backend_version
decoding_temperature
decoding_top_p
max_tokens
seed
task_id
family
regime
prompt_template_id
prompt_sha256
rendered_prompt_sha256
raw_model_text
parsed_action_json
parse_status
repair_status
input_tokens
output_tokens
latency_ms
```

If token counts are unavailable from backend, set to `null` and explain in `software_manifest.json`; do not set to zero unless truly zero.

## Final artifact report

Create `artifact_check_report.md` with:

- command outputs,
- SHA summary,
- list of generated paper tables,
- number of raw model calls,
- number of replayed paired rows,
- any intentional exclusions.
