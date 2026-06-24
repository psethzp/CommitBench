#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

PORT="${LOCAL_MODEL_PORT:-8001}"
BASE_URL="http://localhost:${PORT}/v1"
MODEL_TP="${STAGE3_MODEL_TP:-4}"
SMOKE_LIMIT="${STAGE3_SMOKE_LIMIT:-14}"
OUTPUT_PREFIX="${STAGE3_OUTPUT_PREFIX:-stage3_v2_smoke}"
SPLIT_PREFIX="${STAGE3_SPLIT_PREFIX:-stage3_v2_smoke}"
JOB_ID="${JOB_ID:-stage3_v2_smoke_$(date -u +%Y%m%dT%H%M%SZ)}"
JOB_DIR="effectbench_omega/jobs/${JOB_ID}"
LOG_DIR="${JOB_DIR}/logs"
SUMMARY_DIR="${JOB_DIR}/summaries"
EVENTS="${JOB_DIR}/events.tsv"
QWEN_REPAIR_MANIFEST="${QWEN_REPAIR_MANIFEST:-effectbench_omega/manifests/qwen_repair_rows.csv}"
QWEN_REPAIR_OUT="${QWEN_REPAIR_OUT:-effectbench_omega/outputs/qwen_repair_sensitivity_rerun}"
RUN_QWEN_REPAIR="${RUN_QWEN_REPAIR:-1}"
CURRENT_MODEL="queue"

if [[ -n "${STAGE3_MODELS:-}" ]]; then
  read -r -a MODELS <<<"${STAGE3_MODELS}"
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
ln -sfn "${JOB_ID}" effectbench_omega/jobs/stage3_v2_latest

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
}

wait_for_server() {
  local model="$1"
  local server_pid="$2"
  local log_file="$3"
  local waited=0
  local model_list="/tmp/effectbench_stage3_models_${PORT}.json"
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
        {"role": "user", "content": "Stage 3 V2 health smoke."},
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

run_v2_smoke() {
  local model="$1"
  local out_dir="effectbench_omega/outputs/${OUTPUT_PREFIX}_${model}"
  local run_log="${LOG_DIR}/${model}_v2_smoke_run_online.log"
  local verifier_log="${LOG_DIR}/${model}_v2_smoke_verifier.log"
  local no_oracle_log="${LOG_DIR}/${model}_v2_smoke_no_oracle.log"
  local cost_log="${LOG_DIR}/${model}_v2_smoke_cost.log"
  local summary_json="${SUMMARY_DIR}/${model}_v2_smoke.json"

  if [[ -e "${out_dir}" && "${OVERWRITE_OUTPUTS:-0}" != "1" ]]; then
    event "${model}" "failed" "${out_dir} already exists; set OVERWRITE_OUTPUTS=1 to rerun"
    return 1
  fi
  if [[ "${OVERWRITE_OUTPUTS:-0}" == "1" ]]; then
    rm -rf "${out_dir}"
  fi

  event "${model}" "running_v2_smoke" "writing ${SMOKE_LIMIT} V2 smoke trajectories to ${out_dir}"
  .venv/bin/python effectbench_omega/scripts/run_online.py \
    --config effectbench_omega/configs/local_open.yaml \
    --manifest effectbench_omega/manifests/tasks_guard_v2_local.csv \
    --split "${SPLIT_PREFIX}_${model}" \
    --systems PROJ_GUARD_V2 EFFECTGUARD_V2 \
    --models "${model}" \
    --regimes FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT \
    --out "${out_dir}" \
    --limit "${SMOKE_LIMIT}" \
    --selection-strategy balanced_regime_system \
    --call-local-model \
    --local-base-url "${BASE_URL}" \
    --local-served-model "${model}" \
    --model-controls-policy \
    --model-proposal-mode actions \
    >"${run_log}" 2>&1

  .venv/bin/python effectbench_omega/effectbench/kernel/verifier.py \
    --traces "${out_dir}/traces.parquet" \
    --schemas effectbench_omega/schemas \
    --out "${out_dir}/kernel" \
    >"${verifier_log}" 2>&1
  .venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${out_dir}/runtime_logs.parquet" \
    --out "effectbench_omega/reports/${OUTPUT_PREFIX}_${model}_no_oracle.json" \
    >"${no_oracle_log}" 2>&1
  .venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${out_dir}/api_logs.jsonl" \
    --out "effectbench_omega/reports/${OUTPUT_PREFIX}_${model}_cost.json" \
    >"${cost_log}" 2>&1

  .venv/bin/python - "${model}" "${out_dir}" "${summary_json}" <<'PY'
import json
import sys
from pathlib import Path
import pandas as pd

model, out_dir, summary_json = sys.argv[1:4]
out = Path(out_dir)
traces = pd.read_parquet(out / "traces.parquet")
verifier = json.loads((out / "kernel" / "verifier_summary.json").read_text())
api_count = sum(1 for line in (out / "api_logs.jsonl").open() if line.strip())
failure_count = sum(1 for line in (out / "failures.jsonl").open() if line.strip())
payload = {
    "model": model,
    "out_dir": out_dir,
    "trace_count": int(len(traces)),
    "certificate_count": verifier.get("certificate_count"),
    "strict_excess_count": verifier.get("strict_excess_count"),
    "minimal_count": verifier.get("minimal_count"),
    "api_log_count": api_count,
    "failure_count": failure_count,
    "parse_status_counts": traces["model_proposal_parse_status"].value_counts().sort_index().to_dict(),
    "repair_nonempty_rows": int(traces["model_proposal_repair_log"].astype(str).ne("[]").sum()),
}
Path(summary_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(payload, sort_keys=True))
PY

  local failure_count
  failure_count="$(awk 'NF { count += 1 } END { print count + 0 }' "${out_dir}/failures.jsonl")"
  if (( failure_count > 0 )); then
    event "${model}" "failed" "V2 smoke recorded ${failure_count} failures; see ${out_dir}/failures.jsonl"
    return 1
  fi
  event "${model}" "v2_smoke_done" "summary ${summary_json}"
}

run_qwen_repair() {
  local model="qwen3_6_35b_a3b_local"
  local run_log="${LOG_DIR}/${model}_repair_sensitivity_run_online.log"
  local no_oracle_log="${LOG_DIR}/${model}_repair_sensitivity_no_oracle.log"
  local cost_log="${LOG_DIR}/${model}_repair_sensitivity_cost.log"
  local repair_count
  repair_count="$(.venv/bin/python - "${QWEN_REPAIR_MANIFEST}" <<'PY'
import sys
import pandas as pd
print(len(pd.read_csv(sys.argv[1], dtype=str)))
PY
)"

  if [[ -e "${QWEN_REPAIR_OUT}" && "${OVERWRITE_OUTPUTS:-0}" != "1" ]]; then
    event "${model}" "failed" "${QWEN_REPAIR_OUT} already exists; set OVERWRITE_OUTPUTS=1 to rerun"
    return 1
  fi
  if [[ "${OVERWRITE_OUTPUTS:-0}" == "1" ]]; then
    rm -rf "${QWEN_REPAIR_OUT}"
  fi

  event "${model}" "running_qwen_repair_sensitivity" "rerunning ${repair_count} same-prompt affected Qwen rows"
  .venv/bin/python effectbench_omega/scripts/run_online.py \
    --config effectbench_omega/configs/local_open.yaml \
    --manifest "${QWEN_REPAIR_MANIFEST}" \
    --split "main_mc_postfix_qwen3_6_35b_a3b_local" \
    --systems BASE PROJ_GUARD EFFECTGUARD \
    --models "${model}" \
    --regimes FULL CONCAT SHARDED SNOWBALL REVISE MEMORY_REVISE ADV_EFFECT \
    --out "${QWEN_REPAIR_OUT}" \
    --limit "${repair_count}" \
    --selection-strategy first \
    --call-local-model \
    --local-base-url "${BASE_URL}" \
    --local-served-model "${model}" \
    --model-controls-policy \
    --model-proposal-mode actions \
    >"${run_log}" 2>&1

  .venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${QWEN_REPAIR_OUT}/runtime_logs.parquet" \
    --out "effectbench_omega/reports/qwen_repair_sensitivity_no_oracle.json" \
    >"${no_oracle_log}" 2>&1
  .venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${QWEN_REPAIR_OUT}/api_logs.jsonl" \
    --out "effectbench_omega/reports/qwen_repair_sensitivity_cost.json" \
    >"${cost_log}" 2>&1
  event "${model}" "qwen_repair_sensitivity_done" "rerun output ${QWEN_REPAIR_OUT}"
}

