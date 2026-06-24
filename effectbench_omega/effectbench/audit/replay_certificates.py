#!/usr/bin/env python3
"""Replay generated certificate bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", required=True)
    parser.add_argument("--out")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir)
    bundles = [path for path in bundle_dir.glob("*.json") if path.name != "verifier_summary.json"]
    failures = []
    for path in bundles:
        payload = json.loads(path.read_text())
        cert = payload.get("certificate", {})
        if not cert.get("trace_id") or not payload.get("model_trace"):
            failures.append(str(path))
        if cert.get("verdict") == "strict_excess" and not payload.get("lower_effect_witness_trace"):
            failures.append(str(path))

    report = f"bundles_checked: {len(bundles)}\nfailures: {len(failures)}\n"
    if failures:
        report += "failed_bundles:\n" + "\n".join(failures) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report)
    print(report, end="")
    return 1 if failures and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())

