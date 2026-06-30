#!/usr/bin/env python3
"""Root wrapper for the source online runner.

This wrapper exists so the review artifact gate can run
`python scripts/run_online.py --help` without importing paid-provider clients.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "effectbench_omega/scripts/run_online.py"), run_name="__main__")