main() {
  printf "timestamp\tmodel\tstatus\tdetail\n" >"${EVENTS}"
  printf "%s\n" "$$" >"${JOB_DIR}/queue.pid"
  {
    echo "job_id=${JOB_ID}"
    echo "port=${PORT}"
    echo "base_url=${BASE_URL}"
    echo "model_tp=${MODEL_TP}"
    echo "smoke_limit=${SMOKE_LIMIT}"
    echo "run_qwen_repair=${RUN_QWEN_REPAIR}"
    echo "qwen_repair_manifest=${QWEN_REPAIR_MANIFEST}"
    echo "qwen_repair_out=${QWEN_REPAIR_OUT}"
    echo "cuda_visible_devices=${CUDA_VISIBLE_DEVICES}"
    echo "order=${MODELS[*]}"
  } >"${JOB_DIR}/job.env"

  .venv/bin/python effectbench_omega/scripts/install_mistral_vllm_shim.py >"${LOG_DIR}/install_mistral_vllm_shim.log" 2>&1
  if [[ "${RUN_QWEN_REPAIR}" == "1" ]]; then
    .venv/bin/python effectbench_omega/scripts/qwen_repair_sensitivity.py prepare \
      --manifest-out "${QWEN_REPAIR_MANIFEST}" \
      --summary-out "effectbench_omega/reports/qwen_repair_manifest_summary.json" \
      >"${LOG_DIR}/qwen_repair_prepare.log" 2>&1
  fi

  event "queue" "started" "Stage 3 V2 smokes: ${MODELS[*]}"
  stop_server
  trap 'rc=$?; if (( rc != 0 )); then event "${CURRENT_MODEL:-queue}" "failed" "stage3 supervisor exited rc=${rc}"; fi; stop_server' EXIT

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
    run_v2_smoke "${model}"
    if [[ "${model}" == "qwen3_6_35b_a3b_local" && "${RUN_QWEN_REPAIR}" == "1" ]]; then
      run_qwen_repair
    fi
    event "${model}" "stopping_server" "stopping vLLM before next model"
    stop_server
  done

  if [[ "${RUN_QWEN_REPAIR}" == "1" ]]; then
    event "qwen_repair" "reporting" "building merged sensitivity split and report"
    .venv/bin/python effectbench_omega/scripts/qwen_repair_sensitivity.py report \
      >"${LOG_DIR}/qwen_repair_report.log" 2>&1
  fi

  event "queue" "done" "Stage 3 V2 smoke queue complete"
}

main "$@"
