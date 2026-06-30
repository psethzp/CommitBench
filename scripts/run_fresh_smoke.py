#!/usr/bin/env python3
"""Run the required local fresh-generation smoke."""

from __future__ import annotations

from effectkernelbench_artifact import fresh_smoke_cli


if __name__ == "__main__":
    raise SystemExit(fresh_smoke_cli())
