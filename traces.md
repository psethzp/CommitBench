# 2026-06-30 Final Scope Update

Human/domain validation is intentionally skipped for this freeze and reported as
a limitation. The final artifact must not claim human agreement, kappa/alpha,
human preference, or human-audited correctness. The 300-bundle annotation
package remains included for optional follow-up.

The current paper-facing draft is `PAPER_EFFECTKERNELBENCH_FINAL.md`, and the
final zip should be rebuilt after this scope update so strict gates pass for the
no-human-eval claim set.

# EffectKernelBench Review-Rescue Execution Plan

## Summary

The rescue package says the current submission/artifact is not defensible yet. The core fix is not more broad model sweeps; it is: rename/reframe, expose one canonical split, prove raw model provenance, add direct close-method baselines, run human/domain validation, add uncertainty, and rebuild a clean artifact.

Important repo fact found during inspection: `effectbench_omega/outputs/base_nosystem_v1_all_local/api_logs.jsonl` already has `7,168` real local vLLM BASE proposal calls with raw outputs, timestamps, token counts, latency, and request IDs. So the recommended path is to normalize/prove those into the required provenance schema, run a fresh `512`-call smoke, and only rerun all `7,168` calls if the provenance audit fails.

## Staged Plan

| Stage | Work | GPU? | ETA |
|---|---|---:|---:|
| 0 | Create rescue branch, unpack package into review docs, update runbook/status, freeze old final zip as pre-review proof only | No | 1-2 h |
| 1 | Rename/reframe to `EffectKernelBench`; remove public `CommitBench`, `v1/v2/v3`, `legacy`, `bedrock`, stale leaderboard claims from paper/artifact-facing docs | No | 4-6 h |
| 2 | Build canonical `final_paired_control` from existing v3/base outputs; normalize names and copy only review-facing outputs | No | 4-8 h |
| 3 | Model-provenance audit: convert existing 7,168 local BASE logs into `outputs/model_proposals_final_no_system/raw_model_outputs.parquet`, model revisions, prompt hashes, hardware/software manifests, parse failures, server logs | No by default | 6-10 h |
| 3b | Fresh generation smoke: `32 tasks × 4 regimes × 1 seed × 4 models = 512` calls using final scripts/config | Yes, all 4 GPUs | 1.5-3 h |
| 3c | Conditional full rerun only if Stage 3 provenance fails: regenerate all `7,168` BASE proposals, then replay guards | Yes, all 4 GPUs | +8-12 h |
| 4 | Implement direct baselines: `FINAL_STATE`, `PROGENT_DSL_LITE`, `CMTF_CONTRACT`, `RACG_LITE`, `TOOLPRIV_DETECTOR`, `CORDON_LITE`, `REVISABILITY_ONLY`, `MODERN_PROJECTION_STACK`, `KERNEL_FULL` | No | 1-2 days |
| 5 | Human/domain validation package: sample 300 blinded bundles, create annotation forms/guidelines, collect 2-3 annotators, compute kappa/alpha/agreement | No | 3-5 days calendar |
| 6 | Stats hardening: 10k paired bootstrap, cluster bootstrap, leave-one model/family/regime, CIs for main/baseline/native/human claims | No | 0.5-1 day |
| 7 | No-oracle and EffectGuard reframing: static forbidden-field scan, sentinel invariance, shared-proposal proof, reference-controller wording | No | 0.5 day |
| 8 | Paper rewrite: 8-page ARR/EACL structure, SOTA novelty-boundary table, direct-baseline table, limitations in main paper | No | 2-3 days |
| 9 | Clean artifact rebuild as `EffectKernelBench_artifact.zip`; exact required layout, 3-command README, hashes, claim registry, final report | No | 1-2 days |
| 10 | Final submission gate: zip tests, reproduce checks, tests, claim registry, stale-term scan, PDF checks | No | 0.5-1 day |

Recommended overall ETA:
- Best case using existing 7,168-call provenance: **9-14 calendar days**, mainly gated by human validation.
- If full 7,168-call rerun is required: **add 8-12 GPU-hours**, usually still within the same calendar day.
- If annotators are not available quickly: the submission cannot pass the new review gate; delay by however long annotation takes.

## Key Implementation Changes

- Create a clean review-facing artifact tree named `EffectKernelBench_artifact/`; do not reuse the current development tree as the final artifact.
- Expose only one canonical split name: `final_paired_control`.
- Convert current `base_nosystem_v1_all_local` and `shared_proposal_v3_nosystem_all_local` into review-facing provenance/replay outputs; hide old split labels in excluded dev archives.
- Add final scripts required by the package:
  - `scripts/reproduce.py --check-only`
  - `scripts/reproduce.py --tables`
  - `scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml`
  - `scripts/build_baselines.py --config configs/baselines.yaml`
  - `scripts/verify_claim_registry.py --registry metrics/claim_registry.csv`
  - `scripts/final_submission_gate.py --strict`
