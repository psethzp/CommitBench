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
| Stage 2b model-controlled queue | Ready, not running | Old `local_open_main_mc_20260622T161747Z` was stopped before Qwen/Llama/Gemma; restart with the post-fix command below |

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
server_ready_utc: 2026-06-22T21:50:59Z
current_model: mistral_small_3_2_24b_local
current_status: running_slice
current_output: effectbench_omega/outputs/main_mc_postfix_mistral_small_3_2_24b_local
last_checked_utc: 2026-06-22T21:51:40Z
invalid_old_job_id: local_open_main_mc_20260622T161747Z, stopped before Qwen/Llama/Gemma due pre-fix Mistral serving
```

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

After all four model slices finish, concatenate or aggregate their trace/certificate outputs, then run:

```text
kernel verifier
projection-loss baselines
no-oracle audit
CEGAR audit
lattice sensitivity
bootstrap uncertainty
certificate replay bundles
aggregate tables/figures
claim registry check
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
