# EffectBench-Ω Local-Only Runbook

## Current Boundary

No Bedrock/API experiments. The paper claim is local/open-weight reproducibility plus certified least-effect semantics, not frontier model coverage.

## Locked Local Denominator

```text
128 tasks × 7 regimes × 2 seeds × 4 local models × 3 systems = 21,504 trajectories
```

Task split:

| Family | Tasks |
|---|---:|
| TAU retail | 32 |
| TAU airline | 32 |
| TAU2 telecom | 32 |
| Delegated docs | 16 |
| ToolSandbox contract | 16 |

Models:

| Model key | HF repo | Cache status | Role |
|---|---|---|---|
| `mistral_small_3_2_24b_local` | `mistralai/Mistral-Small-3.2-24B-Instruct-2506` | Ready | non-Qwen tool-control model |
| `qwen3_6_35b_a3b_local` | `Qwen/Qwen3.6-35B-A3B` | Ready | larger local Qwen stress |
| `gemma3_27b_it_local` | `google/gemma-3-27b-it` | Ready | non-Qwen Gemma control |
| `llama3_3_70b_awq_local` | `casperhansen/llama-3.3-70b-instruct-awq` | Ready | large non-Qwen AWQ control |

Full-precision `meta-llama/Llama-3.3-70B-Instruct` remains not cached. The AWQ model is the practical local substitute.

## Done

| Checkpoint | Status | Evidence |
|---|---|---|
| Source-backed adapters | Done | `reports/native_source_audit.md` and `reports/native_source_audit_local_open.md` |
| Local-open manifest | Done | `manifests/tasks_local_open.csv`, 21,504 rows |
| Local runner generalized | Done | `run_online.py` now calls vLLM for any `*_local` model |
| Generic local launcher | Done | `scripts/launch_local_model.sh` |
| Cache verifier | Done | `scripts/verify_local_open_model_cache.py`, writes `artifacts/local_open_model_cache.json` |
| Local-open dry smoke | Done | `outputs/local_open_dry/`, 60 traces, 0 failures |
| Selected-four dry smoke | Done | `outputs/selected4_dry/`, 60 traces, 0 failures |
| Local-open verifier smoke | Done | 60 certs, 0 unresolved abstraction warnings |
| Local-open no-oracle smoke | Done | 100 percent pass |
| Live Qwen14 model-call smoke | Done | `outputs/local_runner_qwen14_smoke/`, 1 trace, 0 failures |
| Mistral 3.2 vLLM serving patch | Done | `scripts/launch_local_model.sh` uses Mistral tokenizer/config/tool parser; `scripts/install_mistral_vllm_shim.py` patches current vLLM/Pixtral compatibility |
| Selected-four live endpoint smokes | Done | `reports/live_smokes/*_endpoint_smoke.json`; all endpoints returned HTTP/API OK |
| Selected-four Stage 1 live smokes | Done | `outputs/smoke_<model>/`; 12 traces/model, 0 failures/model |
| Selected-four Stage 1 verifier/no-oracle/cost | Done | 12 certificates/model, 0 unresolved abstraction warnings/model, no-oracle 100 percent, local cost 0 |
| Stage 2 ordered local queue script | Done | `scripts/run_local_open_queue.sh`; order Mistral, Qwen, Llama, Gemma |
| Stage 2 queue monitor script | Done | `scripts/show_local_open_queue_status.sh` |
| Optional Llama 3.3 70B AWQ cache | Done | `casperhansen/llama-3.3-70b-instruct-awq`, 9 shards, no incomplete blobs |
| Optional Gemma 3 27B IT cache | Done | `google/gemma-3-27b-it`, 12 shards, no incomplete blobs |
| Model proposal parser and repair fallback | Done | `effectbench/agents/systems.py`; JSON, text-scan, legacy, and repaired fallback action proposals |
| Structured model proposal calls | Done | Mistral uses `emit_plan` tool calls; Qwen/Llama/Gemma use `response_format=json_schema` with audited fallback |
| Queue defaults hardened for Step 2b | Done | `run_local_open_queue.sh` defaults to `main_mc_postfix`, `--model-controls-policy`, `--model-proposal-mode actions`, TP=4 |
| Balanced model-controlled smoke selector | Done | `scripts/run_online.py --selection-strategy balanced_regime_system` |
| Stage 1 model-controlled balanced smoke | Superseded | Pre-fix smoke passed workflow but Mistral proposals were repaired fallback; do not use for paper-grade MC claims |
| Default all-four model-controlled smoke | Done | `local_open_smoke_mc_default_20260622T204613Z`; 21 traces/model, 0 failures/model, no-oracle 100%, local cost $0 |
| Model proposal diversity gate | Done | Post-fix proposal signatures differ across all four models |
| Stage 2b model-controlled queue | Done | `local_open_main_mc_postfix_20260622T214941Z`; all four slices complete, 21,504 traces, 0 failures |
| Stage 3 merge | Done | `outputs/main_mc_postfix_all_local/`; 21,504 traces, 21,504 API rows, 0 failures |
| Stage 3 hardened offline suite | Done | `jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z`; verifier, no-oracle, data-derived projection, CEGAR collision audit, paired/bootstrap CIs, guard-tie audit, replay, cost, aggregate, pytest all exited 0 |