- Fix `run_online.py --help` so it does not import Bedrock or unavailable backends at import time.
- Label all close-method baselines as deterministic projections / faithful approximations, never official SOTA reimplementations.
- Frame EffectGuard only as a no-oracle reference controller / constructive upper bound.

## Test And Acceptance Gates

Run after implementation:

```bash
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_online.py --help
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
python scripts/build_baselines.py --config configs/baselines.yaml
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
pytest -q tests
```

Required empirical gates:
- Raw model proposal provenance exists for `7,168` local calls, or paper explicitly weakens the claim.
- Fresh smoke produces `512` local model calls in the same schema.
- Direct baselines include Progent-lite, CMTF, RACG-lite, ToolPriv, Cordon, final-state, and kernel-full.
- Human validation has at least 2 annotators per item over 300 bundles.
- Minimum human gates: label agreement `>= 80%`, strict-excess witness preference `>= 85%`, terminal-equivalence agreement `>= 90%`, admissibility agreement `>= 85%`, kappa `>= 0.50` with caveat.
- No-oracle static scan has `0` violations and sentinel invariance is `100%`.
- Every paper number maps to claim registry source, filter, script, and hash.
- Stale-term scan is clean or justified in `FINAL_SUBMISSION_REPORT.md`.

## Assumptions

- Use public name `EffectKernelBench`.
- Use existing 7,168 local vLLM BASE proposal logs as primary provenance if they pass normalization/audit.
- Run the 512-call fresh smoke regardless, because the review package requires clean-pipeline proof.
- Do not run Bedrock/API/commercial models.
- Do not add new broad models.
- Use all 4 local L40 GPUs only for Stage 3b and conditional Stage 3c.
- Human/domain validation requires the user to provide or approve 2-3 annotators; without that, the paper must be delayed or claims weakened.


Implemented the rescue plan end to end, except the one thing that genuinely needs humans: external annotation.

Built final clean artifact:

[EffectKernelBench_artifact.zip](/home/ubuntu/nachiket/CommitBench/EffectKernelBench_artifact.zip)

```text
size: 4.0 MiB
artifact dir: 16 MiB
files: 690
sha256: cd1ad054d2552dcd8a4e6971f11348f82dfe67ea3e9f797dd9a1e5f39dc6d73a
branch: effectkernelbench-review-rescue
```

What’s now done:

- Unpacked rescue package into `docs/review_rescue_package/`.
- Added clean `EffectKernelBench_artifact/` builder and zip packager.
- Exposed canonical split: `final_paired_control`.
- Normalized 7,168 real local vLLM BASE proposal calls into provenance parquet.
- Added direct baselines: final-state, Progent-lite, CMTF, RACG-lite, ToolPriv, Cordon, revisability, modern stack, kernel-full.
- Added annotation package with 300 blinded bundles.
- Added uncertainty, no-oracle, claim registry, final gate, reproduce scripts.
- Fixed `run_online.py --help` so it does not import paid/Bedrock backends at import time.
- Ran fresh 512-call local smoke across all 4 models with TP=4.

Fresh smoke result:

```text
512 traces / 512 API logs
0 failures
512 merged certificates
no-oracle: 512/512
local cost: $0
GPUs: TP=4 on 0,1,2,3
```

Only caveat in fresh smoke: Qwen had 11/128 non-JSON parser paths: 9 text-scan, 1 low/high-format, 4 repaired fallback. Other three models were 128/128 JSON. This is logged in the artifact summary.

Checks run:

```text
python -m zipfile -t EffectKernelBench_artifact.zip: pass
unzip -tq EffectKernelBench_artifact.zip: pass
python scripts/reproduce.py --check-only: pass
python scripts/reproduce.py --tables: pass
python scripts/run_online.py --help: pass
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml: pass/reuses completed smoke
python scripts/build_baselines.py --config configs/baselines.yaml: pass
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv: pass
pytest -q tests: pass
```

Strict final gate status:

```text
artifact_ok: true
human_validation_complete: false
human_validation_skipped_reported: true
problems: []
```

Updated docs:

- [RUNBOOK_EFFECTKERNELBENCH_RESCUE.md](/home/ubuntu/nachiket/CommitBench/RUNBOOK_EFFECTKERNELBENCH_RESCUE.md)
- [README.md](/home/ubuntu/nachiket/CommitBench/README.md)
- [results.md](/home/ubuntu/nachiket/CommitBench/results.md)
- [implementations.md](/home/ubuntu/nachiket/CommitBench/implementations.md)

No vLLM/queue jobs are running now, and GPUs are idle. Human validation is skipped for this freeze; the annotation package remains optional follow-up, and human-validation claims must stay absent unless that follow-up is completed later.
