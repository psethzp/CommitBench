#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SNAPSHOT="${QWEN3_30B_SNAPSHOT:-/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507/snapshots/0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe}"
TP="${QWEN3_TP:-4}"
PORT="${QWEN3_PORT:-8001}"

source "${ROOT_DIR}/.venv/bin/activate"

export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}"

python -m vllm.entrypoints.openai.api_server \
  --model "${SNAPSHOT}" \
  --served-model-name qwen3_30b_a3b_local \
  --tensor-parallel-size "${TP}" \
  --dtype auto \
  --max-model-len 32768 \
  --trust-remote-code \
  --generation-config vllm \
  --disable-custom-all-reduce \
  --no-enable-flashinfer-autotune \
  --port "${PORT}"
