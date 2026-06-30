#!/usr/bin/env python3
"""Verify EffectKernelBench claim registry rows and source hashes."""

from __future__ import annotations

from effectkernelbench_artifact import verify_claim_registry_cli


if __name__ == "__main__":
    raise SystemExit(verify_claim_registry_cli())