## Cache Commands

Check all planned local model caches:

```bash
python effectbench_omega/scripts/verify_local_open_model_cache.py
```

Continue/repair Mistral cache without creating duplicate local copies:

```bash
hf download mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  --include 'model-*.safetensors' \
  --include 'model.safetensors.index.json' \
  --include '*.json' \
  --include 'tokenizer.*' \
  --include '*.model' \
  --max-workers 8
```

Do not use `--local-dir` for these models; that creates duplicate full copies outside the shared HF cache.
Do not fetch Mistral's consolidated safetensor if the 10 sharded `model-*.safetensors` files are present; it duplicates roughly 48 GB of weights.

Cache optional Llama 3.3 70B AWQ without Xet finalization issues:

```bash
set -a; source .env; set +a
export HF_HUB_DISABLE_XET=1
hf download casperhansen/llama-3.3-70b-instruct-awq \
  --include 'model-*.safetensors' \
  --include 'model.safetensors.index.json' \
  --include '*.json' \
  --include '*.txt' \
  --include '*.md' \
  --max-workers 8
```

Cache optional Gemma 3 27B IT:

```bash
set -a; source .env; set +a
export HF_HUB_DISABLE_XET=1
hf download google/gemma-3-27b-it \
  --include 'model-*.safetensors' \
  --include 'model.safetensors.index.json' \
  --include '*.json' \
  --include '*.model' \
  --include '*.md' \
  --max-workers 8
```

## Launch One Local Model

Stop any existing vLLM server on port 8001, then launch the target model:

```bash
pkill -f 'vllm.entrypoints.openai.api_server' || true
LOCAL_MODEL=mistral_small_3_2_24b_local bash effectbench_omega/scripts/launch_local_model.sh
```

If the venv is recreated, reinstall the Mistral tokenizer compatibility shim before launching Mistral:

```bash
.venv/bin/python effectbench_omega/scripts/install_mistral_vllm_shim.py
```

Available `LOCAL_MODEL` values:

```text
qwen3_14b_awq_local
mistral_small_3_2_24b_local
qwen3_30b_a3b_local
qwen3_6_35b_a3b_local
llama3_3_70b_awq_local
gemma3_27b_it_local
```

The locked headline manifest uses only:

```text
mistral_small_3_2_24b_local
qwen3_6_35b_a3b_local
gemma3_27b_it_local
llama3_3_70b_awq_local
```

## Stage 1: Per-Model Smoke

Run after launching each model:

```bash
python effectbench_omega/scripts/run_online.py \
  --config effectbench_omega/configs/local_open.yaml \
  --manifest effectbench_omega/manifests/tasks_local_open.csv \
  --split smoke_${LOCAL_MODEL} \
  --systems BASE PROJ_GUARD EFFECTGUARD \
  --models ${LOCAL_MODEL} \
  --regimes FULL MEMORY_REVISE ADV_EFFECT \
  --out effectbench_omega/outputs/smoke_${LOCAL_MODEL} \
  --limit 12 \
  --call-local-model
```

Then run verifier/no-oracle on that smoke output.

The selected-four live smoke automation has already passed:

```bash
bash effectbench_omega/scripts/run_selected4_live_smokes.sh
```

Observed Stage 1 results:

| Model | Endpoint | Stage 1 traces | Failures | Certificates | No-oracle | Cost |
|---|---:|---:|---:|---:|---:|---:|
| `mistral_small_3_2_24b_local` | OK | 12 | 0 | 12 | 100% | $0 |
| `qwen3_6_35b_a3b_local` | OK | 12 | 0 | 12 | 100% | $0 |
| `gemma3_27b_it_local` | OK | 12 | 0 | 12 | 100% | $0 |
| `llama3_3_70b_awq_local` | OK | 12 | 0 | 12 | 100% | $0 |

