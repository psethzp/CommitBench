#!/usr/bin/env python3
"""Scan local paper/report files for obvious unresolved placeholders."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\?\?\?"),
    re.compile(r"XX+"),
]

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "effectbench_omega.egg-info",
    "effectbench_omega_local.egg-info",
    "upstreams",
    "outputs",
    "witness_bundles",
    "models",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="effectbench_omega/reports/no_red_placeholders.md")
    args = parser.parse_args()

    root = Path(args.root)
    targets = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and not (IGNORE_DIRS & set(path.parts))
        and path.suffix in {".md", ".tex", ".csv", ".yaml", ".yml"}
    ]
    hits: list[str] = []
    for path in targets:
        text = path.read_text(errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in PATTERNS):
                hits.append(f"{path}:{lineno}: {line.strip()}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if hits:
        out.write_text("# Placeholder Scan\n\nFAIL\n\n" + "\n".join(hits) + "\n")
        print(f"found {len(hits)} placeholder-like lines")
        return 1
    out.write_text("# Placeholder Scan\n\nPASS\n")
    print("placeholder scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
