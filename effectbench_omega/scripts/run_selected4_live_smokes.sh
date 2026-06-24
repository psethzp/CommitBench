#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

PORT="${LOCAL_MODEL_PORT:-8001}"
BASE_URL="http://localhost:${PORT}/v1"
MODELS=(
  "mistral_small_3_2_24b_local"
  "qwen3_6_35b_a3b_local"
  "gemma3_27b_it_local"
  "llama3_3_70b_awq_local"
)

mkdir -p effectbench_omega/reports/live_smokes

stop_server() {
  local pids
  pids="$(pgrep -f 'python -m [v]llm.entrypoints.openai.api_server' || true)"
  if [[ -n "${pids}" ]]; then
    kill -TERM ${pids} 2>/dev/null || true
  fi
  sleep 5
  pids="$(pgrep -f 'python -m [v]llm.entrypoints.openai.api_server' || true)"
  if [[ -n "${pids}" ]]; then
    kill -KILL ${pids} 2>/dev/null || true
  fi
}

trap stop_server EXIT

wait_for_server() {
  local model="$1"
  local server_pid="$2"
  local log_file="$3"
  local waited=0
  while (( waited < 1800 )); do
    if ! kill -0 "${server_pid}" 2>/dev/null; then
      echo "server process exited while loading ${model}" >&2
      tail -120 "${log_file}" >&2 || true
      return 1
    fi
    if curl -fsS "${BASE_URL}/models" >/tmp/effectbench_models.json 2>/dev/null; then
      if grep -q "${model}" /tmp/effectbench_models.json; then
        return 0
      fi
    fi
    sleep 10
    waited=$((waited + 10))
    echo "waiting for ${model}: ${waited}s"
  done
  echo "timed out waiting for ${model}" >&2
  tail -120 "${log_file}" >&2 || true
  return 1
}

endpoint_smoke() {
  local model="$1"
  local out_json="effectbench_omega/reports/live_smokes/${model}_endpoint_smoke.json"
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
        {"role": "user", "content": "Smoke test."},
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
with open(out_json, "w") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
print(json.dumps(payload, sort_keys=True))
PY
}

stage1_smoke() {
  local model="$1"
  local out_dir="effectbench_omega/outputs/smoke_${model}"
  rm -rf "${out_dir}"
  .venv/bin/python effectbench_omega/scripts/run_online.py \
    --config effectbench_omega/configs/local_open.yaml \
    --manifest effectbench_omega/manifests/tasks_local_open.csv \
    --split "smoke_${model}" \
    --systems BASE PROJ_GUARD EFFECTGUARD \
    --models "${model}" \
    --regimes FULL MEMORY_REVISE ADV_EFFECT \
    --out "${out_dir}" \
    --limit 12 \
    --call-local-model
  .venv/bin/python effectbench_omega/effectbench/kernel/verifier.py \
    --traces "${out_dir}/traces.parquet" \
    --schemas effectbench_omega/schemas \
    --out "${out_dir}/kernel"
  .venv/bin/python effectbench_omega/effectbench/audit/no_oracle_report.py \
    --runtime-logs "${out_dir}/runtime_logs.parquet" \
    --out "effectbench_omega/reports/smoke_${model}_no_oracle.md"
  .venv/bin/python effectbench_omega/effectbench/metrics/cost_audit.py \
    --logs "${out_dir}/api_logs.jsonl" \
    --out "effectbench_omega/reports/smoke_${model}_cost.md"
}

summarize_smoke() {
  local model="$1"
  local out_dir="effectbench_omega/outputs/smoke_${model}"
  .venv/bin/python - "${model}" "${out_dir}" <<'PY'
import json
import sys
from pathlib import Path

model, out_dir = sys.argv[1:3]
summary_path = Path(out_dir) / "kernel" / "verifier_summary.json"
api_logs = Path(out_dir) / "api_logs.jsonl"
failures = Path(out_dir) / "failures.jsonl"
summary = json.loads(summary_path.read_text())
api_count = sum(1 for line in api_logs.open() if line.strip()) if api_logs.exists() else 0
failure_count = sum(1 for line in failures.open() if line.strip()) if failures.exists() else 0
print(json.dumps({
    "model": model,
    "trace_count": summary.get("trace_count"),
    "certificate_count": summary.get("certificate_count"),
    "unresolved_abstraction_warnings": summary.get("unresolved_abstraction_warnings"),
    "api_log_count": api_count,
    "failure_count": failure_count,
}, sort_keys=True))
PY
}

stop_server

for model in "${MODELS[@]}"; do
  log_file="effectbench_omega/reports/live_smokes/${model}_vllm.log"
  echo "=== ${model}: launch ==="
  LOCAL_MODEL="${model}" LOCAL_MODEL_PORT="${PORT}" bash effectbench_omega/scripts/launch_local_model.sh \
    >"${log_file}" 2>&1 &
  server_pid=$!
  if ! wait_for_server "${model}" "${server_pid}" "${log_file}"; then
    stop_server
    exit 1
  fi
  echo "=== ${model}: endpoint smoke ==="
  endpoint_smoke "${model}"
  echo "=== ${model}: stage1 smoke ==="
  stage1_smoke "${model}"
  echo "=== ${model}: summary ==="
  summarize_smoke "${model}"
  echo "=== ${model}: stop ==="
  stop_server
done

echo "all selected-four live smokes completed"
