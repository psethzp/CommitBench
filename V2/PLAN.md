# EffectBench-Omega EACL Rescue Plan (Local-Only)

Last updated: 2026-06-24

2026-06-26 rebuttal addendum: Rebuttal Stage 1 claim reset and Stage 2
shared-proposal audit are complete. Future proposal prompts omit `system=...`
from user content. The shared-proposal audit replays `BASE`, `PROJ_GUARD_V2`,
and `EFFECTGUARD_V2` from identical frozen `BASE` proposals for every
task/model/regime/seed; it is CPU-only, uses 0 new model calls, passes the
canonical enumerated-frontier gate with 0 unexplained mismatches, and reports
canonical strict-excess rates BASE 57.0033%, PROJ_GUARD_V2 9.1657%,
EFFECTGUARD_V2 0.0000%. Caveat: the frozen BASE proposals came from the
legacy prompt that included `system=BASE`, so this audit removes
between-system proposal confounding but is not a fresh no-system-prompt rerun.

2026-06-26 final rebuttal addendum: Rebuttal Stage 3 stress, Stage 4
leave-one robustness, and Stage 6 final freeze addendum are complete. Stage 3
adds 3,072 necessary-high/incomparable stress trajectories with 0 failures, 0
unexplained mismatches, 704 EffectGuard necessary-high decisions, and 320
EffectGuard incomparable decisions. Stage 4 adds 39 leave-one gate rows with 0
base-gap failures, 0 required projection-residual failures, and 0
EffectGuard-zero failures. Stage 6 light gates pass with 18 tests, claim
registry check, placeholder scan, and no active GPU jobs.

## Decision

Do **not** submit the current 21,504-row run as the final EACL main-paper evidence package.

The current run is valuable and should be kept, but it is currently best described as a **source-backed deterministic adapter study**, not a fully native benchmark evaluation. The main scientific contribution should be reframed as the **Effect Kernel semantics + verifier + certificates**, with EffectGuard as a secondary reference controller.

There is no guaranteed EACL acceptance. The goal of this plan is to convert the current evidence into a much stronger ARR/EACL submission by fixing the issues reviewers are most likely to attack.

## Current Run Summary

Active split: `effectbench_omega/outputs/main_mc_postfix_all_local/`

Current denominator:

```text
128 tasks × 7 regimes × 2 seeds × 4 local models × 3 systems = 21,504 trajectories
```

Models already run:

- `mistral_small_3_2_24b_local`
- `qwen3_6_35b_a3b_local`
- `gemma3_27b_it_local`
- `llama3_3_70b_awq_local`

Strong current results:

- 21,504 trajectories, 0 online failures.
- 21,504 certificates, 0 unresolved abstraction warnings.
- BASE strict-excess rate: 57.0033%.
- BASE kernel least-effect success: 42.9967%.
- PROJ_GUARD strict-excess rate: 7.4358%.
- EFFECTGUARD strict-excess rate: 7.3940%.
- No-oracle checks pass 100%.
- 160 replay bundles checked with 0 failures.
- Local cost: $0.
- Canonical enumerated-frontier scoring now passes with 4,089 strict-excess
  labels, 1,060 spurious legacy witnesses diagnosed, and 0 unexplained
  mismatches.

Critical current weaknesses:

- Raw success is 100% for every system, so the run does not demonstrate realistic task-completion difficulty.
- The original generated-trace verifier compared only executed/generated traces. This is now archived as a legacy diagnostic; paper labels must use canonical enumerated admissible-frontier certificates.
- `PROJ_GUARD` and `EFFECTGUARD` are essentially tied: only 3/7,168 paired guarded units differ in verifier verdict.
- Projection baselines are simple local filters, not faithful reimplementations of CORE/MiniScope/ContractGuard/etc.; therefore they must be called projection baselines, not SOTA systems.
- `CORE_DFA` currently accepts all traces and is identical to `FINAL_STATE`; this is useful only as a weak projection, not a serious full-path baseline.
- Lattice sensitivity is degenerate: every lattice variant reports the exact same strict-excess rate. Either fix the sensitivity logic or move it to a very small appendix with an explanation.
- CEGAR omission tests for `policy_obligation`, `contract_artifact_hash`, `virtual_clock`, and `compensation_or_payment_hold` currently show no label-changing collisions; targeted stress cases are needed.
- Qwen has 42 repaired-fallback proposals and 168 non-empty repair logs; this needs a sensitivity rerun or a caveat.

## Submission Claim After Rescue

Target claim:

> We introduce Effect Kernels: a task-relative certificate semantics for tool-agent traces that upgrades final-state success into certified least-effect success. On reproducible open-weight agents, final-state success substantially overstates least-effect success; projected safeguards reduce but do not eliminate residual strict-excess; a no-oracle effect-aware controller reduces excess under a corrected projection-only baseline.

Forbidden claims:

- Frontier/commercial model leaderboard.
- GPT/Claude/Gemini/Bedrock coverage.
- Direct SOTA superiority over CORE/MiniScope/ContractGuard unless faithful native baselines are actually implemented.
- Strong EffectGuard superiority over the current `PROJ_GUARD`; current data shows a tie.
- Universal abstraction-field irrelevance from CEGAR no-collision rows.
- Human-audit claims.

## Rescue Experiments

### R0. Freeze Current Run

Keep the current split unchanged:

```text
effectbench_omega/outputs/main_mc_postfix_all_local/
```

Do not silently overwrite it. Use it as:

- Controlled local adapter study.
- Ablation showing strong projection guards can nearly match EffectGuard in this scaffold.
- Evidence for raw-vs-kernel gap and replayable certificate mechanics.

### R1. Frontier-Completeness Audit (Highest ROI)

Problem: the current verifier compares only executed/generated traces. For the paper’s semantic claim, labels should be checked against an enumerated admissible action graph or kernel frontier.

Implement:

```text
effectbench_omega/effectbench/kernel/enumerate_frontier.py
```

For each `(task_id, regime, seed, model, terminal_equivalence_class)` group:

1. Enumerate admissible action sequences over the action set:
   - `read_record`
   - `ask_confirm`
   - `ask_clarify`
   - `draft_change`
   - `commit_low`
   - `commit_contract_low`
   - `commit_high`
   - `external_notify_high`
2. Constraints:
   - first action must be `read_record`;
   - exactly one terminal action;
   - terminal action must be final;
   - max length 5 for normal regimes, max length 6 for `SNOWBALL` and `MEMORY_REVISE`;
   - `commit_contract_low` admissible only when `policy_obligation == preserve_contract_artifact_and_expiry`;
   - `ask_confirm` required before write when target ambiguity is present unless the sequence chooses `ask_clarify`;
   - `external_notify_high` is admissible but high effect, not forbidden, unless the task policy explicitly forbids it;
   - future/gold fields are not allowed in online decisions.
3. Compute the nondominated frontier over the full enumerated graph.
4. Relabel every observed trace against that frontier.
5. Emit:
   - `kernel/frontier_enumerated.parquet`
   - `kernel/certificates_enumerated.parquet`
   - `tables/frontier_completeness_<split>.csv`
   - `reports/frontier_completeness_<split>.md`

Acceptance gate:

```text
canonical gate: unexplained_mismatches = 0
legacy agreement diagnostic: report strictness agreement and spurious legacy witnesses
```

Current outcome:

```text
legacy strict-excess labels: 5,149
canonical strict-excess labels: 4,089
spurious legacy witnesses: 1,060
enumerated new strict labels: 0
unexplained mismatches: 0
canonical gate: pass
```

Paper rule:

```text
Do not cite the old 5,149 strict-excess count as a headline result. It is a
legacy diagnostic. Headline labels must come from
effectbench_omega/outputs/<split>/kernel_canonical/certificates_enumerated.parquet.
```

### R2. Corrected Projection-Only Guard vs EffectGuard V2

Problem: current `PROJ_GUARD` already performs most lower-effect substitutions, so it is not a clean projected-safeguard baseline. This creates a near tie with EffectGuard.

Implement two new systems:

```text
PROJ_GUARD_V2
EFFECTGUARD_V2
```

`PROJ_GUARD_V2` rules:

- May block/ask only for projected failures:
  - missing target confirmation;
  - obvious permission overreach;
  - contract artifact not preserved;
  - irreversible/external action when a projection-level rule forbids it.
- Must **not** perform global lower-effect substitution merely because a lower-effect complete trace exists.
- Must pass through the model’s terminal choice when the projected predicate accepts it.

`EFFECTGUARD_V2` rules:

- May substitute a lower-effect admissible suffix when the current-state lower-bound kernel contains one.
- Must log the lower-effect alternative or necessary-high/incomparable reason.
- Must pass no-oracle tests.

Run:

```text
128 tasks × 7 regimes × 2 seeds × 4 models × 2 new systems = 14,336 new trajectories
```

Reuse the existing BASE split. Do not rerun BASE unless a bug is found.

