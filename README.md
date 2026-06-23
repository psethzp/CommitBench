# CommitBench

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
- Local vLLM endpoint: **running via Stage 2b queue** for `local_open_main_mc_postfix_20260622T214941Z`.
- Upstream benchmark repos: **cloned and pinned**.
- Headline local-only manifest: **generated, 21,504 rows**.
- End-to-end workflow smoke: **passed** on local dry trajectories plus one live local Qwen14 call.
- Final local verification pass: **passed**.
- Native-source audit: **passed**; four benchmark families are source-backed, delegated-docs is explicitly controlled synthetic.
- Stage 1 live per-model smoke: **passed** for all four locked local models, 12 traces/model, 0 failures/model, no-oracle 100%, local cost $0.
- Stage 2 ordered local queue: **complete**. All four local slices finished, 21,504 traces total, 0 final failures, no-oracle 100%, local cost $0.
- Model-controlled action-policy smoke: **passed with hardened defaults**. `local_open_smoke_mc_default_20260622T204613Z` ran 21 traces/model across all regimes and systems, 84 total traces, 0 failures, no-oracle 100%, local cost $0, JSON proposals 21/21 for every model, empty repair logs 21/21 for every model, proposal diversity gate passed.
- Stage 2b model-controlled queue: **running** as `local_open_main_mc_postfix_20260622T214941Z`; current slice is Mistral writing `effectbench_omega/outputs/main_mc_postfix_mistral_small_3_2_24b_local`.
- Queue defaults: **Step 2b hardened path**. `run_local_open_queue.sh` now defaults to `main_mc_postfix`, `MODEL_CONTROLS_POLICY=1`, `MODEL_PROPOSAL_MODE=actions`, TP=4 on GPUs `0,1,2,3`.
- Prompt fairness: **locked**. All four local models receive the same system instruction, task context, user-turn rendering, action enum, `terminal_action` requirement, temperature, and max token budget; only the structured-output transport differs by serving support.

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
| Offline metrics/audits | Working | Projection loss, CEGAR, lattice sensitivity, bootstrap, cost audit, aggregate tables, replay bundles. |
| Local vLLM models | Working | Generic launcher supports the active local model keys; Mistral uses official Mistral tokenizer/config/tool parser. |
| Stage 1 live smokes | Passed | `effectbench_omega/scripts/run_selected4_live_smokes.sh`; four locked models, 48 total live model-call traces, 0 failures. |
| Stage 2 queue | Complete | `effectbench_omega/scripts/run_local_open_queue.sh`; four local slices complete. |
| Stage 2b model-controlled queue | Ready | Default queue mode; restart with the `main_mc_postfix` command in `effectbench_omega/RUNBOOK_LOCAL_ONLY.md`. |
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
- Live Qwen14 smoke outputs: `effectbench_omega/outputs/local_runner_qwen14_smoke/`
- Selected-four smoke certificates: `effectbench_omega/outputs/smoke_<model>/kernel/certificates.parquet`
- Native source audit: `effectbench_omega/reports/native_source_audit.md`

See `effectbench_omega/RUNBOOK_LOCAL_ONLY.md` for staged commands, status, and the next experiment steps.
