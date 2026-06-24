#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL_MODEL="${LOCAL_MODEL:-qwen3_30b_a3b_local}"
PORT="${LOCAL_MODEL_PORT:-8001}"

case "$LOCAL_MODEL" in
  qwen3_14b_awq_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-14B-AWQ/snapshots/31c69efc29464b6bb0aee1398b5a7b50a99340c3"
    TP="${LOCAL_MODEL_TP:-1}"
    EXTRA_ARGS=(--quantization awq)
    ;;
  mistral_small_3_2_24b_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--mistralai--Mistral-Small-3.2-24B-Instruct-2506/snapshots/95a6d26c4bfb886c58daf9d3f7332c857cb27b43"
    TP="${LOCAL_MODEL_TP:-4}"
    EXTRA_ARGS=(
      --tokenizer-mode mistral
      --config-format mistral
      --tool-call-parser mistral
      --enable-auto-tool-choice
      --limit-mm-per-prompt '{"image":10}'
    )
    ;;
  qwen3_30b_a3b_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507/snapshots/0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe"
    TP="${LOCAL_MODEL_TP:-4}"
    EXTRA_ARGS=()
    ;;
  qwen3_6_35b_a3b_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B/snapshots/995ad96eacd98c81ed38be0c5b274b04031597b0"
    TP="${LOCAL_MODEL_TP:-4}"
    EXTRA_ARGS=()
    ;;
  llama3_3_70b_awq_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--casperhansen--llama-3.3-70b-instruct-awq/snapshots/64d255621f40b42adaf6d1f32a47e1d4534c0f14"
    TP="${LOCAL_MODEL_TP:-4}"
    EXTRA_ARGS=(--quantization awq)
    ;;
  gemma3_27b_it_local)
    MODEL_PATH="/home/ubuntu/.cache/huggingface/hub/models--google--gemma-3-27b-it/snapshots/005ad3404e59d6023443cb575daa05336842228a"
    TP="${LOCAL_MODEL_TP:-4}"
    EXTRA_ARGS=()
    ;;
  *)
    echo "Unknown LOCAL_MODEL=$LOCAL_MODEL" >&2
    exit 2
    ;;
esac

source "${ROOT_DIR}/.venv/bin/activate"

export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}"

exec python -m vllm.entrypoints.openai.api_server \
  --model "${MODEL_PATH}" \
  --served-model-name "${LOCAL_MODEL}" \
  --tensor-parallel-size "${TP}" \
  --dtype auto \
  --max-model-len 32768 \
  --trust-remote-code \
  --generation-config vllm \
  --disable-custom-all-reduce \
  --no-enable-flashinfer-autotune \
  --port "${PORT}" \
  "${EXTRA_ARGS[@]}"
