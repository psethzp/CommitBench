# EffectBench-Omega EACL Rescue V2 Runbook

Last updated: 2026-06-25 UTC

## Operating Rules

This runbook tracks the V2 rescue plan under `V2/`.

Hard boundaries:

- Do not use Bedrock/API.
- Do not add or download new headline models.
- Do not overwrite the frozen split:
  `effectbench_omega/outputs/main_mc_postfix_all_local/`.
- Do not overwrite the frozen Stage 3 job:
  `effectbench_omega/jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z/`.
- All new experiment outputs must use new split names.
- Update this runbook, `README.md`, and `results.md` after each stage.
- Operator approved continuing through final Stages 7-11 in one pass after
  Stage 6.

## Stage Status

| Stage | Name | Status | Approval Gate |
|---|---|---:|---|
| 0 | Freeze and preflight | Complete | Approved for Stage 1 |
| 1 | Enumerated frontier completeness audit | Complete, gate failed | Approved to start Stage 2 repair/implementation |
| 2 | Corrected guards V2 implementation | Complete | Approved for Stage 3 |
| 3 | V2 smoke and Qwen repair sensitivity | Complete | Approved for Stage 4 |
| 3.5 | Canonical verifier hardening | Complete | Stage 4 ready |
| 4 | Full corrected-guard local run | Complete | Approved for Stage 5 |
| 5 | Native-fidelity subset | Complete | Approved for Stage 6 |
| 6 | Full replay and targeted CEGAR stress | Complete | Approved for Stage 7 |
| 7 | Lattice policy and paper freeze | Complete | Option B frozen |
| 8 | Claim registry and paper-number audit | Complete | 23 final claim rows |
| 9 | Final reproducibility gate | Complete | All local gates passed |
| 10 | Paper-ready summary | Complete | Writing package ready |
| 11 | Artifact tracking with Git LFS | Complete locally | LFS configured; final push pending/pushed per git status |

## Stage 0: Freeze And Preflight

Completed on 2026-06-24 UTC.

Branch:

```text
eacl-rescue-v2
```

Commands run:

```bash
.venv/bin/python effectbench_omega/scripts/sanity_check.py --local-only
.venv/bin/python effectbench_omega/scripts/verify_local_open_model_cache.py
.venv/bin/python -m pytest -q effectbench_omega/tests/no_oracle
.venv/bin/python effectbench_omega/effectbench/metrics/claim_registry_check.py \
  --registry effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv
.venv/bin/python effectbench_omega/scripts/no_red_placeholders.py \
  --root . \
  --out effectbench_omega/reports/no_red_placeholders.md
```

Results:

| Check | Status | Detail |
|---|---:|---|
| Branch created | Pass | `eacl-rescue-v2` from current `main` |
| Sanity/import check | Pass | Python `3.11.15`; required modules imported; 4 x NVIDIA L40S visible |
| Required local model cache | Pass | Mistral, Qwen3.6-35B-A3B, Llama 3.3 70B AWQ, and Gemma 3 27B IT ready |
| Optional local model cache | Informational | Qwen3-14B-AWQ and Qwen3-30B-A3B cached but not in headline grid |
| Full Llama 3.3 70B precision cache | Informational | Not cached; AWQ substitute remains active |
| No-oracle pytest | Pass | `9 passed, 1 warning` |
| Claim registry check | Pass | 50 rows |
| Placeholder scan | Pass | `effectbench_omega/reports/no_red_placeholders.md` reports PASS |
| Bedrock/API use | Pass | No paid/API runs launched |
| Frozen split modified | Pass | No experiment reruns launched in Stage 0 |

Stage 0 conclusion:

```text
The environment is ready for Stage 1. The frozen current run remains the
baseline evidence package. Next implementation should start with the offline
enumerated-frontier audit only.
```

## Stage 1 Plan: Enumerated Frontier Completeness Audit

Do after operator approval only.

Implementation target:

```text
effectbench_omega/effectbench/kernel/enumerate_frontier.py
effectbench_omega/scripts/run_frontier_completeness.py
```

Important decision:

```text
Do not write enumerated artifacts into the frozen split's existing kernel
directory. Write them into:
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/
```

Required outputs:

```text
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/frontier_enumerated.parquet
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/certificates_enumerated.parquet
effectbench_omega/tables/frontier_completeness_main_mc_postfix_all_local.csv
effectbench_omega/reports/frontier_completeness_main_mc_postfix_all_local.md
```

Acceptance gate:

```text
label_agreement >= 0.995
unexplained_mismatches = 0
```

## Stage 1 Results: Enumerated Frontier Completeness Audit

Completed on 2026-06-24 UTC.

Code added:

```text
effectbench_omega/effectbench/kernel/enumerate_frontier.py
effectbench_omega/scripts/run_frontier_completeness.py
effectbench_omega/tests/test_frontier_enumeration.py
```

Commands run:

```bash
.venv/bin/python -m pytest -q \
  effectbench_omega/tests/test_frontier_enumeration.py \
  effectbench_omega/tests/no_oracle

.venv/bin/python effectbench_omega/scripts/run_frontier_completeness.py \
  --split main_mc_postfix_all_local
```

Outputs:

```text
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/frontier_enumerated.parquet
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/certificates_enumerated.parquet
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/frontier_group_summary.parquet
effectbench_omega/tables/frontier_completeness_main_mc_postfix_all_local.csv
effectbench_omega/reports/frontier_completeness_main_mc_postfix_all_local.md
```

Results:

