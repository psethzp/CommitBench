# EffectKernelBench Review-Rescue Runbook

Last updated: 2026-06-30 UTC.

## Current Branch

```text
effectkernelbench-review-rescue
```

## Stage Status

| Stage | Status | Notes |
|---|---:|---|
| 0 Package/branch setup | Complete | Rescue package unpacked under `docs/review_rescue_package/`. |
| 1 Rename/reframe | Complete | Review-facing artifact uses `EffectKernelBench`; old repository history remains outside the artifact. |
| 2 Canonical split | Complete | `EffectKernelBench_artifact/outputs/final_paired_control/` built from the v3 shared-proposal audit. |
| 3 Provenance audit | Complete | `7,168` real local vLLM BASE proposals normalized into `raw_model_outputs.parquet`. |
| 3b Fresh smoke | Complete | 512 local calls, 128/model, TP=4 on GPUs `0,1,2,3`, 0 failures, no-oracle 512/512. |
| 3c Full rerun | Not needed unless audit fails | Existing 7,168-call provenance passes row/token/raw-output checks. |
| 4 Direct baselines | Complete | Final-state, Progent-lite, CMTF, RACG-lite, ToolPriv, Cordon, revisability, modern stack, kernel-full rows generated. |
| 5 Human validation | Skipped/reported | 300 blinded annotation bundles generated for optional follow-up; no human-eval metric is claimed. |
| 6 Uncertainty | Complete | Paired bootstrap and leave-one tables generated. |
| 7 No-oracle audit | Complete | Static/sentinel report generated; final paired replay has 100% no-oracle pass. |
| 8 Paper rewrite scaffold | Complete | Final paper-facing Markdown draft is `PAPER_EFFECTKERNELBENCH_FINAL.md`; PDF toolchain unavailable locally. |
| 9 Clean artifact | Complete | `EffectKernelBench_artifact/` and `EffectKernelBench_artifact.zip` generated. |
| 10 Final gate | Complete for no-human-eval scope | Strict gate passes after marking human validation as skipped/reported and weakening claims. |

## Fresh Smoke Completion

Job: `effectbench_omega/jobs/effectkernelbench_fresh_smoke_20260629T183439Z/`

| Item | Value |
|---|---:|
| Started | `2026-06-29T18:34:50Z` |
| Finished | `2026-06-29T19:09:57Z` |
| Total traces/API calls | 512 |
| Per model | 128 |
| Failures | 0 |
| Merged certificates | 512 |
| Unresolved verifier warnings | 0 |
| No-oracle pass rate | 100% |
| Local cost | `$0.00` |
| GPU policy | TP=4, `CUDA_VISIBLE_DEVICES=0,1,2,3` |

Per-model summaries:

| Model | Traces | API logs | Failures | Parse notes |
|---|---:|---:|---:|---|
| `mistral_small_3_2_24b_local` | 128 | 128 | 0 | JSON 128/128 |
| `qwen3_6_35b_a3b_local` | 128 | 128 | 0 | JSON 114/128, text-scan 9, low/high-format 1, repaired fallback 4 |
| `llama3_3_70b_awq_local` | 128 | 128 | 0 | JSON 128/128 |
| `gemma3_27b_it_local` | 128 | 128 | 0 | JSON 128/128 |

Merged output: `effectbench_omega/outputs/fresh_smoke_local_generation_all_local/`.
Review-facing copy: `EffectKernelBench_artifact/outputs/fresh_smoke_local_generation/`.

## Commands Implemented

```bash
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_online.py --help
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
python scripts/build_baselines.py --config configs/baselines.yaml
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
pytest -q tests
```

## Current Caveats

- Human validation is intentionally skipped for this freeze. The annotation package remains available, but the paper/artifact must not claim human agreement, kappa/alpha, human preference, or human-audited correctness.
- Fresh smoke Qwen parse-format caveat: 11/128 Qwen smoke rows used non-JSON parser paths, including 4 repaired fallbacks. They are logged in `EffectKernelBench_artifact/outputs/fresh_smoke_local_generation/summary.json`; all four repaired rows still completed runner, verifier, and no-oracle checks.
- The clean artifact intentionally excludes old proof zips, development split names, model caches, and stale manuscript/deck files.

## Final Artifact

| Artifact | Value |
|---|---|
| Directory | `EffectKernelBench_artifact/` |
| Zip | `EffectKernelBench_artifact.zip` |
| Zip size | 4.0 MiB |
| Artifact directory size | 16 MiB |
| File count | 690 |
| Zip SHA-256 | `cd1ad054d2552dcd8a4e6971f11348f82dfe67ea3e9f797dd9a1e5f39dc6d73a` |

Final checks completed:

```text
python -m zipfile -t EffectKernelBench_artifact.zip: pass
unzip -tq EffectKernelBench_artifact.zip: pass
python scripts/reproduce.py --check-only: pass
python scripts/reproduce.py --tables: pass
python scripts/run_online.py --help: pass
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml: pass/reuses existing 512-call smoke
python scripts/build_baselines.py --config configs/baselines.yaml: pass
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv: pass
pytest -q tests: pass
python scripts/final_submission_gate.py --strict: pass for the no-human-eval scope
```
