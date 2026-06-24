# EffectBench-Omega Local Implementation Handoff

Last updated: 2026-06-23 UTC

## Plan Status

The executable local-only plan in `PLAN.md` is complete through Stage 3. There
are no active queue jobs, no active `run_online.py` processes, and no active
vLLM server for the local experiment path.

What remains is paper/package work, not core experiment execution:

| Area | Status | Notes |
|---|---:|---|
| Stage 1 per-model live smokes | Done | All four local models passed endpoint, workflow, verifier, no-oracle, and cost checks. |
| Stage 2b model-controlled local queue | Done | 21,504 trajectories across four models, seven regimes, two seeds, and three systems. |
| Stage 3 merge and hardened offline metrics | Done | Verifier, no-oracle, projection, CEGAR, lattice, bootstrap, guard-tie, replay, cost, aggregate all completed. |
| Bedrock/API experiments | Intentionally skipped | Archived by active local-only override; not part of headline claims. |
| Full local Qwen rerun of 42 repaired proposals | Deferred | Can be run later only as a named ablation or sensitivity check, not a silent replacement. |
| Figures | Done | Aggregate now writes PNG/PDF figures under `effectbench_omega/figures/main_mc_postfix_all_local/`. |
| Claim registry | Lite fixed | Aggregate now writes 50 computed claim rows; expand only if the manuscript adds more numeric claims. |
| Paper rewrite | Remaining | Required because the current result supports local/open-weight kernel claims, not frontier SOTA leaderboard claims. |

## Active Experiment Boundary

The active setup is local/open-weight only:

| Item | Locked value |
|---|---|
| Denominator | 128 tasks x 7 regimes x 2 seeds x 4 models x 3 systems = 21,504 trajectories |
| Models | `mistral_small_3_2_24b_local`, `qwen3_6_35b_a3b_local`, `llama3_3_70b_awq_local`, `gemma3_27b_it_local` |
| Systems | `BASE`, `PROJ_GUARD`, `EFFECTGUARD` |
| Regimes | `FULL`, `CONCAT`, `SHARDED`, `SNOWBALL`, `REVISE`, `MEMORY_REVISE`, `ADV_EFFECT` |
| Runner | `effectbench_omega/scripts/run_local_open_queue.sh` |
| Main output prefix | `main_mc_postfix` |
| Model controls | Enabled |
| Proposal mode | `actions` |
| GPU policy | TP=4 on GPUs `0,1,2,3` |
| Model order | Mistral, Qwen, Llama, Gemma |

## Implemented Components

| Component | Status | Main files / artifacts | What was added or hardened |
|---|---:|---|---|
| Local model cache checks | Done | `effectbench_omega/scripts/verify_local_open_model_cache.py`, `artifacts/local_open_model_cache.json` | Verifies shared HF cache without creating duplicate local copies. |
| Local model launcher | Done | `effectbench_omega/scripts/launch_local_model.sh` | Generic vLLM launcher for the selected local models; Mistral uses official tokenizer/config/tool-call serving defaults. |
| Mistral serving fix | Done | `effectbench_omega/scripts/install_mistral_vllm_shim.py`, launcher defaults | Replaced old HF tokenizer/custom template path with Mistral-compatible vLLM serving. |
| Manifest and local denominator | Done | `effectbench_omega/manifests/tasks_local_open.csv` | 21,504-row local-open manifest for headline run. |
| Online runner | Done | `effectbench_omega/scripts/run_online.py` | Supports local model calls, balanced smoke selection, model-controlled policies, and per-model outputs. |
| Ordered local queue | Done | `effectbench_omega/scripts/run_local_open_queue.sh` | Serializes four local slices, runs verifier/no-oracle/cost checks per slice, fail-stops on failures. |
| Queue monitor | Done | `effectbench_omega/scripts/show_local_open_queue_status.sh` | Reports queue, current model, summaries, and status files. |
| Model proposal parser | Done | `effectbench_omega/effectbench/agents/systems.py` | Parses JSON object/list outputs, text-scan action lists, legacy LOW/HIGH outputs, and explicit repaired fallback. |
| Structured proposal transport | Done | `effectbench_omega/effectbench/agents/systems.py` | Mistral uses official `emit_plan` tool calling; Qwen/Llama/Gemma use `response_format=json_schema`. |
| Prompt fairness invariant | Done | Runner/config/docs | Same semantic proposal task for all four models: same instruction, task context, user rendering, action enum, terminal action rule, temperature, and token budget. |
| Trace audit fields | Done | `traces.parquet`, runner | Logs raw model output, proposed actions, parse status, and repair log. |
| API audit fields | Done | `api_logs.jsonl` | Logs structured-output fallback errors and local request metadata. |
| Guard audit fields | Done | Runtime logs and trace guard decisions | Logs model proposal review, executed actions, substitutions, and ask/read decisions. |
| Merge utility | Done | `effectbench_omega/scripts/merge_local_open_slices.py` | Merges the four per-model Stage 2b outputs into one replayable split. |
| Stage 3 driver | Done | `effectbench_omega/scripts/run_stage3_offline.sh` | Replays verifier, no-oracle, projections, CEGAR, lattice, bootstrap, guard tie, bundles, replay, cost, aggregate, and pytest. |
| Kernel verifier | Done | `effectbench_omega/effectbench/kernel/verifier.py` | Produced 21,504 certificates, frontiers, prune log, rejected abstractions, and summary. |
| Projection baselines | Hardened | `effectbench_omega/effectbench/baselines/project.py` | Replaced placeholder fixed-retention scaffolds with data-derived accept/reject predicates and reason table. |
| Bootstrap uncertainty | Hardened | `effectbench_omega/effectbench/metrics/bootstrap.py` | Replaced placeholder intervals with paired, task-cluster, and hierarchical bootstraps over paired units. |
| CEGAR audit | Hardened | `effectbench_omega/effectbench/audit/cegar.py` | Replaced placeholder audit with reduced abstract-state collision and label-change audit. |
| Guard-tie audit | Added | `effectbench_omega/effectbench/audit/guard_tie.py` | Explains why `PROJ_GUARD` and `EFFECTGUARD` are almost tied. |
| Figure generation | Added | `effectbench_omega/effectbench/metrics/aggregate.py`, `effectbench_omega/figures/main_mc_postfix_all_local/` | Writes online-control, projection-loss, and family/regime strict-excess figures in PNG and PDF. |
| Lite claim registry | Added | `effectbench_omega/effectbench/metrics/aggregate.py`, `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv` | Writes 50 source-linked claim rows covering denominator, system metrics, projection metrics, and local cost. |
| Witness bundles | Done | `effectbench_omega/witness_bundles/main_mc_postfix_all_local/` | Reviewer-readable sampled certificate bundles and index. |
| Certificate replay | Done | `effectbench_omega/reports/certificate_replay_main_mc_postfix_all_local.md` | Strict replay over sampled bundles passed. |
| No-oracle tests | Done | `effectbench_omega/tests/no_oracle/` | Report and pytest both passed. |
| Runbook docs | Updated | `effectbench_omega/RUNBOOK_LOCAL_ONLY.md` | Tracks completed stages, commands, outputs, caveats, and claims. |
| README | Updated | `README.md` | Records local-only defaults and current state. |

