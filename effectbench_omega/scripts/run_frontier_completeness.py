#!/usr/bin/env python3
"""Run the enumerated frontier completeness audit for a frozen split."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="main_mc_postfix_all_local")
    parser.add_argument("--traces")
    parser.add_argument("--certificates")
    parser.add_argument("--out")
    parser.add_argument("--tables-out")
    parser.add_argument("--report-out")
    args = parser.parse_args()

    split = args.split
    traces = args.traces or f"effectbench_omega/outputs/{split}/traces.parquet"
    certificates = args.certificates or f"effectbench_omega/outputs/{split}/kernel/certificates.parquet"
    out = args.out or f"effectbench_omega/outputs/frontier_audit_{split}"
    tables_out = args.tables_out or f"effectbench_omega/tables/frontier_completeness_{split}.csv"
    report_out = args.report_out or f"effectbench_omega/reports/frontier_completeness_{split}.md"

    for path in (traces, certificates):
        if not Path(path).exists():
            raise SystemExit(f"missing required input: {path}")

    command = [
        sys.executable,
        "effectbench_omega/effectbench/kernel/enumerate_frontier.py",
        "--traces",
        traces,
        "--certificates",
        certificates,
        "--out",
        out,
        "--tables-out",
        tables_out,
        "--report-out",
        report_out,
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())

