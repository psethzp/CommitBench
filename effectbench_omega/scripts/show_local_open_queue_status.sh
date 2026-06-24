#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

JOB_DIR="${1:-effectbench_omega/jobs/local_open_latest}"

if [[ -L "${JOB_DIR}" ]]; then
  JOB_DIR="$(readlink -f "${JOB_DIR}")"
fi

if [[ ! -d "${JOB_DIR}" ]]; then
  echo "No queue directory found: ${JOB_DIR}" >&2
  exit 1
fi

echo "queue_dir=${JOB_DIR}"
if [[ -f "${JOB_DIR}/queue.pid" ]]; then
  queue_pid="$(cat "${JOB_DIR}/queue.pid")"
  if kill -0 "${queue_pid}" 2>/dev/null; then
    echo "queue_pid=${queue_pid} running"
  else
    echo "queue_pid=${queue_pid} not-running"
  fi
fi
if [[ -f "${JOB_DIR}/current_model" ]]; then
  echo "current_model=$(cat "${JOB_DIR}/current_model")"
  echo "current_status=$(cat "${JOB_DIR}/current_status")"
  echo "current_detail=$(cat "${JOB_DIR}/current_detail")"
fi

echo
echo "recent_events:"
tail -20 "${JOB_DIR}/events.tsv" 2>/dev/null || true

echo
echo "summaries:"
if compgen -G "${JOB_DIR}/summaries/*.json" >/dev/null; then
  jq -c . "${JOB_DIR}"/summaries/*.json
else
  echo "none yet"
fi

echo
echo "vllm_processes:"
pgrep -af 'python -m [v]llm.entrypoints.openai.api_server' || true

echo
echo "gpu:"
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
