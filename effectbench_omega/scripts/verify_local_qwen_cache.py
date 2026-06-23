#!/usr/bin/env python3
"""Verify or optionally populate the local Qwen3-30B-A3B cache."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MODEL_ID = "Qwen/Qwen3-30B-A3B-Instruct-2507"
CACHE_DIR = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507"
SNAPSHOT = CACHE_DIR / "snapshots/0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe"
REQUIRED_FILES = [
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "model.safetensors.index.json",
]


def _download_snapshot() -> Path:
    from huggingface_hub import snapshot_download

    path = snapshot_download(MODEL_ID)
    return Path(path)


def _verify_snapshot(snapshot: Path) -> dict[str, object]:
    missing = [name for name in REQUIRED_FILES if not (snapshot / name).exists()]
    shards = sorted(snapshot.glob("model-*-of-*.safetensors"))
    incomplete = sorted(CACHE_DIR.glob("**/*.incomplete"))

    transformers_ok = False
    config_model_type = None
    tokenizer_class = None
    tokenizer_vocab_size = None
    error = None

    if not missing and shards and not incomplete:
        try:
            from transformers import AutoConfig, AutoTokenizer

            config = AutoConfig.from_pretrained(
                str(snapshot),
                local_files_only=True,
                trust_remote_code=True,
            )
            tokenizer = AutoTokenizer.from_pretrained(
                str(snapshot),
                local_files_only=True,
                trust_remote_code=True,
            )
            transformers_ok = True
            config_model_type = getattr(config, "model_type", None)
            tokenizer_class = tokenizer.__class__.__name__
            tokenizer_vocab_size = getattr(tokenizer, "vocab_size", None)
        except Exception as exc:  # pragma: no cover - diagnostic script.
            error = f"{type(exc).__name__}: {exc}"

    return {
        "model_id": MODEL_ID,
        "cache_dir": str(CACHE_DIR),
        "snapshot": str(snapshot),
        "snapshot_exists": snapshot.exists(),
        "missing_required_files": missing,
        "safetensor_shard_count": len(shards),
        "incomplete_file_count": len(incomplete),
        "transformers_local_load_ok": transformers_ok,
        "config_model_type": config_model_type,
        "tokenizer_class": tokenizer_class,
        "tokenizer_vocab_size": tokenizer_vocab_size,
        "error": error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-if-missing", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    snapshot = SNAPSHOT
    if args.download_if_missing and not snapshot.exists():
        snapshot = _download_snapshot()

    result = _verify_snapshot(snapshot)
    payload = json.dumps(result, indent=2, sort_keys=True)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n")

    ok = (
        result["snapshot_exists"]
        and not result["missing_required_files"]
        and result["safetensor_shard_count"] == 16
        and result["incomplete_file_count"] == 0
        and result["transformers_local_load_ok"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
