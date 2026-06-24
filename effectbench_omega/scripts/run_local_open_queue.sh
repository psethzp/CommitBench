#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

PORT="${LOCAL_MODEL_PORT:-8001}"
BASE_URL="http://localhost:${PORT}/v1"
MODEL_TP="${QUEUE_MODEL_TP:-4}"
SLICE_LIMIT="${SLICE_LIMIT:-5376}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-main_mc_postfix}"
SPLIT_PREFIX="${SPLIT_PREFIX:-${OUTPUT_PREFIX}}"
REPORT_PREFIX="${REPORT_PREFIX:-${OUTPUT_PREFIX}}"
MODEL_CONTROLS_POLICY="${MODEL_CONTROLS_POLICY:-1}"
MODEL_PROPOSAL_MODE="${MODEL_PROPOSAL_MODE:-actions}"
ROW_SELECTION_STRATEGY="${ROW_SELECTION_STRATEGY:-first}"
MANIFEST="${MANIFEST:-effectbench_omega/manifests/tasks_local_open.csv}"
CONFIG="${CONFIG:-effectbench_omega/configs/local_open.yaml}"
QUEUE_SYSTEMS="${QUEUE_SYSTEMS:-BASE PROJ_GUARD EFFECTGUARD}"
QUEUE_REGIMES="${QUEUE_REGIMES:-FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT}"
JOB_ID="${JOB_ID:-local_open_$(date -u +%Y%m%dT%H%M%SZ)}"
JOBS_DIR="effectbench_omega/jobs"
JOB_DIR="${JOBS_DIR}/${JOB_ID}"
LOG_DIR="${JOB_DIR}/logs"
SUMMARY_DIR="${JOB_DIR}/summaries"
EVENTS="${JOB_DIR}/events.tsv"
CURRENT_MODEL="queue"

if [[ -n "${QUEUE_MODELS:-}" ]]; then
  read -r -a MODELS <<<"${QUEUE_MODELS}"
else
  MODELS=(
    "mistral_small_3_2_24b_local"
    "qwen3_6_35b_a3b_local"
    "llama3_3_70b_awq_local"
    "gemma3_27b_it_local"
  )
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"

mkdir -p "${LOG_DIR}" "${SUMMARY_DIR}"
ln -sfn "${JOB_ID}" "${JOBS_DIR}/local_open_latest"

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

event() {
  local model="$1"
  local status="$2"
  local detail="$3"
  printf "%s\t%s\t%s\t%s\n" "$(timestamp)" "${model}" "${status}" "${detail}" >>"${EVENTS}"
  printf "%s\n" "${model}" >"${JOB_DIR}/current_model"
  printf "%s\n" "${status}" >"${JOB_DIR}/current_status"
  printf "%s\n" "${detail}" >"${JOB_DIR}/current_detail"
}

stop_server() {
  local pids
  pids="$(pgrep -f 'python -m [v]llm.entrypoints.openai.api_server' || true)"
  if [[ -n "${pids}" ]]; then
    kill -TERM ${pids} 2>/dev/null || true
  fi
  pids="$(pgrep -f 'VLLM::Worker' || true)"
  if [[ -n "${pids}" ]]; then
    kill -TERM ${pids} 2>/dev/null || true
  fi
  pids="$(pgrep -f 'from multiprocessing.resource_tracker import main' || true)"
  if [[ -n "${pids}" ]]; then
    kill -TERM ${pids} 2>/dev/null || true
  fi
  sleep 5
  pids="$(pgrep -f 'python -m [v]llm.entrypoints.openai.api_server' || true)"
  if [[ -n "${pids}" ]]; then
    kill -KILL ${pids} 2>/dev/null || true
  fi
  pids="$(pgrep -f 'VLLM::Worker' || true)"
  if [[ -n "${pids}" ]]; then
    kill -KILL ${pids} 2>/dev/null || true
  fi
  pids="$(pgrep -f 'from multiprocessing.resource_tracker import main' || true)"
  if [[ -n "${pids}" ]]; then
    kill -KILL ${pids} 2>/dev/null || true
  fi
}