| Metric | Value |
|---|---:|
| Frontier enumeration tests | `12 passed, 1 warning` |
| Groups audited | 7,168 |
| Observed successful traces relabeled | 21,504 |
| Enumerated admissible candidates | 1,205,248 |
| Nondominated frontier candidates | 7,168 |
| Old strict-excess labels | 5,149 |
| Enumerated strict-excess labels | 4,089 |
| Exact label agreement | 92.9315% |
| Strictness agreement | 95.0707% |
| Strictness disagreements | 1,060 |
| Unexplained mismatches | 0 |
| Gate result | Failed |

Disagreement diagnosis:

| Slice | Count |
|---|---:|
| `observed_trace_witness_not_admissible_under_enumerated_rules` | 1,060 |
| `PROJ_GUARD` old strict-excess now enumerated minimal | 530 |
| `EFFECTGUARD` old strict-excess now enumerated minimal | 530 |
| Qwen affected rows | 824 |
| Gemma affected rows | 224 |
| Llama affected rows | 12 |

Interpretation:

```text
Stage 1 is scientifically useful but does not validate the old generated-trace
verifier labels. The enumerated audit found no unexplained mismatches, but it
also found 1,060 old strict-excess labels whose old witness traces are not
admissible under the enumerated rules. Paper-grade results must use the
enumerated labels or an explicitly repaired verifier, not the old strict-excess
counts alone.
```

Stage 1 conclusion:

```text
Do not treat the frozen split's original strict-excess labels as final paper
labels. Stage 2 should implement corrected V2 guards and align downstream
comparison/metrics with enumerated-frontier certificate semantics.
```

## Stage 2 Plan: Corrected Guards V2 Implementation

Operator approval received via "Ok, next Stge".

Implementation target:

```text
PROJ_GUARD_V2
EFFECTGUARD_V2
```

Stage 2 tasks:

1. Add system names and guard behavior without changing `BASE`, `PROJ_GUARD`, or `EFFECTGUARD`.
2. Make `PROJ_GUARD_V2` projection-only: ask/block for target ambiguity, permission, contract, and explicit irreversible/external projection violations; do not perform global lower-effect substitution.
3. Make `EFFECTGUARD_V2` kernel-aware: substitute lower-effect admissible actions only when justified by current-state admissible alternatives; log substitution, necessary-high, or incomparable reasons.
4. Keep no-oracle sentinels intact.
5. Add unit tests for V2 guard behavior and system routing.
6. Run local tests only. No GPU/model runs in Stage 2 unless a later stage explicitly starts smoke runs.

## Stage 2 Results: Corrected Guards V2 Implementation

Completed on 2026-06-24 UTC.

Code/data added:

```text
effectbench_omega/effectbench/agents/systems.py
effectbench_omega/tests/test_guards_v2.py
effectbench_omega/manifests/tasks_guard_v2_local.csv
```

Commands run:

```bash
.venv/bin/python -m pytest -q \
  effectbench_omega/tests/test_guards_v2.py \
  effectbench_omega/tests/test_frontier_enumeration.py \
  effectbench_omega/tests/no_oracle

.venv/bin/python effectbench_omega/effectbench/families/build_manifest.py \
  --out effectbench_omega/manifests/tasks_guard_v2_local.csv \
  --systems PROJ_GUARD_V2 EFFECTGUARD_V2

.venv/bin/python effectbench_omega/scripts/run_online.py \
  --manifest effectbench_omega/manifests/tasks_guard_v2_local.csv \
  --split guard_v2_dry_smoke \
  --systems PROJ_GUARD_V2 EFFECTGUARD_V2 \
  --models mistral_small_3_2_24b_local \
  --regimes FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT \
  --out effectbench_omega/outputs/guard_v2_dry_smoke \
  --limit 14 \
  --dry-run \
  --model-controls-policy \
  --model-proposal-mode actions \
  --selection-strategy balanced_regime_system

.venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
  --runtime-logs effectbench_omega/outputs/guard_v2_dry_smoke/runtime_logs.parquet \
  --out effectbench_omega/tables/no_oracle_guard_v2_dry_smoke.csv
```

Results:

| Check | Status | Detail |
|---|---:|---|
| V2 guard unit tests | Pass | `17 passed, 1 warning` |
| V2 manifest | Pass | 14,336 rows: 128 tasks x 7 regimes x 2 seeds x 4 models x 2 systems |
| V2 dry online smoke | Pass | 14 traces, 41 ledger rows, 0 failures |
| No-oracle smoke audit | Pass | 14 rows checked, 0 oracle failures, pass rate 1.0 |
| Bedrock/API use | Pass | None |
| GPU/model use | Pass | None; dry local runner only |

Observed dry-smoke behavior:

| System | Representative behavior |
|---|---|
| `PROJ_GUARD_V2` | Passes through `commit_high` when projected predicates accept it; asks on ambiguous-target regimes; blocks external irreversible `ADV_EFFECT` terminal to `commit_high` instead of globally substituting `commit_low`. |
| `EFFECTGUARD_V2` | Uses `draft_change > commit_low` lower-effect suffix when the model/fallback proposes high effect; asks on ambiguous-target regimes; uses `commit_contract_low` for contract preservation. |

Stage 2 conclusion:

```text
Corrected guard systems are implemented and work through the normal online
runner in dry mode. The next stage should run V2 live/local smokes and the Qwen
repair-sensitivity slice without overwriting the frozen split.
```

## Stage 3 Plan: V2 Smoke And Qwen Repair Sensitivity

Operator approval received via "Go".

Stage 3 scope:

1. Run V2 live local smoke for all four locked models with TP=4.
2. Use `PROJ_GUARD_V2` and `EFFECTGUARD_V2` only for V2 smoke rows.
3. Rerun only the affected Qwen rows from the frozen split where
   `model_proposal_repair_log != []`.