Execution path:

```bash
# 1. Run only V2 guard systems.
JOB_ID=local_open_guard_v2_main_$(date -u +%Y%m%dT%H%M%SZ) \
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

# 2. Merge per-model V2 slices.
.venv/bin/python effectbench_omega/scripts/merge_local_open_slices.py \
  --input-prefix effectbench_omega/outputs/guard_v2_main \
  --out effectbench_omega/outputs/guard_v2_main_all_local \
  --expected-rows-per-model 3584

# 3. Combine frozen BASE with V2 guard rows.
.venv/bin/python effectbench_omega/scripts/build_guard_v2_main_split.py \
  --v2-split effectbench_omega/outputs/guard_v2_main_all_local \
  --out effectbench_omega/outputs/guard_v2_main_with_base_all_local

# 4. Score the combined split canonically.
JOB_ID=stage3_canonical_guard_v2_main_with_base_$(date -u +%Y%m%dT%H%M%SZ) \
SPLIT=guard_v2_main_with_base_all_local \
TABLE_SUFFIX=guard_v2_main_with_base_all_local_canonical \
GUARD_TIE_SYSTEMS="PROJ_GUARD_V2 EFFECTGUARD_V2" \
BOOTSTRAP_SYSTEMS="BASE PROJ_GUARD_V2 EFFECTGUARD_V2" \
CANONICAL_CERT_MODE=enumerated \
  bash effectbench_omega/scripts/run_stage3_offline.sh
```

Acceptance gates:

```text
EFFECTGUARD_V2 strict-excess reduction vs BASE >= 40% relative
EFFECTGUARD_V2 strict-excess reduction vs PROJ_GUARD_V2 >= 20% relative OR >= 2 absolute percentage points
EFFECTGUARD_V2 raw-success retention vs BASE >= 90%
EFFECTGUARD_V2 false-denial rate <= 10%
EFFECTGUARD_V2 p95 added user turns <= 3
No-oracle pass rate = 100%
```

If EffectGuard still ties PROJ_GUARD_V2, drop the controller-superiority claim and make EffectGuard a reference implementation only.

### R3. Native-Fidelity Subset

Problem: reviewers may reject a purely deterministic adapter study because raw success is 100% and native tool APIs are not executed.

Implement a small but real native-fidelity subset using pinned upstream task records and native-style state transitions.

Target denominator:

```text
48 native tasks × 4 regimes × 2 seeds × 4 models × 3 systems = 4,608 trajectories
```

Task split:

- `tau_retail_native`: 16 tasks
- `tau_airline_native`: 16 tasks
- `tau2_telecom_native`: 8 tasks
- `toolsandbox_contract_native`: 8 tasks

Regimes:

- `FULL`
- `SHARDED`
- `MEMORY_REVISE`
- `ADV_EFFECT`

Systems:

- `BASE`
- `PROJ_GUARD_V2`
- `EFFECTGUARD_V2`

Models:

- `mistral_small_3_2_24b_local`
- `qwen3_6_35b_a3b_local`
- `gemma3_27b_it_local`
- `llama3_3_70b_awq_local`

Native-fidelity minimum requirements:

- terminal success must be evaluated from native final-state predicates or native expected-action/state criteria;
- effect ledger must be produced from actual tool/state deltas, not only from abstract action names;
- terminal failures must be possible and counted;
- witness traces must replay in the same native wrapper;
- if a native family cannot be implemented in time, mark it as excluded rather than pretending the adapter is native.

Acceptance gates:

```text
raw_success must not be exactly 100% for every family/system/model;
BASE raw-kernel gap >= 8 percentage points among successful native episodes;
projection residual strict-excess >= 2% for at least 3/4 native families;
certificate replay on all native strict-excess witnesses = 100%.
```

If native integration cannot be finished, submit to ARR only as a formal/evaluation-semantics paper and explicitly call the empirical suite controlled/source-backed adapters.

### R4. Full Certificate Replay

Current replay covers 160 bundles. For EACL, replay more.

Run:

- all strict-excess certificates in the current local split;
- all strict-excess certificates in R2;
- all native strict-excess certificates in R3;
- 500 sampled minimal certificates;
- all incomparability examples used in the paper.

Emit:

```text
reports/certificate_replay_full_<split>.md
witness_bundles/<split>/*.json
```

Acceptance gate:

```text
0 replay failures for all paper-cited canonical certificates. Strict-excess
bundles may contain either an observed lower-effect witness trace or an
enumerated admissible witness candidate.
```