Mistral 3.2 defaults to the official Mistral serving path in
`scripts/launch_local_model.sh`: `--tokenizer-mode mistral`,
`--config-format mistral`, `--tool-call-parser mistral`,
`--enable-auto-tool-choice`, and `--limit-mm-per-prompt '{"image":10}'`.
Do not re-add `--language-model-only` or the custom Mistral chat template.
Do not add `--load-format mistral` with the current HF sharded cache; that
expects consolidated Mistral-format weights and fails unless those duplicate
weights are separately cached. The launcher keeps `VLLM_USE_FLASHINFER_SAMPLER=0`
because FlashInfer sampling compilation failed on this stack.

Endpoint smoke is a health/API smoke. The raw endpoint responses are saved in
`reports/live_smokes/*_endpoint_smoke.json`; Mistral and Qwen did not strictly
echo the requested `LOW` token, but the live Stage 1 workflow calls, ledgers,
verifier, no-oracle audit, and cost audit all completed successfully with zero
recorded failures.

## Stage 2: Full Local Runs

The queue script now defaults to the Step 2b model-controlled path. To rerun
the older deterministic Stage 2 workflow, explicitly opt out of model controls:

```bash
cd /home/ubuntu/nachiket/CommitBench
JOB_ID=local_open_$(date -u +%Y%m%dT%H%M%SZ) \
QUEUE_MODEL_TP=4 \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
OUTPUT_PREFIX=main \
SPLIT_PREFIX=main \
REPORT_PREFIX=main \
MODEL_CONTROLS_POLICY=0 \
MODEL_PROPOSAL_MODE=low_high \
setsid -f bash -c 'exec bash effectbench_omega/scripts/run_local_open_queue.sh \
  > effectbench_omega/jobs/local_open_queue_launch.log 2>&1'
```

Use `setsid -f`, not bare `nohup`, so the queue is detached from short-lived
operator shells and can keep running after this terminal command returns.

Queue order:

```text
mistral_small_3_2_24b_local
qwen3_6_35b_a3b_local
llama3_3_70b_awq_local
gemma3_27b_it_local
```

Monitor:

```bash
cd /home/ubuntu/nachiket/CommitBench
bash effectbench_omega/scripts/show_local_open_queue_status.sh
tail -f effectbench_omega/jobs/local_open_latest/events.tsv
tail -f effectbench_omega/jobs/local_open_latest/logs/mistral_small_3_2_24b_local_vllm.log
tail -f effectbench_omega/jobs/local_open_latest/logs/mistral_small_3_2_24b_local_run_online.log
nvidia-smi
```

The queue writes per-model outputs to:

```text
effectbench_omega/outputs/main_mistral_small_3_2_24b_local
effectbench_omega/outputs/main_qwen3_6_35b_a3b_local
effectbench_omega/outputs/main_llama3_3_70b_awq_local
effectbench_omega/outputs/main_gemma3_27b_it_local
```

It also runs per-slice verifier, no-oracle, and cost checks before moving to the next model. The queue fail-stops on launch failure, runner failure, or any nonempty `failures.jsonl`.

Manual equivalent for one model:

```bash
python effectbench_omega/scripts/run_online.py \
  --config effectbench_omega/configs/local_open.yaml \
  --manifest effectbench_omega/manifests/tasks_local_open.csv \
  --split main_${LOCAL_MODEL} \
  --systems BASE PROJ_GUARD EFFECTGUARD \
  --models ${LOCAL_MODEL} \
  --regimes FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT \
  --out effectbench_omega/outputs/main_${LOCAL_MODEL} \
  --limit 5376 \
  --call-local-model
```

Each model slice is 5,376 trajectories.

Current queue status:

```text
job_id: local_open_20260622T113253Z plus local_open_gemma_repair_20260622T142850Z
queue_pid: completed
started_utc: 2026-06-22T11:32:56Z
completed_utc: 2026-06-22T14:39:28Z
final_status: all four Stage 2 local slices complete
server: stopped
last_checked_utc: 2026-06-22T15:08:02Z
```

Completed slices:

| Model | Status | Traces | Failures | Certificates | Runtime |
|---|---:|---:|---:|---:|---:|
| `mistral_small_3_2_24b_local` | Done | 5,376 | 0 | 5,376 | 11:34:06-11:50:16 UTC |
| `qwen3_6_35b_a3b_local` | Done | 5,376 | 0 | 5,376 | 11:52:16-12:01:10 UTC |
| `llama3_3_70b_awq_local` | Done | 5,376 | 0 | 5,376 | 12:03:00-12:39:34 UTC |
| `gemma3_27b_it_local` | Done after repair | 5,376 | 0 | 5,376 | 14:31:14-14:39:28 UTC |

Gemma failure cause: Gemma's chat template rejects consecutive user turns in
multi-turn regimes (`Conversation roles must alternate user/assistant/...`).
`scripts/run_online.py` now packs Gemma's benchmark turns into one user message
for the local model-advice health/logging call. This does not change the online
policy path because `--model-controls-policy` is not used for these Stage 2
slices.

Final Stage 2 integrity summary:

```text
total_traces: 21,504
total_api_logs: 21,504
total_failures: 0
total_certificates: 21,504
total_unresolved_abstraction_warnings: 0
no_oracle_pass_rate: 100 percent for each slice
local_cost_usd: 0
```

Important caveat: these Stage 2 runs call and log each local model, but online
policies are deterministic because `--model-controls-policy` is not enabled.
The identical certificate counts across models are therefore expected for this
implementation path. Use this as local workflow/denominator completion unless a
separate model-controlled variant is intentionally launched.

## Stage 2b: Model-Controlled Full Local Runs

This is the main candidate local run where model action proposals affect the
online policy path and are reviewed by `PROJ_GUARD` / `EFFECTGUARD`.

Implemented hardening:

```text
model proposal mode: actions
parser paths: JSON object/list, text scan, LOW/HIGH legacy
repair fallback: unparseable output becomes an explicit repaired action plan
terminal action schema: required terminal_action plus actions ending in that action
Mistral action proposal call: official vLLM Mistral tool parser with emit_plan
Qwen/Llama/Gemma action proposal call: OpenAI response_format=json_schema
prompt fairness invariant: same system instruction, task context, user-turn
  rendering, action enum, terminal_action rule, temperature, and max token
  budget for all four local models; only structured-output transport differs
trace audit fields: model_raw_output, model_proposed_actions,
  model_proposal_parse_status, model_proposal_repair_log
api audit fields: structured_output_fallback_error
guard audit fields: model proposal reviewed/executed, substitution decisions
smoke sampling: balanced_regime_system for mixed regime/system coverage
queue defaults: output_prefix=main_mc_postfix, model_controls_policy=1,
  model_proposal_mode=actions, queue_model_tp=4, cuda_visible_devices=0,1,2,3
```

Accepted default balanced MC smoke command shape. This overrides only the
small-smoke output prefix, limit, and balanced sampling; model controls and
action proposal mode come from the queue defaults:

```bash
JOB_ID=local_open_smoke_mc_default_$(date -u +%Y%m%dT%H%M%SZ) \
QUEUE_MODELS="mistral_small_3_2_24b_local qwen3_6_35b_a3b_local llama3_3_70b_awq_local gemma3_27b_it_local" \
OVERWRITE_OUTPUTS=1 \
QUEUE_MODEL_TP=4 \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
SLICE_LIMIT=21 \
OUTPUT_PREFIX=smoke_mc_default \
SPLIT_PREFIX=smoke_mc_default \
REPORT_PREFIX=smoke_mc_default \
ROW_SELECTION_STRATEGY=balanced_regime_system \
setsid -f bash -c 'exec bash effectbench_omega/scripts/run_local_open_queue.sh \
  > effectbench_omega/jobs/local_open_queue_launch.log 2>&1'
```

Pre-fix balanced MC smoke result is retained only as a debugging breadcrumb:
Mistral output was garbled and all Mistral proposals were repaired fallback
under the old serving path. Do not use `outputs/smoke_mc_balanced_*` as the
paper-grade model-controlled smoke.

Post-fix balanced MC smoke result:

| Model | Traces | Failures | Certificates | Strict excess | Parse / repair note |
|---|---:|---:|---:|---:|---|
| `mistral_small_3_2_24b_local` | 21 | 0 | 21 | 5 | JSON/tool-call proposals 21/21; repair log empty 21/21 |
| `qwen3_6_35b_a3b_local` | 21 | 0 | 21 | 7 | JSON-schema proposals 21/21; repair log empty 21/21 |
| `llama3_3_70b_awq_local` | 21 | 0 | 21 | 5 | JSON-schema proposals 21/21; repair log empty 21/21 |
| `gemma3_27b_it_local` | 21 | 0 | 21 | 4 | JSON-schema proposals 21/21; repair log empty 21/21 |