4. Keep the Qwen rerun same-prompt/same-settings:
   `model_controls_policy`, `model_proposal_mode=actions`, temperature `0`,
   same logical rows, and original Qwen split trace IDs.
5. Build a merged Qwen sensitivity split and compare proposal/effect/verdict
   deltas against the frozen split.

Implementation added:

```text
effectbench_omega/scripts/run_stage3_v2_smoke_queue.sh
effectbench_omega/scripts/qwen_repair_sensitivity.py
effectbench_omega/manifests/qwen_repair_rows.csv
```

Main command:

```bash
JOB_ID=stage3_v2_smoke_20260624T143808Z \
  bash effectbench_omega/scripts/run_stage3_v2_smoke_queue.sh
```

Job:

```text
effectbench_omega/jobs/stage3_v2_smoke_20260624T143808Z/
effectbench_omega/jobs/stage3_v2_latest -> stage3_v2_smoke_20260624T143808Z
```

V2 smoke results:

| Model | Load wait | Traces | Failures | Parse status | Repair logs | No-oracle | Cost |
|---|---:|---:|---:|---|---:|---:|---:|
| `mistral_small_3_2_24b_local` | 60s | 14 | 0 | `json`: 14 | 0 | 100% | $0 |
| `qwen3_6_35b_a3b_local` | 110s | 14 | 0 | `json`: 14 | 0 | 100% | $0 |
| `llama3_3_70b_awq_local` | 90s | 14 | 0 | `json`: 14 | 0 | 100% | $0 |
| `gemma3_27b_it_local` | 130s | 14 | 0 | `json`: 14 | 0 | 100% | $0 |

All four smoke runs used `CUDA_VISIBLE_DEVICES=0,1,2,3` and TP=4. GPU samples
showed full-model residency across all four cards, and active generation
samples reached ~98-100% utilization.

Qwen repair sensitivity:

| Metric | Value |
|---|---:|
| Affected Qwen rows rerun | 168 |
| Original non-empty repair-log rows | 168 |
| Original repair-fallback rows | 42 |
| Rerun non-empty repair-log rows | 168 |
| Rerun repair-fallback rows | 42 |
| Proposal changed rows | 0 |
| Effect-vector changed rows | 0 |
| Verifier verdict changed rows | 0 |
| Overall strict-rate delta | 0.000000 pp |
| Qwen strict-rate delta | 0.000000 pp |
| Qwen rerun failures | 0 |
| Qwen rerun no-oracle pass rate | 100% |
| Qwen rerun local cost | $0 |

Qwen sensitivity outputs:

```text
effectbench_omega/outputs/qwen_repair_sensitivity_rerun/
effectbench_omega/outputs/qwen_repair_sensitivity_merged/
effectbench_omega/tables/qwen_repair_sensitivity.csv
effectbench_omega/reports/qwen_repair_sensitivity.md
```

Stage 3 conclusion:

```text
Corrected V2 systems are live-call smoke-clean for all four locked local
models. Qwen repaired rows are stable under same-prompt rerun: the rerun exactly
reproduced the prior proposal/effect/verdict behavior and changed no headline
strict-rate metric. The Qwen parse-status caveat remains an audit disclosure
because the same 42 repair-fallback parses reproduced, but it is not a
volatility/headline-sensitivity issue in this rerun.
```

Next stage:

```text
Stage 4 should run the full corrected-guard local split:
128 tasks x 7 regimes x 2 seeds x 4 models x 2 V2 systems = 14,336
trajectories. Reuse the frozen BASE split; do not rerun BASE unless a code bug
requires it.
```

## Stage 3.5: Canonical Verifier Hardening

Completed on 2026-06-24 UTC.

Purpose:

```text
Resolve the Stage 1 caveat by making enumerated admissible-frontier
certificates the canonical source for paper strict-excess labels. The old
generated-trace verifier is retained only as a legacy diagnostic.
```

Code changes:

```text
effectbench_omega/effectbench/kernel/enumerate_frontier.py
effectbench_omega/effectbench/audit/replay_bundles.py
effectbench_omega/effectbench/audit/replay_certificates.py
effectbench_omega/effectbench/audit/cegar.py
effectbench_omega/effectbench/audit/guard_tie.py
effectbench_omega/effectbench/metrics/bootstrap.py
effectbench_omega/effectbench/metrics/aggregate.py
effectbench_omega/scripts/run_stage3_offline.sh
effectbench_omega/scripts/run_local_open_queue.sh
effectbench_omega/scripts/build_guard_v2_main_split.py
```

Canonical rule:

```text
Paper strict-excess labels must come from:
effectbench_omega/outputs/<split>/kernel_canonical/certificates_enumerated.parquet

Legacy generated-trace labels may be reported only as an audit/diagnostic.
```

Commands run:

```bash
bash -n effectbench_omega/scripts/run_stage3_offline.sh
bash -n effectbench_omega/scripts/run_local_open_queue.sh
.venv/bin/python -m py_compile \
  effectbench_omega/effectbench/kernel/enumerate_frontier.py \
  effectbench_omega/effectbench/audit/replay_bundles.py \
  effectbench_omega/effectbench/audit/replay_certificates.py \
  effectbench_omega/effectbench/audit/cegar.py \
  effectbench_omega/effectbench/audit/guard_tie.py \
  effectbench_omega/effectbench/metrics/bootstrap.py \
  effectbench_omega/effectbench/metrics/aggregate.py \
  effectbench_omega/scripts/build_guard_v2_main_split.py
.venv/bin/python -m pytest -q \
  effectbench_omega/tests/test_frontier_enumeration.py \
  effectbench_omega/tests/test_guards_v2.py \
  effectbench_omega/tests/no_oracle

JOB_ID=stage3_canonical_main_mc_postfix_all_local_20260624T162051Z \
TABLE_SUFFIX=main_mc_postfix_all_local_canonical \
CANONICAL_CERT_MODE=enumerated \
  bash effectbench_omega/scripts/run_stage3_offline.sh
```

