#!/usr/bin/env python3
"""Build deterministic projection baselines for EffectKernelBench."""

from __future__ import annotations

from effectkernelbench_artifact import build_baselines_cli


if __name__ == "__main__":
    raise SystemExit(build_baselines_cli())
