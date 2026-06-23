#!/usr/bin/env python3
"""Clone/pin upstream benchmark repos without running experiments."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


REPOS = {
    "tau-bench": "https://github.com/sierra-research/tau-bench",
    "tau2-bench": "https://github.com/sierra-research/tau2-bench",
    "ToolSandbox": "https://github.com/apple/ToolSandbox",
}

QWEN_SNAPSHOT = "/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B-Instruct-2507/snapshots/0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe"
QWEN_COMMIT = "0d7cf23991f47feeb3a57ecb4c9cee8ea4a17bfe"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def ensure_repo(name: str, url: str, root: Path) -> dict[str, str]:
    path = root / name
    if not path.exists():
        run(["git", "clone", "--depth", "1", url, str(path)])
    else:
        run(["git", "fetch", "--depth", "1", "origin", "HEAD"], cwd=path)
    commit = run(["git", "rev-parse", "HEAD"], cwd=path)
    remote = run(["git", "remote", "get-url", "origin"], cwd=path)
    return {"url": remote, "path": str(path), "commit": commit, "status": "cloned_and_pinned"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="effectbench_omega/artifacts/repo_versions.json")
    parser.add_argument("--root", default="effectbench_omega/upstreams")
    parser.add_argument("--skip-clone", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    versions: dict[str, object] = {
        "commitbench": {
            "path": str(Path.cwd()),
            "commit": run(["git", "rev-parse", "HEAD"]),
            "status": "working_tree_may_have_uncommitted_setup_changes",
        },
        "qwen3_30b_a3b_local": {
            "model_id": "Qwen/Qwen3-30B-A3B-Instruct-2507",
            "snapshot": QWEN_SNAPSHOT,
            "snapshot_commit": QWEN_COMMIT,
            "status": "present_and_local_load_verified",
        },
        "upstreams": {},
    }

    upstreams: dict[str, object] = {}
    for name, url in REPOS.items():
        if args.skip_clone:
            upstreams[name] = {"url": url, "status": "not_cloned_skip_clone"}
        else:
            upstreams[name] = ensure_repo(name, url, root)
    versions["upstreams"] = upstreams

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(versions, indent=2, sort_keys=True) + "\n")
    print(json.dumps(versions, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

