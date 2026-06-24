# EffectBench-Omega EACL Rescue V2 Runbook

Last updated: 2026-06-24 UTC

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
- Stop after each stage and wait for operator approval before moving on.

## Stage Status

| Stage | Name | Status | Approval Gate |
|---|---|---:|---|
| 0 | Freeze and preflight | Complete | Approved for Stage 1 |
| 1 | Enumerated frontier completeness audit | Complete, gate failed | Approved to start Stage 2 repair/implementation |
| 2 | Corrected guards V2 implementation | Complete | Approved for Stage 3 |
| 3 | V2 smoke and Qwen repair sensitivity | Complete | Awaiting approval for Stage 4 |
| 4 | Full corrected-guard local run | Pending | Requires Stage 3 approval |
| 5 | Native-fidelity subset | Pending | Requires Stage 4 approval |
| 6 | Full replay and targeted CEGAR stress | Pending | Requires Stage 5 approval |
| 7 | Lattice policy and paper freeze | Pending | Requires Stage 6 approval |

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
