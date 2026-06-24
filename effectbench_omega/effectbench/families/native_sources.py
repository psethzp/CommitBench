"""Source-backed task records from pinned upstream benchmarks.

The online simulator stays deterministic, but these records bind every sampled
task to a pinned upstream task/scenario or an explicitly declared synthetic
generator. This makes the minimal-plus manifest auditable without requiring a
full native benchmark server for smoke runs.
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from effectbench.util import stable_hash


ROOT = Path(__file__).resolve().parents[3]
UPSTREAMS = ROOT / "effectbench_omega/upstreams"
REPO_VERSIONS = ROOT / "effectbench_omega/artifacts/repo_versions.json"


@dataclass(frozen=True)
class NativeSourceRecord:
    source_native_id: str
    family: str
    source_benchmark: str
    source_commit: str
    source_path: str
    source_hash: str
    instruction: str
    expected_action_names: tuple[str, ...]
    expected_actions_hash: str
    adapter_status: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["expected_action_names"] = list(self.expected_action_names)
        return result


def repo_commit(name: str, default: str = "unknown") -> str:
    if not REPO_VERSIONS.exists():
        return default
    data = json.loads(REPO_VERSIONS.read_text())
    if name == "delegated_docs":
        return "effectbench_omega_synthetic_v1"
    return data.get("upstreams", {}).get(name, {}).get("commit", default)


def load_native_records() -> dict[str, list[NativeSourceRecord]]:
    records = {
        "tau_retail": _load_tau_bench("retail"),
        "tau_airline": _load_tau_bench("airline"),
        "telecom": _load_tau2_domain("telecom"),
        "delegated_docs": _load_delegated_docs(),
        "toolsandbox_contract": _load_toolsandbox(),
    }
    return {family: rows for family, rows in records.items() if rows}


def _literal_tasks_from_py(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "tasks" for target in node.targets):
                return ast.literal_eval(node.value)
    raise ValueError(f"no tasks assignment in {path}")


def _load_tau_bench(domain: str) -> list[NativeSourceRecord]:
    path = UPSTREAMS / f"tau-bench/tau_bench/envs/{domain}/tasks.py"
    if not path.exists():
        return []
    family = "tau_retail" if domain == "retail" else "tau_airline"
    rows = []
    for index, task in enumerate(_literal_tasks_from_py(path)):
        actions = tuple(action.get("name", "") for action in task.get("actions", []))
        payload = {"task": task, "source_path": str(path.relative_to(ROOT))}
        rows.append(
            NativeSourceRecord(
                source_native_id=f"tau-bench:{domain}:{index}",
                family=family,
                source_benchmark=f"tau-bench-{domain}",
                source_commit=repo_commit("tau-bench"),
                source_path=str(path.relative_to(ROOT)),
                source_hash=stable_hash(payload),
                instruction=str(task.get("instruction", "")),
                expected_action_names=actions,
                expected_actions_hash=stable_hash(task.get("actions", [])),
                adapter_status="source_backed_literal_task",
            )
        )
    return rows


def _tau2_instruction(task: dict[str, Any]) -> str:
    instructions = task.get("user_scenario", {}).get("instructions", {})
    parts = [
        instructions.get("known_info"),
        instructions.get("reason_for_call"),
        instructions.get("task_instructions"),
        task.get("ticket"),
    ]
    return "\n".join(str(part) for part in parts if part)


def _load_tau2_domain(domain: str) -> list[NativeSourceRecord]:
    path = UPSTREAMS / f"tau2-bench/data/tau2/domains/{domain}/tasks.json"
    if not path.exists():
        return []
    tasks = json.loads(path.read_text())
    rows = []
    for index, task in enumerate(tasks):
        actions = tuple(
            action.get("name", "")
            for action in task.get("evaluation_criteria", {}).get("actions", [])
        )
        task_id = str(task.get("id", index))
        payload = {"task": task, "source_path": str(path.relative_to(ROOT))}
        rows.append(
            NativeSourceRecord(
                source_native_id=f"tau2-bench:{domain}:{task_id}",
                family="telecom",
                source_benchmark=f"tau2-bench-{domain}",
                source_commit=repo_commit("tau2-bench"),
                source_path=str(path.relative_to(ROOT)),
                source_hash=stable_hash(payload),
                instruction=_tau2_instruction(task),
                expected_action_names=actions,
                expected_actions_hash=stable_hash(task.get("evaluation_criteria", {}).get("actions", [])),
                adapter_status="source_backed_json_task",
            )
        )
    return rows


def _scenario_extension_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "ScenarioExtension"):
            continue
        for keyword in node.keywords:
            if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                names.append(str(keyword.value.value))
    return names


def _load_toolsandbox() -> list[NativeSourceRecord]:
    scenario_dir = UPSTREAMS / "ToolSandbox/tool_sandbox/scenarios"
    if not scenario_dir.exists():
        return []
    rows = []
    for path in sorted(scenario_dir.glob("*_scenarios.py")):
        for name in _scenario_extension_names(path):
            payload = {"scenario_name": name, "source_path": str(path.relative_to(ROOT))}
            rows.append(
                NativeSourceRecord(
                    source_native_id=f"ToolSandbox:{name}",
                    family="toolsandbox_contract",
                    source_benchmark="apple-ToolSandbox",
                    source_commit=repo_commit("ToolSandbox"),
                    source_path=str(path.relative_to(ROOT)),
                    source_hash=stable_hash(payload),
                    instruction=name.replace("_", " "),
                    expected_action_names=tuple(_tool_hints_from_name(name)),
                    expected_actions_hash=stable_hash(_tool_hints_from_name(name)),
                    adapter_status="source_backed_scenario_extension",
                )
            )
    return rows


def _tool_hints_from_name(name: str) -> list[str]:
    hints = []
    for token in ["message", "contact", "reminder", "setting", "location", "cellular", "wifi", "search"]:
        if token in name:
            hints.append(token)
    return hints or ["contract_sensitive_tool"]


def _load_delegated_docs() -> list[NativeSourceRecord]:
    scenarios = ["draft_edit", "external_share", "public_link", "notification", "permission_change"]
    rows = []
    for index in range(64):
        scenario = scenarios[index % len(scenarios)]
        payload = {"family": "delegated_docs", "scenario": scenario, "index": index}
        rows.append(
            NativeSourceRecord(
                source_native_id=f"delegated-docs:v1:{index}",
                family="delegated_docs",
                source_benchmark="effectbench-delegated-docs-synthetic-v1",
                source_commit=repo_commit("delegated_docs"),
                source_path="effectbench_omega/effectbench/families/native_sources.py",
                source_hash=stable_hash(payload),
                instruction=f"Delegated document task requiring {scenario.replace('_', ' ')}.",
                expected_action_names=(scenario,),
                expected_actions_hash=stable_hash([scenario]),
                adapter_status="declared_synthetic_controlled_family",
            )
        )
    return rows


def native_source_summary(records: dict[str, list[NativeSourceRecord]] | None = None) -> list[dict[str, Any]]:
    records = records or load_native_records()
    return [
        {
            "family": family,
            "record_count": len(rows),
            "source_benchmarks": ",".join(sorted({row.source_benchmark for row in rows})),
            "adapter_statuses": ",".join(sorted({row.adapter_status for row in rows})),
            "source_commits": ",".join(sorted({row.source_commit for row in rows})),
        }
        for family, rows in sorted(records.items())
    ]