## Stage 5: Native-Fidelity Subset

Operator approval received via "Proceed to Stage 5."

Stage 5 target:

```text
split: native_subset_v1_all_local
denominator: 48 native tasks x 4 regimes x 2 seeds x 4 models x 3 systems = 4,608 trajectories
families: tau_retail_native, tau_airline_native, tau2_telecom_native, toolsandbox_contract_native
regimes: FULL, SHARDED, MEMORY_REVISE, ADV_EFFECT
systems: BASE, PROJ_GUARD_V2, EFFECTGUARD_V2
local cost: $0
```

Implementation completed before live model launch:

```text
native package: effectbench_omega/effectbench/native/
manifest builder: effectbench_omega/effectbench/families/build_native_subset_manifest.py
online hook: native rows replay the selected actions through the native state machine
trace audit fields: native state hashes, native success reason, native replay status, and state-delta ledger
certificate replay: native bundles re-execute model traces and enumerated witness candidates in the same wrapper
```

Native minimum-requirement status:

| Requirement | Status | Artifact |
|---|---:|---|
| Pinned upstream records loaded | Pass | `source_native_id`, `source_path`, `source_hash`, `source_commit` in `effectbench_omega/manifests/tasks_native_subset.csv` |
| Terminal success from native predicate | Pass | `native_success_reason` in Stage 5 traces |
| Effect ledger from state deltas | Pass | `native_state_delta_ledger` and per-step `tool_ledgers.parquet` |
| Terminal failures possible/counted | Pass | dry run recorded native failures |
| Witness replay in same wrapper | Pass | `effectbench_omega/effectbench/audit/replay_certificates.py` replays native traces/candidates |

Commands run:

```bash
.venv/bin/python -m py_compile \
  effectbench_omega/effectbench/native/*.py \
  effectbench_omega/effectbench/families/build_native_subset_manifest.py \
  effectbench_omega/effectbench/agents/systems.py \
  effectbench_omega/scripts/run_online.py \
  effectbench_omega/effectbench/audit/replay_certificates.py

.venv/bin/python effectbench_omega/effectbench/families/build_native_subset_manifest.py \
  --out effectbench_omega/manifests/tasks_native_subset.csv \
  --tau-retail 16 \
  --tau-airline 16 \
  --telecom 8 \
  --toolsandbox-contract 8 \
  --regimes FULL SHARDED MEMORY_REVISE ADV_EFFECT \
  --seeds 13 47 \
  --models mistral_small_3_2_24b_local qwen3_6_35b_a3b_local gemma3_27b_it_local llama3_3_70b_awq_local \
  --systems BASE PROJ_GUARD_V2 EFFECTGUARD_V2
```

Manifest check:

| Field | Count |
|---|---:|
| Total rows | 4,608 |
| `tau_retail_native` rows | 1,536 |
| `tau_airline_native` rows | 1,536 |
| `tau2_telecom_native` rows | 768 |
| `toolsandbox_contract_native` rows | 768 |
| Rows with `native_execution=True` | 4,608 |

Dry smokes completed before live model launch:

| Check | Status | Detail |
|---|---:|---|
| 48-row balanced native smoke | Pass | 48 traces, 0 runner failures |
| 48-row verifier | Pass | 36 certificates, 12 strict-excess, 0 warnings |
| 48-row canonical frontier | Pass | canonical gate true, unexplained mismatches 0 |
| 48-row native replay | Pass | 15 bundles checked, 15 native replays, 0 failures |
| Full 4,608-row dry native pass | Pass | 4,608 traces, 0 runner failures |
| Full dry verifier | Pass | 3,408 certificates, 720 strict-excess, 0 warnings |
| Full dry canonical frontier | Pass | canonical gate true, 720 canonical strict-excess, unexplained mismatches 0 |
| Full dry native replay | Pass | 35 bundles checked, 35 native replays, 0 failures |

Full dry native raw-success shape:

| Family | BASE | PROJ_GUARD_V2 | EFFECTGUARD_V2 |
|---|---:|---:|---:|
| `tau_retail_native` | 50.0000% | 78.1250% | 100.0000% |
| `tau_airline_native` | 50.0000% | 75.0000% | 100.0000% |
| `tau2_telecom_native` | 50.0000% | 75.0000% | 100.0000% |
| `toolsandbox_contract_native` | 0.0000% | 100.0000% | 100.0000% |

Interpretation:

```text
The native dry suite exercises real failure paths rather than the old
all-success scaffold. It is still a compact native-style wrapper over pinned
upstream task records, not a full upstream server re-host. Paper language
should call it a native-fidelity subset/validation block, not a replacement for
the controlled source-backed headline suite.
```

Live Stage 5 queue command:

