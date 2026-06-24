# CommitBench

PPT -> https://docs.google.com/presentation/d/105Rw6dBRRDFlABEg7VL8iJBnOge10DoGh79Z1J3YwSE/edit?slide=id.g3ee20b0a688_2_2#slide=id.g3ee20b0a688_2_2

Local handoff/setup repo for the EffectBench-Ω minimal-plus experiment suite.

Current active plan: **local/open-weight only**. Bedrock/API runs are archived and should not be used for headline claims.

Historical Bedrock smoke notes exist in older runbooks, but the active `PLAN.md` path does not require Bedrock access.

## Current Status

- Main Bedrock experiments: **not run**.
- Full local Qwen experiment grid: **not run by request**.
- Local-open 21,504-row manifest: **built** at `effectbench_omega/manifests/tasks_local_open.csv`.
- Selected-four local-open dry smoke: **passed** on 60 traces.
- Historical live local model-call smoke: **passed** with `qwen3_14b_awq_local` on 1 trajectory, 0 failures.
- Selected-four live model-call smokes: **passed** for Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Gemma-3-27B-it, and Llama-3.3-70B-AWQ.
- Open model cache: Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Gemma-3-27B-it, and Llama-3.3-70B-AWQ are ready in the shared HF cache. Qwen3-14B-AWQ and Qwen3-30B-A3B are also cached but no longer in the locked headline grid.
- Local vLLM endpoint: **stopped** after completed Stage 2b queue; no experiment server is currently required.
- Upstream benchmark repos: **cloned and pinned**.
- Headline local-only manifest: **generated, 21,504 rows**.
- End-to-end workflow smoke: **passed** on local dry trajectories plus one live local Qwen14 call.
- Final local verification pass: **passed**.
- Native-source audit: **passed**; four benchmark families are source-backed, delegated-docs is explicitly controlled synthetic.
- Stage 1 live per-model smoke: **passed** for all four locked local models, 12 traces/model, 0 failures/model, no-oracle 100%, local cost $0.
- Stage 2 ordered local queue: **complete**. All four local slices finished, 21,504 traces total, 0 final failures, no-oracle 100%, local cost $0.
- Model-controlled action-policy smoke: **passed with hardened defaults**. `local_open_smoke_mc_default_20260622T204613Z` ran 21 traces/model across all regimes and systems, 84 total traces, 0 failures, no-oracle 100%, local cost $0, JSON proposals 21/21 for every model, empty repair logs 21/21 for every model, proposal diversity gate passed.
- Stage 2b model-controlled queue: **complete** as `local_open_main_mc_postfix_20260622T214941Z`; all four slices finished, 21,504 traces, 0 failures, no-oracle 100%, local cost $0.
- Stage 3 merge: **complete** at `effectbench_omega/outputs/main_mc_postfix_all_local/`; 21,504 merged traces, 21,504 API log rows, 0 failures.
- Stage 3 hardened offline suite: **complete** as `stage3_hardened_main_mc_postfix_all_local_20260623T220316Z`; 21,504 certificates, 5,149 strict-excess certificates, 0 unresolved abstraction warnings, no-oracle aggregate pass, 160 replay bundles checked with 0 failures.
- Hardened metrics: **complete**. Projection baselines are data-derived, bootstrap uses paired/task-cluster/hierarchical resampling with 2,000 draws, CEGAR uses reduced abstract-state collision checks, and `guard_tie` explains PROJ_GUARD vs EFFECTGUARD.
- Stage 3 figures and lite claim registry: **complete**. Aggregate writes PNG/PDF figures under `effectbench_omega/figures/main_mc_postfix_all_local/` and a 50-row computed registry at `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv`.
- Queue defaults: **Step 2b hardened path**. `run_local_open_queue.sh` now defaults to `main_mc_postfix`, `MODEL_CONTROLS_POLICY=1`, `MODEL_PROPOSAL_MODE=actions`, TP=4 on GPUs `0,1,2,3`.
- Prompt fairness: **locked**. All four local models receive the same system instruction, task context, user-turn rendering, action enum, `terminal_action` requirement, temperature, and max token budget; only the structured-output transport differs by serving support.

## Current Caveats

- Qwen full slice has `42/5,376` audited repaired-fallback proposals. The primary run remains frozen; any same-prompt rerun of those rows should be reported as a sensitivity/ablation, not silently substituted.
- Stage 3 projection/bootstrap/CEGAR are now replayable data-derived local audits. They are still simulator-local, not external human audits. CEGAR no-collision fields are a conservative-audit strength: the checker does not reject omissions without observed label-changing collisions; that means "not exercised by this scaffold," not "never future-relevant."
- PROJ_GUARD and EFFECTGUARD are effectively tied in this local implementation: only `3/7,168` paired units differ in verifier verdict, all Mistral telecom confirm-target cases.
- Active claims are local/open-weight only. Do not claim Bedrock/frontier leaderboard coverage from this run.

## Implemented Features