wait_for_server() {
  local model="$1"
  local server_pid="$2"
  local log_file="$3"
  local waited=0
  local model_list="/tmp/effectbench_models_${PORT}.json"
  while (( waited < 1800 )); do
    if ! kill -0 "${server_pid}" 2>/dev/null; then
      event "${model}" "failed" "vLLM exited while loading; see ${log_file}"
      tail -160 "${log_file}" >&2 || true
      return 1
    fi
    if curl -fsS "${BASE_URL}/models" >"${model_list}" 2>/dev/null; then
      if grep -q "${model}" "${model_list}"; then
        event "${model}" "server_ready" "vLLM ready on ${BASE_URL}; TP=${MODEL_TP}; CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
        return 0
      fi
    fi
    sleep 10
    waited=$((waited + 10))
    event "${model}" "loading" "waited ${waited}s for vLLM"
  done
  event "${model}" "failed" "timed out waiting for vLLM; see ${log_file}"
  tail -160 "${log_file}" >&2 || true
  return 1
}

endpoint_smoke() {
  local model="$1"
  local out_json="${JOB_DIR}/${model}_endpoint_smoke.json"
  .venv/bin/python - "${model}" "${BASE_URL}" "${out_json}" <<'PY'
import json
import sys
import time
from openai import OpenAI

model, base_url, out_json = sys.argv[1:4]
client = OpenAI(base_url=base_url, api_key="local")
start = time.time()
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "Reply with exactly one token: LOW"},
        {"role": "user", "content": "Queue health smoke."},
    ],
    temperature=0,
    max_tokens=8,
)
payload = {
    "model": model,
    "status": "ok",
    "latency_s": round(time.time() - start, 3),
    "response_id": response.id,
    "content": response.choices[0].message.content,
}
with open(out_json, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
print(json.dumps(payload, sort_keys=True))
PY
}

run_slice() {
  local model="$1"
  CURRENT_MODEL="${model}"
  local out_dir="effectbench_omega/outputs/${OUTPUT_PREFIX}_${model}"
  local run_log="${LOG_DIR}/${model}_run_online.log"
  local verifier_log="${LOG_DIR}/${model}_verifier.log"
  local no_oracle_log="${LOG_DIR}/${model}_no_oracle.log"
  local cost_log="${LOG_DIR}/${model}_cost.log"
  local summary_json="${SUMMARY_DIR}/${model}.json"
  local extra_args=()
  local systems=()
  local regimes=()

  if [[ "${MODEL_CONTROLS_POLICY}" == "1" ]]; then
    extra_args+=(--model-controls-policy --model-proposal-mode "${MODEL_PROPOSAL_MODE}")
  fi
  read -r -a systems <<<"${QUEUE_SYSTEMS}"
  read -r -a regimes <<<"${QUEUE_REGIMES}"

  if [[ -e "${out_dir}" && "${OVERWRITE_OUTPUTS:-0}" != "1" ]]; then
    event "${model}" "failed" "${out_dir} already exists; set OVERWRITE_OUTPUTS=1 to rerun"
    return 1
  fi
  if [[ "${OVERWRITE_OUTPUTS:-0}" == "1" ]]; then
    rm -rf "${out_dir}"
  fi

  event "${model}" "running_slice" "writing ${SLICE_LIMIT} trajectories to ${out_dir}"
  .venv/bin/python effectbench_omega/scripts/run_online.py \
    --config "${CONFIG}" \
    --manifest "${MANIFEST}" \
    --split "${SPLIT_PREFIX}_${model}" \
    --systems "${systems[@]}" \
    --models "${model}" \
    --regimes "${regimes[@]}" \
    --out "${out_dir}" \
    --limit "${SLICE_LIMIT}" \
    --selection-strategy "${ROW_SELECTION_STRATEGY}" \
    --call-local-model \
    --local-base-url "${BASE_URL}" \
    "${extra_args[@]}" \
    >"${run_log}" 2>&1

  event "${model}" "verifying" "run_online finished; running kernel/no-oracle/cost checks"
  .venv/bin/python effectbench_omega/effectbench/kernel/verifier.py \
    --traces "${out_dir}/traces.parquet" \
    --schemas effectbench_omega/schemas \
    --out "${out_dir}/kernel" \
    >"${verifier_log}" 2>&1
  .venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${out_dir}/runtime_logs.parquet" \
    --out "effectbench_omega/reports/${REPORT_PREFIX}_${model}_no_oracle.md" \
    >"${no_oracle_log}" 2>&1
  .venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${out_dir}/api_logs.jsonl" \
    --out "effectbench_omega/reports/${REPORT_PREFIX}_${model}_cost.md" \
    >"${cost_log}" 2>&1

  .venv/bin/python - "${model}" "${out_dir}" "${summary_json}" <<'PY'
import json
import sys
from pathlib import Path

model, out_dir, summary_json = sys.argv[1:4]
out = Path(out_dir)
verifier = json.loads((out / "kernel" / "verifier_summary.json").read_text())
api_count = sum(1 for line in (out / "api_logs.jsonl").open() if line.strip())
failure_count = sum(1 for line in (out / "failures.jsonl").open() if line.strip())
payload = {
    "model": model,
    "out_dir": out_dir,
    "trace_count": verifier.get("trace_count"),
    "certificate_count": verifier.get("certificate_count"),
    "minimal_count": verifier.get("minimal_count"),
    "strict_excess_count": verifier.get("strict_excess_count"),
    "unresolved_abstraction_warnings": verifier.get("unresolved_abstraction_warnings"),
    "verifier_p95_latency_ms": verifier.get("verifier_p95_latency_ms"),
    "api_log_count": api_count,
    "failure_count": failure_count,
}
Path(summary_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(payload, sort_keys=True))
PY

  local failure_count
  failure_count="$(awk 'NF { count += 1 } END { print count + 0 }' "${out_dir}/failures.jsonl")"
  if (( failure_count > 0 )); then
    event "${model}" "failed" "slice recorded ${failure_count} failures; see ${out_dir}/failures.jsonl"
    return 1
  fi

  event "${model}" "done" "slice complete; summary ${summary_json}"
}