```bash
cd /home/ubuntu/nachiket/CommitBench
JOB_ID=local_open_native_subset_v1_$(date -u +%Y%m%dT%H%M%SZ) \
OUTPUT_PREFIX=native_subset_v1 \
SPLIT_PREFIX=native_subset_v1 \
REPORT_PREFIX=native_subset_v1 \
MANIFEST=effectbench_omega/manifests/tasks_native_subset.csv \
QUEUE_SYSTEMS="BASE PROJ_GUARD_V2 EFFECTGUARD_V2" \
QUEUE_REGIMES="FULL SHARDED MEMORY_REVISE ADV_EFFECT" \
SLICE_LIMIT=1152 \
MODEL_CONTROLS_POLICY=1 \
MODEL_PROPOSAL_MODE=actions \
ROW_SELECTION_STRATEGY=first \
QUEUE_MODELS="mistral_small_3_2_24b_local qwen3_6_35b_a3b_local gemma3_27b_it_local llama3_3_70b_awq_local" \
QUEUE_MODEL_TP=4 \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
  bash effectbench_omega/scripts/run_local_open_queue.sh
```

Live Stage 5 queue status:

```text
job_id: local_open_native_subset_v1_20260625T085816Z
latest_symlink: effectbench_omega/jobs/local_open_latest
launched: 2026-06-25T08:58:16Z
first_model: mistral_small_3_2_24b_local
server_ready: 2026-06-25T08:59:34Z
first running_slice: 2026-06-25T08:59:43Z
queue_done: 2026-06-25T12:55:39Z
stable GPU sample during run: all four GPUs at 100% utilization, about 42 GB used each
```

Final Stage 5 queue result:

| Model | Trace count | Native successes | Failures | Legacy strict-excess | Legacy minimal | Notes |
|---|---:|---:|---:|---:|---:|---|
| `mistral_small_3_2_24b_local` | 1,152 | 1,152 | 0 | 273 | 879 | completed 2026-06-25T09:32:01Z |
| `qwen3_6_35b_a3b_local` | 1,152 | 822 | 0 | 22 | 800 | completed 2026-06-25T09:41:07Z |
| `gemma3_27b_it_local` | 1,152 | 1,091 | 0 | 243 | 848 | completed 2026-06-25T10:14:38Z |
| `llama3_3_70b_awq_local` | 1,152 | 1,152 | 0 | 310 | 842 | completed 2026-06-25T12:55:34Z |

Stage 5 merge:

```text
merged output: effectbench_omega/outputs/native_subset_v1_all_local/
merged traces: 4,608
merged api log rows: 4,608
failure lines: 0
```

Stage 5 canonical scoring:

```text
job_id: stage5_canonical_native_subset_v1_20260625T191826Z
canonical certificates: effectbench_omega/outputs/native_subset_v1_all_local/kernel_canonical/certificates_enumerated.parquet
canonical gate: pass
observed native successes: 4,217
native terminal failures: 391
enumerated strict-excess labels: 848
legacy strict-excess labels: 848
spurious legacy witnesses: 0
unexplained mismatches: 0
replay bundles checked: 160
native replays checked: 160
replay failures: 0
no-oracle pass rate: 100%
local cost: $0
```

Final Stage 5 raw success and canonical strict-excess:

| System | Raw success | Native successes | Canonical strict-excess among successes | Kernel success among successes |
|---|---:|---:|---:|---:|
| `BASE` | 81.5755% | 1,253 / 1,536 | 67.6776% | 32.3224% |
| `PROJ_GUARD_V2` | 92.9688% | 1,428 / 1,536 | 0.0000% | 100.0000% |
| `EFFECTGUARD_V2` | 100.0000% | 1,536 / 1,536 | 0.0000% | 100.0000% |

Final interpretation:

```text
Stage 5 is complete. The native-fidelity subset fixes the old all-success
scaffold caveat for a validation block: terminal failures are possible and
counted, state-delta ledgers drive effects, and native replay passes. The
subset remains a compact native-style wrapper over pinned upstream records, not
a full upstream benchmark server re-host.
```

## Stage 6: Full Replay And Targeted CEGAR Stress

Operator approval received via "Do Stage 6 now."

Implementation updates:

```text
effectbench_omega/effectbench/audit/replay_bundles.py now supports
strict_excess=all plus explicit minimal/incomparable/necessary-high selectors.

effectbench_omega/effectbench/audit/cegar.py now supports
--inject-targeted-cases and --stress-targets for deterministic CEGAR stress
pairs.
```

Smoke checks:

```text
py_compile: pass
targeted CEGAR smoke: pass; all seven fields had label-changing collisions
replay smoke: 4 native bundles checked, 4 native replays, 0 failures
no-oracle pytest: 9 passed, 1 warning
```

Full replay commands:

```bash
.venv/bin/python effectbench_omega/effectbench/audit/replay_bundles.py \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel_canonical/certificates_enumerated.parquet \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --sample strict_excess=all minimal=500 incomparable=all necessary_high=all \
  --out effectbench_omega/witness_bundles/full_replay_main_mc_postfix_all_local_canonical

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_main_mc_postfix_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_full_main_mc_postfix_all_local_canonical.md \
  --strict

.venv/bin/python effectbench_omega/effectbench/audit/replay_bundles.py \
  --certificates effectbench_omega/outputs/guard_v2_main_with_base_all_local/kernel_canonical/certificates_enumerated.parquet \
  --traces effectbench_omega/outputs/guard_v2_main_with_base_all_local/traces.parquet \
  --sample strict_excess=all minimal=500 incomparable=all necessary_high=all \
  --out effectbench_omega/witness_bundles/full_replay_guard_v2_main_with_base_all_local_canonical

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_guard_v2_main_with_base_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_full_guard_v2_main_with_base_all_local_canonical.md \
  --strict

.venv/bin/python effectbench_omega/effectbench/audit/replay_bundles.py \
  --certificates effectbench_omega/outputs/native_subset_v1_all_local/kernel_canonical/certificates_enumerated.parquet \
  --traces effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet \
  --sample strict_excess=all minimal=500 incomparable=all necessary_high=all \
  --out effectbench_omega/witness_bundles/full_replay_native_subset_v1_all_local_canonical

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_native_subset_v1_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_full_native_subset_v1_all_local_canonical.md \
  --strict
```

