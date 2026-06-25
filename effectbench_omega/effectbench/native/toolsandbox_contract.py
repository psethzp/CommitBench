"""Native-style wrapper for the ToolSandbox contract subset."""

from __future__ import annotations

from typing import Any

from effectbench.native.common import NativeResult, run_native_state_machine


def execute(row: dict[str, Any], actions: list[str]) -> NativeResult:
    return run_native_state_machine(row, actions, domain="toolsandbox_contract")