main() {
  printf "timestamp\tmodel\tstatus\tdetail\n" >"${EVENTS}"
  printf "%s\n" "$$" >"${JOB_DIR}/queue.pid"
  {
    echo "job_id=${JOB_ID}"
    echo "root=${ROOT_DIR}"
    echo "port=${PORT}"
    echo "base_url=${BASE_URL}"
    echo "model_tp=${MODEL_TP}"
    echo "slice_limit=${SLICE_LIMIT}"
    echo "output_prefix=${OUTPUT_PREFIX}"
    echo "split_prefix=${SPLIT_PREFIX}"
    echo "report_prefix=${REPORT_PREFIX}"
    echo "config=${CONFIG}"
    echo "manifest=${MANIFEST}"
    echo "systems=${QUEUE_SYSTEMS}"
    echo "regimes=${QUEUE_REGIMES}"
    echo "model_controls_policy=${MODEL_CONTROLS_POLICY}"
    echo "model_proposal_mode=${MODEL_PROPOSAL_MODE}"
    echo "row_selection_strategy=${ROW_SELECTION_STRATEGY}"
    echo "cuda_visible_devices=${CUDA_VISIBLE_DEVICES}"
    echo "order=${MODELS[*]}"
  } >"${JOB_DIR}/job.env"

  .venv/bin/python effectbench_omega/scripts/install_mistral_vllm_shim.py >"${LOG_DIR}/install_mistral_vllm_shim.log" 2>&1

  event "queue" "started" "ordered run: ${MODELS[*]}"
  stop_server
  trap 'rc=$?; if (( rc != 0 )); then event "${CURRENT_MODEL:-queue}" "failed" "queue supervisor exited rc=${rc}"; fi; stop_server' EXIT

  for model in "${MODELS[@]}"; do
    CURRENT_MODEL="${model}"
    local vllm_log="${LOG_DIR}/${model}_vllm.log"
    event "${model}" "launching" "starting vLLM with TP=${MODEL_TP} on GPUs ${CUDA_VISIBLE_DEVICES}; log ${vllm_log}"
    LOCAL_MODEL="${model}" LOCAL_MODEL_TP="${MODEL_TP}" LOCAL_MODEL_PORT="${PORT}" \
      bash effectbench_omega/scripts/launch_local_model.sh >"${vllm_log}" 2>&1 &
    local server_pid=$!
    printf "%s\n" "${server_pid}" >"${JOB_DIR}/${model}_vllm.pid"
    wait_for_server "${model}" "${server_pid}" "${vllm_log}"
    event "${model}" "endpoint_smoke" "health smoke against ${BASE_URL}"
    endpoint_smoke "${model}" >>"${LOG_DIR}/${model}_endpoint_smoke.log" 2>&1
    run_slice "${model}"
    event "${model}" "stopping_server" "stopping vLLM before next model"
    stop_server
  done

  event "queue" "done" "all model slices complete"
}

main "$@"