Full replay results:

| Split | Bundles checked | Native replays | Failures |
|---|---:|---:|---:|
| `main_mc_postfix_all_local_canonical` | 4,819 | 0 | 0 |
| `guard_v2_main_with_base_all_local_canonical` | 5,341 | 0 | 0 |
| `native_subset_v1_all_local_canonical` | 1,348 | 1,348 | 0 |
| **Total** | **11,508** | **1,348** | **0** |

Generated full replay bundle directories:

```text
effectbench_omega/witness_bundles/full_replay_main_mc_postfix_all_local_canonical/ (41M)
effectbench_omega/witness_bundles/full_replay_guard_v2_main_with_base_all_local_canonical/ (46M)
effectbench_omega/witness_bundles/full_replay_native_subset_v1_all_local_canonical/ (15M)
```

Note: these full JSON bundle directories are generated artifacts and are not
tracked in git. The replay reports and summary tables are tracked.

Targeted CEGAR stress command:

```bash
.venv/bin/python effectbench_omega/effectbench/audit/cegar.py \
  --traces effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet \
  --certificates effectbench_omega/outputs/native_subset_v1_all_local/kernel_canonical/certificates_enumerated.parquet \
  --schemas effectbench_omega/schemas \
  --omit-fields outbox policy_obligation contract_artifact_hash virtual_clock memory_cache user_visible_exposure compensation_or_payment_hold \
  --inject-targeted-cases \
  --stress-targets outbox policy_obligation contract_artifact_hash virtual_clock memory_cache user_visible_exposure compensation_or_payment_hold \
  --out effectbench_omega/tables/cegar_rejections_stage6_targeted_stress.csv \
  --label-changes effectbench_omega/tables/cegar_label_changes_stage6_targeted_stress.csv
```

Targeted CEGAR stress results:

| Omitted field | Label-change groups | Rejected abstractions | Affected rows |
|---|---:|---:|---:|
| `outbox` | 29 | 29 | 834 |
| `policy_obligation` | 1 | 1 | 2 |
| `contract_artifact_hash` | 1 | 1 | 2 |
| `virtual_clock` | 1 | 1 | 2 |
| `memory_cache` | 103 | 103 | 2,682 |
| `user_visible_exposure` | 83 | 83 | 3,822 |
| `compensation_or_payment_hold` | 1 | 1 | 2 |

Interpretation:

```text
Stage 6 completes the full replay/CEGAR repair step. All full replay bundles
pass, including all native strict-excess bundles. Targeted stress rows now
exercise every future-relevant CEGAR field, including fields that were quiet in
the ordinary scaffold. The correct paper framing is that earlier no-collision
fields were not exercised there; Stage 6 demonstrates they are relevant under
targeted counterexamples.
```

## Stage 7: Lattice Policy And Paper Freeze

Operator approved the recommended path after Stage 6.

Decision:

```text
Use the fixed declared Pareto lattice for main claims.
Move lattice sensitivity to appendix/diagnostic only.
Do not claim robustness across alternate value-governance lattices from the
current invariant sensitivity tables.
```

Result:

| Split | Variants | Unique strict-excess rates | Paper treatment |
|---|---:|---:|---|
| `main_mc_postfix_all_local_canonical` | 6 | 1 | Appendix/diagnostic only |
| `guard_v2_main_with_base_all_local_canonical` | 6 | 1 | Appendix/diagnostic only |
| `native_subset_v1_all_local_canonical` | 6 | 1 | Appendix/diagnostic only |

Artifact:

```text
effectbench_omega/reports/stage7_lattice_policy_freeze.md
```

## Stage 8: Claim Registry And Paper-Number Audit

Final claim registry:

```text
effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv
```

Result:

| Metric | Value |
|---|---:|
| Final registry rows | 23 |
| Main allowed claims | 11 |
| Validation claims | 5 |
| Audit/caveat/reproducibility rows | 6 |
| Archived-only rows | 1 |

Audit rules:

```text
canonical enumerated-frontier labels only for strict-excess claims
legacy generated-trace labels archived only
no Bedrock/frontier/commercial leaderboard claims
native subset reported separately
lattice sensitivity appendix/diagnostic only
no human-eval claim
```

Artifacts:

```text
effectbench_omega/reports/stage8_claim_audit.md
effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv
```

## Stage 9: Final Reproducibility Gate

Commands/checks run:

```bash
.venv/bin/python -m py_compile effectbench_omega/scripts/finalize_eacl_rescue.py
.venv/bin/python -m pytest -q effectbench_omega/tests/no_oracle
.venv/bin/python effectbench_omega/effectbench/metrics/claim_registry_check.py \
  --registry effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv
.venv/bin/python effectbench_omega/scripts/no_red_placeholders.py \
  --root . \
  --out effectbench_omega/reports/no_red_placeholders.md
.venv/bin/python effectbench_omega/scripts/reproduce.py --check-only
.venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
  --logs effectbench_omega/outputs/main_mc_postfix_all_local/api_logs.jsonl \
         effectbench_omega/outputs/guard_v2_main_with_base_all_local/api_logs.jsonl \
         effectbench_omega/outputs/native_subset_v1_all_local/api_logs.jsonl \
  --final \
  --out effectbench_omega/reports/final_cost_audit.json
```

Replay checks:

```bash
.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_main_mc_postfix_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_final_main_mc_postfix_all_local_canonical.md \
  --strict

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_guard_v2_main_with_base_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_final_guard_v2_main_with_base_all_local_canonical.md \
  --strict

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/full_replay_native_subset_v1_all_local_canonical \
  --out effectbench_omega/reports/certificate_replay_final_native_subset_v1_all_local_canonical.md \
  --strict
```

Results:

| Gate | Result | Detail |
|---|---:|---|
| No-oracle tests | Pass | `9 passed, 1 warning` |
| Claim registry check | Pass | 23 rows |
| Placeholder scan | Pass | PASS |
| Check-only reproducer | Pass | Missing required files: none; local endpoint stopped as expected |
| Cost audit | Pass | 47,616 local request rows, `$0`, 0 unpriced Bedrock rows |
| Main controlled replay | Pass | 4,819 bundles, 0 failures |
| Corrected-guard replay | Pass | 5,341 bundles, 0 failures |
| Native replay | Pass | 1,348 bundles, 1,348 native replays, 0 failures |

Artifact:

```text
effectbench_omega/reports/final_reproducibility_gate.md
```

## Stage 10: Paper-Ready Summary

Paper posture:

```text
EffectBench-Omega is a local/open-weight certificate-semantics paper.
The central claim is that final-state success overstates certified
least-effect success and that enumerated Effect Kernel certificates make this
auditable.
```

Artifact:

```text
effectbench_omega/reports/eacl_rescue_paper_ready_summary.md
```

## Stage 11: Artifact Tracking With Git LFS

Git LFS patterns configured:

```text
*.parquet
*.jsonl
*.log
*.png
*.pdf
*.pptx
*.zip
effectbench_omega/outputs/**
effectbench_omega/jobs/**
effectbench_omega/witness_bundles/**
```

Tracked artifact policy:

```text
Track generated outputs, response logs, job logs, figures, reports, metrics,
tables, manifests, and witness bundles.
Keep .env files, local model caches, upstream clones, and virtualenvs out of
git.
```

Artifact manifest:

| Metric | Value |
|---|---:|
| Files indexed | 13,836 |
| Bytes indexed | 416,877,747 |

Artifacts:

```text
effectbench_omega/tables/artifact_manifest.csv
effectbench_omega/reports/artifact_manifest.md
```

Monitor:

```bash
cd /home/ubuntu/nachiket/CommitBench
tail -f effectbench_omega/jobs/local_open_latest/events.tsv
bash effectbench_omega/scripts/show_local_open_queue_status.sh
nvidia-smi dmon -s pucm -d 5
```

After the live queue completes:

```bash
cd /home/ubuntu/nachiket/CommitBench
.venv/bin/python effectbench_omega/scripts/merge_local_open_slices.py \
  --input-prefix effectbench_omega/outputs/native_subset_v1 \
  --out effectbench_omega/outputs/native_subset_v1_all_local \
  --expected-rows-per-model 1152

JOB_ID=stage5_canonical_native_subset_v1_$(date -u +%Y%m%dT%H%M%SZ) \
SPLIT=native_subset_v1_all_local \
TABLE_SUFFIX=native_subset_v1_all_local_canonical \
GUARD_TIE_SYSTEMS="PROJ_GUARD_V2 EFFECTGUARD_V2" \
BOOTSTRAP_SYSTEMS="BASE PROJ_GUARD_V2 EFFECTGUARD_V2" \
CANONICAL_CERT_MODE=enumerated \
  bash effectbench_omega/scripts/run_stage3_offline.sh
```

Canonical output:

```text
effectbench_omega/outputs/main_mc_postfix_all_local/kernel_legacy_generated_trace/
effectbench_omega/outputs/main_mc_postfix_all_local/kernel_canonical/
effectbench_omega/jobs/stage3_canonical_main_mc_postfix_all_local_20260624T162051Z/
effectbench_omega/tables/main_mc_postfix_all_local_canonical/
effectbench_omega/figures/main_mc_postfix_all_local_canonical/
effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local_canonical.csv
```

Results:

| Metric | Value |
|---|---:|
| Tests | `18 passed, 1 warning` |
| Canonical gate | Pass |
| Groups | 7,168 |
| Successful traces scored | 21,504 |
| Enumerated candidates | 1,205,248 |
| Frontier candidates | 7,168 |
| Legacy strict-excess labels | 5,149 |
| Canonical strict-excess labels | 4,089 |
| Spurious legacy witnesses | 1,060 |
| Enumerated new strict labels | 0 |
| Unexplained mismatches | 0 |
| Replay bundles checked | 160 |
| Replay failures | 0 |

Canonical online-control results for the frozen split:

| System | Raw success | Canonical strict excess | Canonical kernel success |
|---|---:|---:|---:|
| `BASE` | 100.0000% | 57.0033% | 42.9967% |
| `PROJ_GUARD` | 100.0000% | 0.0419% | 99.9581% |
| `EFFECTGUARD` | 100.0000% | 0.0000% | 100.0000% |

Interpretation:

```text
The Stage 1 caveat is fixed operationally: old generated-trace witnesses are
not used for paper labels. The 1,060 disagreements are now recorded as
spurious legacy witnesses. Canonical scoring requires zero unexplained
mismatches, not agreement with the legacy verifier.
```

## Stage 4 Ready Commands

Operator approval received via "Ok, so now launch Stage 4 and lemme know how
to monitor, once stable."

Live job:

```text
job_id: local_open_guard_v2_main_20260624T200115Z
latest_symlink: effectbench_omega/jobs/local_open_latest
current_model: mistral_small_3_2_24b_local
current_status: running_slice
current_detail: writing 3584 trajectories to effectbench_omega/outputs/guard_v2_main_mistral_small_3_2_24b_local
```

Stable-start check:

```text
Mistral reached server_ready at 2026-06-24T20:02:32Z.
The Stage 4 slice started at 2026-06-24T20:02:41Z.
TP=4 on CUDA_VISIBLE_DEVICES=0,1,2,3.
GPU sample after slice start showed 100% utilization on all four GPUs.
```

Final Stage 4 queue result:

| Model | Trace count | Failures | Legacy strict-excess | Legacy minimal | Notes |
|---|---:|---:|---:|---:|---|
| `mistral_small_3_2_24b_local` | 3,584 | 0 | 61 | 3,523 | completed 2026-06-24T21:37:49Z |
| `qwen3_6_35b_a3b_local` | 3,584 | 0 | 456 | 3,128 | completed 2026-06-24T22:03:56Z |
| `llama3_3_70b_awq_local` | 3,584 | 0 | 6 | 3,578 | completed 2026-06-25T06:14:03Z |
| `gemma3_27b_it_local` | 3,584 | 0 | 2 | 3,582 | completed 2026-06-25T07:56:59Z |

Stage 4 merge/combine:

```text
V2 guard merged output: effectbench_omega/outputs/guard_v2_main_all_local/
V2 guard traces: 14,336
V2 failure lines: 0
Combined BASE+V2 output: effectbench_omega/outputs/guard_v2_main_with_base_all_local/
Combined traces: 21,504
Combined systems: BASE, PROJ_GUARD_V2, EFFECTGUARD_V2
```

Stage 4 canonical scoring:

```text
job_id: stage3_canonical_guard_v2_main_with_base_20260625T082959Z
canonical certificates: effectbench_omega/outputs/guard_v2_main_with_base_all_local/kernel_canonical/certificates_enumerated.parquet
canonical gate: pass
enumerated strict-excess labels: 4,611
legacy strict-excess labels: 5,621
spurious legacy witnesses: 1,010
unexplained mismatches: 0
replay bundles checked: 160
replay failures: 0
local cost: $0
```

Canonical online-control result:

| System | Trajectories | Raw success | Canonical strict excess | Canonical kernel success |
|---|---:|---:|---:|---:|
| `BASE` | 7,168 | 100.0000% | 57.0033% | 42.9967% |
| `PROJ_GUARD_V2` | 7,168 | 100.0000% | 7.3242% | 92.6758% |
| `EFFECTGUARD_V2` | 7,168 | 100.0000% | 0.0000% | 100.0000% |

Interpretation:

```text
Stage 4 fixed the old PROJ_GUARD/EFFECTGUARD near-tie for the corrected V2
comparison. PROJ_GUARD_V2 remains a projection-only baseline with nonzero
canonical residual strict-excess, while EFFECTGUARD_V2 reaches zero canonical
strict-excess in this controlled local scaffold without raw-success loss.
```

Run the full V2 guard-only queue:

```bash
cd /home/ubuntu/nachiket/CommitBench
JOB_ID=local_open_guard_v2_main_20260624T200115Z \
OUTPUT_PREFIX=guard_v2_main \
SPLIT_PREFIX=guard_v2_main \
REPORT_PREFIX=guard_v2_main \
MANIFEST=effectbench_omega/manifests/tasks_guard_v2_local.csv \
QUEUE_SYSTEMS="PROJ_GUARD_V2 EFFECTGUARD_V2" \
SLICE_LIMIT=3584 \
MODEL_CONTROLS_POLICY=1 \
MODEL_PROPOSAL_MODE=actions \
QUEUE_MODEL_TP=4 \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
  bash effectbench_omega/scripts/run_local_open_queue.sh
```

Launch note:

```text
The queue was launched detached with setsid so it survives outside the Codex
tool session:
setsid bash -lc '<exports>; exec bash effectbench_omega/scripts/run_local_open_queue.sh' > effectbench_omega/jobs/local_open_guard_v2_main_20260624T200115Z_launch.log 2>&1 < /dev/null &
```

Monitor:

```bash
cd /home/ubuntu/nachiket/CommitBench
tail -f effectbench_omega/jobs/local_open_latest/events.tsv
bash effectbench_omega/scripts/show_local_open_queue_status.sh
nvidia-smi dmon -s pucm -d 5
```

After all four model slices complete:

```bash
cd /home/ubuntu/nachiket/CommitBench
.venv/bin/python effectbench_omega/scripts/merge_local_open_slices.py \
  --input-prefix effectbench_omega/outputs/guard_v2_main \
  --out effectbench_omega/outputs/guard_v2_main_all_local \
  --expected-rows-per-model 3584

.venv/bin/python effectbench_omega/scripts/build_guard_v2_main_split.py \
  --v2-split effectbench_omega/outputs/guard_v2_main_all_local \
  --out effectbench_omega/outputs/guard_v2_main_with_base_all_local

JOB_ID=stage3_canonical_guard_v2_main_with_base_$(date -u +%Y%m%dT%H%M%SZ) \
SPLIT=guard_v2_main_with_base_all_local \
TABLE_SUFFIX=guard_v2_main_with_base_all_local_canonical \
GUARD_TIE_SYSTEMS="PROJ_GUARD_V2 EFFECTGUARD_V2" \
BOOTSTRAP_SYSTEMS="BASE PROJ_GUARD_V2 EFFECTGUARD_V2" \
CANONICAL_CERT_MODE=enumerated \
  bash effectbench_omega/scripts/run_stage3_offline.sh
```