| Area | Status | Notes |
|---|---|---|
| Task families | Working local adapters | Retail, airline, telecom, delegated docs, and ToolSandbox/contract-style tasks. |
| Regimes | Working | `FULL`, `CONCAT`, `SHARDED`, `SNOWBALL`, `REVISE`, `MEMORY_REVISE`, `ADV_EFFECT`. |
| Manifest builder | Working | `effectbench_omega/manifests/tasks_local_open.csv` has the locked 21,504-row denominator. |
| Online systems | Working local policies | `BASE`, `PROJ_GUARD`, `EFFECTGUARD`. |
| Model proposal parser | Working | JSON, text-scan, LOW/HIGH legacy, explicit repaired fallback action proposals, required `terminal_action`, Mistral tool calls, and JSON-schema constrained proposals for Qwen/Llama/Gemma. |
| No-oracle guard | Working | Runtime forbidden-field checks plus audit reports. |
| Kernel verifier | Working | Emits certificates, frontiers, prune logs, rejected-abstraction table, and summary JSON. |
| Offline metrics/audits | Working | Projection loss, CEGAR, lattice sensitivity, bootstrap, cost audit, aggregate tables, figures, claim registry, replay bundles. |
| Local vLLM models | Working | Generic launcher supports the active local model keys; Mistral uses official Mistral tokenizer/config/tool parser. |
| Stage 1 live smokes | Passed | `effectbench_omega/scripts/run_selected4_live_smokes.sh`; four locked models, 48 total live model-call traces, 0 failures. |
| Stage 2 queue | Complete | `effectbench_omega/scripts/run_local_open_queue.sh`; four local slices complete. |
| Stage 2b model-controlled queue | Complete | `main_mc_postfix`; four local model slices complete, 21,504 total traces, 0 failures. |
| Stage 3 merge helper | Complete | `effectbench_omega/scripts/merge_local_open_slices.py`; merged output is `effectbench_omega/outputs/main_mc_postfix_all_local/`. |
| Stage 3 hardened offline suite | Complete | `effectbench_omega/scripts/run_stage3_offline.sh`; hardened projection/bootstrap/CEGAR/guard-tie outputs generated for `main_mc_postfix_all_local`. |
| Bedrock | Archived | Not part of the active local-only plan. |

## Key Outputs

- Active runbook/checkpoint tracker: `effectbench_omega/RUNBOOK_LOCAL_ONLY.md`
- Archived Bedrock-era runbook: `effectbench_omega/RUNBOOK.md`
- Local-open model cache report: `effectbench_omega/artifacts/local_open_model_cache.json`
- Local Qwen cache report: `effectbench_omega/artifacts/local_qwen_cache.json`
- Repo/model pins: `effectbench_omega/artifacts/repo_versions.json`
- Workflow smoke dry outputs: `effectbench_omega/outputs/workflow_smoke_dry/`
- Workflow smoke local-Qwen outputs: `effectbench_omega/outputs/workflow_smoke_local_qwen/`
- Selected-four dry outputs: `effectbench_omega/outputs/selected4_dry/`
- Selected-four live smoke automation: `effectbench_omega/scripts/run_selected4_live_smokes.sh`
- Selected-four live endpoint smoke reports: `effectbench_omega/reports/live_smokes/`
- Selected-four Stage 1 live outputs: `effectbench_omega/outputs/smoke_<model>/`
- Ordered Stage 2 queue runner: `effectbench_omega/scripts/run_local_open_queue.sh`
- Ordered Stage 2 queue monitor: `effectbench_omega/scripts/show_local_open_queue_status.sh`
- Pre-fix model-controlled balanced smoke outputs: `effectbench_omega/outputs/smoke_mc_balanced_<model>/`
- Accepted default model-controlled smoke outputs: `effectbench_omega/outputs/smoke_mc_default_<model>/`
- Recommended next full model-controlled outputs: `effectbench_omega/outputs/main_mc_postfix_<model>/`
- Merged Stage 2b output: `effectbench_omega/outputs/main_mc_postfix_all_local/`
- Stage 3 hardened job log: `effectbench_omega/jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z/`
- Stage 3 main tables: `effectbench_omega/tables/main_mc_postfix_all_local/`
- Stage 3 hardened projection table: `effectbench_omega/tables/projection_loss_main_mc_postfix_all_local.csv`
- Stage 3 hardened uncertainty table: `effectbench_omega/tables/uncertainty_main_mc_postfix_all_local.csv`
- Stage 3 hardened CEGAR table: `effectbench_omega/tables/cegar_rejections_main_mc_postfix_all_local.csv`
- Stage 3 guard-tie report: `effectbench_omega/tables/guard_tie_main_mc_postfix_all_local.md`
- Stage 3 figures: `effectbench_omega/figures/main_mc_postfix_all_local/`
- Stage 3 witness bundles: `effectbench_omega/witness_bundles/main_mc_postfix_all_local/`
- Stage 3 lite claim registry: `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv`
- Live Qwen14 smoke outputs: `effectbench_omega/outputs/local_runner_qwen14_smoke/`
- Selected-four smoke certificates: `effectbench_omega/outputs/smoke_<model>/kernel/certificates.parquet`
- Native source audit: `effectbench_omega/reports/native_source_audit.md`

See `effectbench_omega/RUNBOOK_LOCAL_ONLY.md` for staged commands, status, and the next experiment steps.