## Main Completed Jobs

| Job | Status | Evidence |
|---|---:|---|
| Accepted all-model MC smoke | Done | `effectbench_omega/jobs/local_open_smoke_mc_default_20260622T204613Z` |
| Full Stage 2b local queue | Done | `effectbench_omega/jobs/local_open_main_mc_postfix_20260622T214941Z` |
| Merged Stage 2b split | Done | `effectbench_omega/outputs/main_mc_postfix_all_local/merge_summary.json` |
| Hardened Stage 3 offline suite | Done | `effectbench_omega/jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z` |
| Latest Stage 3 pointer | Done | `effectbench_omega/jobs/stage3_latest` |

## Important Defaults To Preserve

Mistral serving defaults are mandatory for paper-grade local runs:

```text
--tokenizer-mode mistral
--config-format mistral
--tool-call-parser mistral
--enable-auto-tool-choice
--limit-mm-per-prompt '{"image":10}'
VLLM_USE_FLASHINFER_SAMPLER=0
load_format=auto
```

Do not reintroduce:

```text
--language-model-only
old custom Mistral chat template
--tokenizer-mode hf for Mistral
--load-format mistral unless consolidated duplicate Mistral weights are deliberately cached
```

## Caveats and Errors Logged

| Caveat / issue | Status | Impact |
|---|---:|---|
| No Bedrock/API access | Accepted boundary | Headline claims must be local/open-weight only. No GPT/Claude/Gemini/Bedrock generality. |
| Old pre-fix Mistral MC run | Invalidated | `effectbench_omega/outputs/main_mc_mistral_small_3_2_24b_local/INVALID_DO_NOT_USE.md`; do not aggregate it. |
| Qwen repaired proposals | Logged caveat | 42/5,376 Qwen proposals used `unparsed:repair_fallback`; 168 Qwen traces have nonempty repair logs. Keep visible or rerun later as ablation. |
| Mistral full post-fix parse | Acceptable | 5,362 JSON/tool-call parses and 14 text-scan parses; 0 repaired fallbacks. |
| Llama runtime | Expected | Dense 70B AWQ over TP=4 took much longer than other slices; completed successfully. |
| PROJ_GUARD / EFFECTGUARD tie | Major claim caveat | EffectGuard only beats PROJ_GUARD by 0.0419 percentage points in strict-excess rate. Do not claim strong superiority over PROJ_GUARD. |
| Current adapters have 100% raw success | Claim caveat | The paper should emphasize least-effect certification, not raw success competition. |
| CEGAR no-collision fields | Conservative-audit strength with boundary | The audit only rejects omissions when this scaffold shows label-changing collisions. Zero-collision fields mean not exercised as label-changing here, not universally irrelevant. |
| Projection and CEGAR audits are simulator-local | Claim caveat | They are replayable and data-derived, but not external human audit. |
| Figures | Fixed | Six figure files exist: three PNG and three PDF. |
| Claim registry lite | Fixed | `claim_registry_check.py` passes with 50 rows. Manuscript-specific registry expansion is still needed if new numbers are introduced. |

## Recommended Claim Framing

Use:

> Across reproducible open-weight tool agents, final-state success substantially
> overstates certified least-effect success. Projected safeguards reduce but do
> not eliminate residual strict excess. EffectGuard is a no-oracle reference
> controller that matches a strong projection guard and slightly improves a few
> telecom target-confirmation cases in this implementation.

Do not use:

```text
state of the art across frontier models
commercial model coverage
GPT/Claude/Gemini generality
largest-model benchmark
strong EffectGuard-over-PROJ_GUARD superiority
guaranteed acceptance
```

## Next Non-Compute Steps

| Step | Why |
|---|---|
| Decide final claim wording | Current data supports BASE-vs-guard and projection-loss claims strongly, but not strong EffectGuard-vs-PROJ claims. |
| Review generated figures in paper context | The required figure files now exist; still choose which ones enter the paper. |
| Expand claim registry only as paper numbers grow | Current lite registry covers the main computed result numbers; add rows for any new manuscript claims. |
| Optional Qwen 42-row ablation | Useful sensitivity check only; do not silently replace the frozen primary run. |
| Paper rewrite | Local/open-weight kernel semantics paper, not frontier model leaderboard. |