Proposal diversity gate:

```text
total_failures: 0
no_oracle_sentinel_pass_rate: 100 percent for each slice
structured_output_fallback_errors: 0 for each slice
diversity_gate: pass
pairwise proposal signatures: all unequal
```

Current Stage 2b queue:

```text
job_id: local_open_main_mc_postfix_20260622T214941Z
started_utc: 2026-06-22T21:49:53Z
order: Mistral, Qwen, Llama, Gemma
slice_limit: 5,376 trajectories/model
model_controls_policy: enabled
model_proposal_mode: actions
row_selection_strategy: first
tensor_parallelism: TP=4 on GPUs 0,1,2,3
current_model: queue
current_status: done
current_output: effectbench_omega/outputs/main_mc_postfix_all_local
last_checked_utc: 2026-06-23T17:06:40Z
completed_utc: 2026-06-23T15:44:52Z
stage3_merge: done, 21,504 traces, 21,504 API log rows, 0 failures
invalid_old_job_id: local_open_main_mc_20260622T161747Z, stopped before Qwen/Llama/Gemma due pre-fix Mistral serving
```

Completed Stage 2b slices:

| Model | Status | Load time | Slice time | Traces | Failures | Certificates | Strict excess | Proposal parse / repair note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `mistral_small_3_2_24b_local` | Done | 1.00 min | 137.57 min | 5,376 | 0 | 5,376 | 1,201 | `json`: 5,362, `text_scan`: 14; repair log empty 5,376/5,376 |
| `qwen3_6_35b_a3b_local` | Done | 1.83 min | 33.98 min | 5,376 | 0 | 5,376 | 1,588 | `json`: 5,152, `text_scan`: 164, `low_high_legacy`: 18, `unparsed:repair_fallback`: 42; repair log empty 5,208/5,376 |
| `llama3_3_70b_awq_local` | Done | 1.50 min | 742.82 min | 5,376 | 0 | 5,376 | 1,232 | `json`: 5,376; repair log empty 5,376/5,376 |
| `gemma3_27b_it_local` | Done | 2.17 min | 149.23 min | 5,376 | 0 | 5,376 | 1,128 | `json`: 5,376; repair log empty 5,376/5,376 |

Why Llama is slow:

```text
Llama is a dense 70B AWQ checkpoint; Qwen is MoE with much lower active
parameters, while Mistral/Gemma are smaller. The runner is intentionally
serial for clean replay, so vLLM logs show one running request and no queue
backlog. TP=4 spreads that one dense model across all GPUs, but it does not
create request-level batching. JSON-schema constrained decoding also adds
guided-decoding overhead. Current GPU status confirms all 4 L40S GPUs at
100 percent utilization with about 42.8 GB allocated per GPU.
```

Completed-slice integrity checks:

```text
Mistral no-oracle pass rate: 100 percent
Qwen no-oracle pass rate: 100 percent
Llama no-oracle pass rate: 100 percent
Gemma no-oracle pass rate: 100 percent
Mistral unresolved abstraction warnings: 0
Qwen unresolved abstraction warnings: 0
Llama unresolved abstraction warnings: 0
Gemma unresolved abstraction warnings: 0
Mistral local cost: $0
Qwen local cost: $0
Llama local cost: $0
Gemma local cost: $0
```

Quality note: Mistral's post-fix full slice is parser-clean for the paper-grade
criterion, with no repaired fallback. Qwen's full slice has zero episode
failures but 42/5,376 audited repaired-fallback proposals. Keep this visible
in the analysis. Spot checks show readable but truncated/verbose JSON that did
not expose a parseable action field before the 192-token budget ended. Decide
after all four slices finish whether to accept this small audited fallback rate
or rerun Qwen under a new versioned config with a smaller schema or larger
token budget. Do not change defaults mid-queue, because that would break equal
treatment for the remaining models.

Recommended Step 2b full restart command. These values are now the queue
defaults, but they are shown explicitly for reproducibility and so old pre-fix
artifacts cannot be aggregated accidentally:

```bash
cd /home/ubuntu/nachiket/CommitBench
JOB_ID=local_open_main_mc_postfix_$(date -u +%Y%m%dT%H%M%SZ) \
QUEUE_MODELS="mistral_small_3_2_24b_local qwen3_6_35b_a3b_local llama3_3_70b_awq_local gemma3_27b_it_local" \
OVERWRITE_OUTPUTS=1 \
QUEUE_MODEL_TP=4 \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
SLICE_LIMIT=5376 \
OUTPUT_PREFIX=main_mc_postfix \
SPLIT_PREFIX=main_mc_postfix \
REPORT_PREFIX=main_mc_postfix \
MODEL_CONTROLS_POLICY=1 \
MODEL_PROPOSAL_MODE=actions \
ROW_SELECTION_STRATEGY=first \
setsid -f bash -c 'exec bash effectbench_omega/scripts/run_local_open_queue.sh \
  > effectbench_omega/jobs/local_open_queue_launch.log 2>&1'
```

Monitor:

```bash
cd /home/ubuntu/nachiket/CommitBench
bash effectbench_omega/scripts/show_local_open_queue_status.sh
tail -f effectbench_omega/jobs/local_open_latest/events.tsv
tail -f effectbench_omega/jobs/local_open_latest/logs/mistral_small_3_2_24b_local_run_online.log
nvidia-smi
```

Expected per-model output directories for the post-fix restart command:

```text
effectbench_omega/outputs/main_mc_postfix_mistral_small_3_2_24b_local
effectbench_omega/outputs/main_mc_postfix_qwen3_6_35b_a3b_local
effectbench_omega/outputs/main_mc_postfix_llama3_3_70b_awq_local
effectbench_omega/outputs/main_mc_postfix_gemma3_27b_it_local
```

## Stage 3: Offline Analyses

All four Stage 2b slices finished and each per-slice verifier/no-oracle/cost
check passed. Stage 3 merge completed:

```text
merged_output: effectbench_omega/outputs/main_mc_postfix_all_local
trace_count: 21,504
api_logs_lines: 21,504
failure_count: 0
models_merged: 4
merge_summary: effectbench_omega/outputs/main_mc_postfix_all_local/merge_summary.json
```

Merge command used:

```bash
cd /home/ubuntu/nachiket/CommitBench
.venv/bin/python effectbench_omega/scripts/merge_local_open_slices.py \
  --input-prefix effectbench_omega/outputs/main_mc_postfix \
  --out effectbench_omega/outputs/main_mc_postfix_all_local
```

Offline suite command used:

```bash
cd /home/ubuntu/nachiket/CommitBench
SPLIT=main_mc_postfix_all_local bash effectbench_omega/scripts/run_stage3_offline.sh
```

Hardened Stage 3 offline suite completed:

```text
job_id: stage3_hardened_main_mc_postfix_all_local_20260623T220316Z
completed_utc: 2026-06-23T22:07:56Z
verifier_certificates: 21,504
verifier_strict_excess: 5,149
verifier_minimal: 16,355
unresolved_abstraction_warnings: 0
no_oracle_rows_checked: 21,504
no_oracle_failures: 0
certificate_replay_bundles_checked: 160
certificate_replay_failures: 0
local_request_count: 21,504
local_cost_usd: 0.0
figure_files: 6
claim_registry_rows: 50
no_oracle_pytest: passed
```

Hardened metric replacements:

```text
projection_loss: data-derived accept/reject predicates over action order,
  permissions, contract/menu checks, revisability, target confirmation, and
  parser fallback status; reason table emitted.
bootstrap: paired unit, base-task cluster, and hierarchical family/base-task
  bootstrap over task/model/seed paired system differences, 2,000 resamples.
CEGAR: reduced abstract-state hash collision audit; reports only omitted fields
  that actually collapse distinct full states into different verifier labels.
guard_tie: paired PROJ_GUARD/EFFECTGUARD action/effect/verdict audit.
aggregate: paper-facing CSV tables, PNG/PDF figures, and a lite source-linked
  claim registry.
```

Key Stage 3 outputs:

```text
effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet
effectbench_omega/outputs/main_mc_postfix_all_local/kernel/frontiers.parquet
effectbench_omega/outputs/main_mc_postfix_all_local/kernel/prune_log.parquet
effectbench_omega/outputs/main_mc_postfix_all_local/kernel/rejected_abstractions.parquet
effectbench_omega/tables/no_oracle_main_mc_postfix_all_local.csv
effectbench_omega/tables/projection_loss_main_mc_postfix_all_local.csv
effectbench_omega/tables/projection_loss_main_mc_postfix_all_local_reasons.csv
effectbench_omega/tables/cegar_rejections_main_mc_postfix_all_local.csv
effectbench_omega/tables/cegar_label_changes_main_mc_postfix_all_local.csv
effectbench_omega/tables/lattice_sensitivity_main_mc_postfix_all_local.csv
effectbench_omega/tables/uncertainty_main_mc_postfix_all_local.csv
effectbench_omega/tables/guard_tie_main_mc_postfix_all_local.csv
effectbench_omega/tables/guard_tie_main_mc_postfix_all_local_details.csv
effectbench_omega/tables/guard_tie_main_mc_postfix_all_local.md
effectbench_omega/tables/main_mc_postfix_all_local/main_family_results.csv
effectbench_omega/tables/main_mc_postfix_all_local/online_control_main.csv
effectbench_omega/figures/main_mc_postfix_all_local/online_control_outcomes.{png,pdf}
effectbench_omega/figures/main_mc_postfix_all_local/projection_loss.{png,pdf}
effectbench_omega/figures/main_mc_postfix_all_local/strict_excess_family_regime.{png,pdf}
effectbench_omega/witness_bundles/main_mc_postfix_all_local/
effectbench_omega/reports/certificate_replay_main_mc_postfix_all_local.md
effectbench_omega/reports/main_mc_postfix_all_local_cost.md
effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv
```

Main aggregate sanity from current scaffolded tables:

```text
overall_strict_excess_rate: 5,149 / 21,504 = 23.94 percent
BASE strict_excess_rate: 57.00 percent
PROJ_GUARD strict_excess_rate: 7.44 percent
EFFECTGUARD strict_excess_rate: 7.39 percent
raw_success: 100 percent for all systems in current local adapters
```

Hardened uncertainty summary:

```text
BASE raw-minus-kernel gap: 0.5700
  paired 95% CI: [0.5586, 0.5815]
  task-cluster 95% CI: [0.5515, 0.5872]
  hierarchical 95% CI: [0.4823, 0.6183]
BASE strict minus PROJ_GUARD strict: 0.4957
  paired 95% CI: [0.4813, 0.5103]
  task-cluster 95% CI: [0.4700, 0.5207]
  hierarchical 95% CI: [0.3703, 0.5699]
PROJ_GUARD strict minus EFFECTGUARD strict: 0.000419
  paired 95% CI: [0.0000, 0.00098]
  task-cluster 95% CI: [0.0000, 0.00112]
  hierarchical 95% CI: [0.0000, 0.00144]
```

Hardened projection summary:

```text
FINAL_STATE residual strict excess: 23.94 percent of accepted successes
CORE_DFA residual strict excess: 23.94 percent
MINISCOPE_PERMISSION residual strict excess: 21.29 percent
CONTRACT_MENU_CMTF residual strict excess: 21.68 percent
REVISABILITY residual strict excess: 21.29 percent
MODERNSTACK_PROJECTION residual strict excess: 21.88 percent
KERNEL_FULL residual strict excess: 0 percent
```

Hardened CEGAR summary:

```text
outbox omission: 95 label-changing reduced-state collisions, 4,618 affected rows
memory_cache omission: 146 collisions, 10,713 affected rows
user_visible_exposure omission: 213 collisions, 19,084 affected rows
policy_obligation, contract_artifact_hash, virtual_clock, and
compensation_or_payment_hold produced no label-changing collisions under the
currently available local scaffold fields.
```

This is a conservative-audit strength when written carefully: the checker only
rejects omitted fields when the current scaffold shows label-changing
reduced-state collisions. It should not be written as proof that zero-collision
fields are universally irrelevant.

PROJ_GUARD vs EFFECTGUARD tie audit:

```text
paired_units: 7,168
same_effect_vector_rate: 99.958 percent
same_verdict_rate: 99.958 percent
verdict_diff_units: 3
proj_strict_rate: 7.4358 percent
effect_strict_rate: 7.3940 percent
proj_minus_effect_strict_rate: 0.0419 percentage points
```

The only verdict differences are three Mistral telecom
`shared_agent_confirmation` / `confirm_target_before_write` units where
PROJ_GUARD executed `commit_high` and EFFECTGUARD substituted `commit_low` or
`draft_change -> commit_low`. The near-tie is therefore implementation-driven:
the current PROJ_GUARD already contains most of the same one-step lower-effect
substitutions, and EFFECTGUARD's extra suffix-feasibility logic only has room
to improve a tiny set of cases in this local scaffold.

Historical explicit command sequence, equivalent to the driver:

