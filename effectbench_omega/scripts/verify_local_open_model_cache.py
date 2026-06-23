#!/usr/bin/env python3
"""Verify local open-weight model cache readiness without duplicating files."""

from __future__ import annotations

import json
from pathlib import Path


SPECS = [
    {
        "model": "qwen3_14b_awq_local",
        "repo": "Qwen/Qwen3-14B-AWQ",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-14B-AWQ/snapshots/31c69efc29464b6bb0aee1398b5a7b50a99340c3",
        "min_safetensor_bytes": 9_000_000_000,
        "required": False,
        "note": "cached but not in the locked headline grid",
    },
    {
        "model": "mistral_small_3_2_24b_local",
        "repo": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--mistralai--Mistral-Small-3.2-24B-Instruct-2506/snapshots/95a6d26c4bfb886c58daf9d3f7332c857cb27b43",
        "min_safetensor_bytes": 45_000_000_000,
        "required": True,
    },
    {
        "model": "qwen3_30b_a3b_local",
        "repo": "Qwen/Qwen3-30B-A3B-Instruct-2507",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507/snapshots/0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe",
        "min_safetensor_bytes": 60_000_000_000,
        "required": False,
        "note": "cached but not in the locked headline grid",
    },
    {
        "model": "qwen3_6_35b_a3b_local",
        "repo": "Qwen/Qwen3.6-35B-A3B",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B/snapshots/995ad96eacd98c81ed38be0c5b274b04031597b0",
        "min_safetensor_bytes": 70_000_000_000,
        "required": True,
    },
    {
        "model": "llama3_3_70b_awq_local",
        "repo": "casperhansen/llama-3.3-70b-instruct-awq",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--casperhansen--llama-3.3-70b-instruct-awq/snapshots/64d255621f40b42adaf6d1f32a47e1d4534c0f14",
        "min_safetensor_bytes": 39_000_000_000,
        "required": True,
        "note": "active headline AWQ INT4 substitute for full Llama 3.3 70B Instruct",
    },
    {
        "model": "gemma3_27b_it_local",
        "repo": "google/gemma-3-27b-it",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--google--gemma-3-27b-it/snapshots/005ad3404e59d6023443cb575daa05336842228a",
        "min_safetensor_bytes": 54_000_000_000,
        "required": True,
        "note": "active headline Gemma 3 27B instruction model",
    },
    {
        "model": "llama3_3_70b_full_local",
        "repo": "meta-llama/Llama-3.3-70B-Instruct",
        "snapshot": "/home/ubuntu/.cache/huggingface/hub/models--meta-llama--Llama-3.3-70B-Instruct",
        "min_safetensor_bytes": 135_000_000_000,
        "required": False,
        "note": "full precision gated/not cached; AWQ substitute is ready",
    },
]


def _snapshot_status(spec: dict) -> dict:
    path = Path(spec["snapshot"])
    safes = list(path.glob("*.safetensors")) if path.exists() else []
    safetensor_bytes = sum(item.stat().st_size for item in safes if item.exists())
    repo_root = path.parents[1] if "snapshots" in path.parts else path
    incomplete = list(repo_root.glob("blobs/*.incomplete")) if repo_root.exists() else []
    missing_core = []
    for name in ("config.json",):
        if path.exists() and not (path / name).exists():
            missing_core.append(name)
    ready = (
        path.exists()
        and safetensor_bytes >= int(spec["min_safetensor_bytes"])
        and not incomplete
        and not missing_core
    )
    return {
        "model": spec["model"],
        "repo": spec["repo"],
        "snapshot": str(path),
        "required": spec.get("required", False),
        "ready": ready,
        "safetensor_count": len(safes),
        "safetensor_gb": round(safetensor_bytes / 1_000_000_000, 3),
        "incomplete_blob_count": len(incomplete),
        "missing_core_files": missing_core,
        "note": spec.get("note", ""),
    }


def main() -> int:
    rows = [_snapshot_status(spec) for spec in SPECS]
    payload = {
        "cache_root": "/home/ubuntu/.cache/huggingface/hub",
        "models": rows,
        "required_ready": all(row["ready"] for row in rows if row["required"]),
    }
    out = Path("effectbench_omega/artifacts/local_open_model_cache.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["required_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