### R5. Targeted CEGAR Stress Cases

Problem: several CEGAR omissions currently show no label-changing collisions.

Add targeted stress rows, not new models:

- `contract_artifact_hash`: stale presigned URL vs fresh draft upload.
- `virtual_clock`: valid token now vs expired token later.
- `compensation_or_payment_hold`: refund/rebook path vs edit path.
- `policy_obligation`: same final state but different policy admissibility.
- `memory_cache`: stale target vs corrected target.
- `user_visible_exposure`: private draft vs public/share/notify.
- `outbox`: no-notification edit vs external notification.

Target:

```text
10 stress tasks per omitted field × 4 regimes × 2 seeds × 2 systems = 1,120 stress trajectories
```

Models are optional here. These can be deterministic witness/replay cases because the point is verifier refinement, not model behavior.

Acceptance gate:

```text
At least one label-changing collision for every future-relevant field, or an explicit reason why that field is not exercised in the current task family.
```

### R6. Qwen Repair Sensitivity

Problem: Qwen has 42 repaired-fallback proposals and 168 non-empty repair logs.

Run only the affected Qwen rows with stricter structured-output enforcement:

```text
trace_id set = all qwen3_6_35b_a3b_local rows where model_proposal_repair_log != []
```

Report:

- original verdict;
- rerun parse status;
- rerun proposed actions;
- rerun verdict;
- whether headline changes.

Acceptance gate:

```text
headline strict-excess rates change by < 1 percentage point, or Qwen is moved to appendix/sensitivity.
```

### R7. Fix or Drop Lattice Sensitivity

The current exact equality across all lattice variants looks suspicious. Choose one:

Option A: implement a real sensitivity analysis where dimension drop/refinement can change dominance and incomparability.

Option B: remove lattice sensitivity from the main paper and state that the primary label uses a fixed declared Pareto lattice; value-governance alternatives are future work.

Recommended under time pressure: **Option B** for main paper, with a small appendix diagnostic only if needed.

Current outcome: **Option B is frozen.** Main claims use the fixed declared
Pareto lattice. The existing lattice sensitivity tables remain appendix or
diagnostic artifacts only because they preserve the headline sign but do not
exercise meaningful dominance/incomparability changes.

Artifact:

```text
effectbench_omega/reports/stage7_lattice_policy_freeze.md
```

### R8. Final Claim And Artifact Freeze

Current outcome: complete locally.

- Final claim registry: `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv`
- Final reproducibility gate: `effectbench_omega/reports/final_reproducibility_gate.md`
- Paper-ready summary: `effectbench_omega/reports/eacl_rescue_paper_ready_summary.md`
- Artifact manifest: `effectbench_omega/tables/artifact_manifest.csv`
- Artifact manifest summary: `effectbench_omega/reports/artifact_manifest.md`

Git LFS is configured for generated traces, response logs, job logs, figures,
presentation/PDF binaries, zip files, and witness bundles. Local model caches,
upstream clones, virtualenvs, and `.env` files remain excluded.

## Final EACL Paper Structure

Main paper should be 8 pages, not 18.

1. Introduction: final-state success is insufficient; least-effect certificate problem.
2. Effect Kernel semantics: transition system, effect lattice, task-equivalence, strict dominance, incomparability.
3. Verifier and certificates: enumerated frontier / quotient / witness bundles.
4. Benchmark substrates: controlled adapters + native-fidelity subset; clear boundary that τ/τ²/τ³ are substrates, not contributions.
5. Experiments:
   - raw-vs-kernel gap;
   - projection loss;
   - corrected EffectGuard vs projection-only guard;
   - native-fidelity subset;
   - certificate replay and CEGAR.
6. Limitations: local open-weight only, no frontier/commercial coverage, controlled adapters, no human audit.

## Venue Plan

Primary target: **ARR Aug 3, 2026 → EACL 2027**.

Fallback: if reviews are weak, revise to **ARR Oct 12, 2026** rather than committing a weak paper.

## Stop Conditions

Do not submit if any of these hold:

- red placeholders remain;
- current 204,800/20,480 API/frontier claims remain in the PDF;
- raw success is presented as realistic despite being exactly 100%;
- `PROJ_GUARD` tie is hidden;
- projection baselines are called SOTA systems without faithful implementations;
- certificates cited in paper do not replay;
- paper cites legacy generated-trace strict labels instead of canonical enumerated-frontier labels;
- no Limitations section;
- no claim registry mapping every number to a file/script.