```bash
.venv/bin/python effectbench_omega/effectbench/kernel/verifier.py \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --schemas effectbench_omega/schemas \
  --out effectbench_omega/outputs/main_mc_postfix_all_local/kernel

.venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
  --runtime-logs effectbench_omega/outputs/main_mc_postfix_all_local/runtime_logs.parquet \
  --out effectbench_omega/tables/no_oracle_main_mc_postfix_all_local.csv

.venv/bin/python effectbench_omega/effectbench/baselines/project.py \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --baselines FINAL_STATE CORE_DFA MINISCOPE_PERMISSION CONTRACT_MENU_CMTF REVISABILITY MODERNSTACK_PROJECTION KERNEL_FULL \
  --out effectbench_omega/tables/projection_loss_main_mc_postfix_all_local.csv

.venv/bin/python effectbench_omega/effectbench/audit/cegar.py \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --schemas effectbench_omega/schemas \
  --omit-fields outbox policy_obligation contract_artifact_hash virtual_clock memory_cache user_visible_exposure compensation_or_payment_hold \
  --out effectbench_omega/tables/cegar_rejections_main_mc_postfix_all_local.csv \
  --label-changes effectbench_omega/tables/cegar_label_changes_main_mc_postfix_all_local.csv

.venv/bin/python effectbench_omega/effectbench/metrics/lattice_sensitivity.py \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --lattices effectbench_omega/configs/lattices \
  --out effectbench_omega/tables/lattice_sensitivity_main_mc_postfix_all_local.csv

.venv/bin/python effectbench_omega/effectbench/metrics/bootstrap.py \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --group-by task_id model seed family \
  --methods paired_bootstrap task_cluster hierarchical \
  --out effectbench_omega/tables/uncertainty_main_mc_postfix_all_local.csv \
  --n-bootstrap 2000 \
  --seed 13

.venv/bin/python effectbench_omega/effectbench/audit/guard_tie.py \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --out effectbench_omega/tables/guard_tie_main_mc_postfix_all_local.csv \
  --details-out effectbench_omega/tables/guard_tie_main_mc_postfix_all_local_details.csv

.venv/bin/python effectbench_omega/effectbench/audit/replay_bundles.py \
  --certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --traces effectbench_omega/outputs/main_mc_postfix_all_local/traces.parquet \
  --sample strict_excess=100 minimal=60 incomparable=60 necessary_high=30 \
  --out effectbench_omega/witness_bundles/main_mc_postfix_all_local

.venv/bin/python effectbench_omega/effectbench/audit/replay_certificates.py \
  --bundle-dir effectbench_omega/witness_bundles/main_mc_postfix_all_local \
  --out effectbench_omega/reports/certificate_replay_main_mc_postfix_all_local.md \
  --strict

.venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
  --logs effectbench_omega/outputs/main_mc_postfix_all_local/api_logs.jsonl \
  --out effectbench_omega/reports/main_mc_postfix_all_local_cost.md \
  --final

.venv/bin/python effectbench_omega/effectbench/metrics/aggregate.py \
  --main-certificates effectbench_omega/outputs/main_mc_postfix_all_local/kernel/certificates.parquet \
  --projection-loss effectbench_omega/tables/projection_loss_main_mc_postfix_all_local.csv \
  --cost-logs effectbench_omega/outputs/main_mc_postfix_all_local/api_logs.jsonl \
  --out-tables effectbench_omega/tables/main_mc_postfix_all_local \
  --out-figures effectbench_omega/figures/main_mc_postfix_all_local \
  --claim-registry effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv
```

Stage 3 caveat/strength boundary: the projection/bootstrap/CEGAR modules are
now data-derived and replayable over the merged certificates. They are still
simulator-local audits, not external human audits. The CEGAR audit can only test
fields represented in the current local trace abstraction, so no-collision
fields should be read as "not exercised by this scaffold" rather than "never
future-relevant."

Stage 3 checklist:

```text
kernel verifier
projection-loss baselines
no-oracle audit
CEGAR audit
lattice sensitivity
bootstrap uncertainty
certificate replay bundles
aggregate tables/figures
claim registry check, currently 50 rows
```

## Paper Claim

Use:

> Across reproducible open-weight tool agents, final-state success substantially overstates certified least-effect success. Projected safeguards reduce but do not eliminate residual strict excess, and EffectGuard reduces excess without oracle access.

Do not use:

```text
frontier model coverage
commercial model comparison
GPT/Claude/Gemini/Bedrock generality
SOTA frontier leaderboard
```
