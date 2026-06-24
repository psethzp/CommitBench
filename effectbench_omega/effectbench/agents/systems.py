"""Deterministic online systems plus optional local-model advice."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

from effectbench.effects import ACTION_LIBRARY, action_effect, dumps, max_effect
from effectbench.guard.no_oracle import assert_no_oracle
from effectbench.regimes import hazard_flags


@dataclass
class TraceAction:
    step: int
    action: str
    target_id: str
    effect_vector: str
    rationale: str


@dataclass
class EpisodeTrace:
    actions: list[TraceAction]
    terminal_success: bool
    terminal_equivalence_class: str
    effect_vector: dict[str, int]
    guard_decisions: list[dict[str, Any]]
    added_user_turns: int
    false_denial: bool
    model_proposed_actions: list[str]
    model_proposal_parse_status: str
    model_proposal_repair_log: list[str]

    def actions_json(self) -> str:
        return json.dumps([asdict(action) for action in self.actions], sort_keys=True)

    def guard_json(self) -> str:
        return json.dumps(self.guard_decisions, sort_keys=True)


def run_system(row: dict[str, Any], model_advice: str | None = None) -> EpisodeTrace:
    system = str(row["system"])
    proposal = _parse_model_proposal(model_advice, row)
    runtime_context = {
        "observed_user_turns_so_far": row.get("turns", []),
        "prior_tool_observations": [],
        "policy_preconditions": row.get("policy_obligation"),
        "current_abstract_state": {"target_id": row.get("target_id")},
    }
    assert_no_oracle(runtime_context)

    if system == "BASE":
        names = _base_policy(row, model_advice, proposal)
    elif system == "PROJ_GUARD":
        names = _proj_guard_policy(row, proposal)
    elif system == "EFFECTGUARD":
        names = _effectguard_policy(row, proposal)
    else:
        raise ValueError(f"unknown system: {system}")

    target = str(row["target_id"])
    effects = [action_effect(name) for name in names]
    actions = [
        TraceAction(
            step=index + 1,
            action=name,
            target_id=target,
            effect_vector=dumps(action_effect(name)),
            rationale=_rationale(system, name, row),
        )
        for index, name in enumerate(names)
    ]
    guard_decisions = _guard_decisions(system, names, row, proposal)
    return EpisodeTrace(
        actions=actions,
        terminal_success=names[-1] in {"commit_low", "commit_contract_low", "commit_high", "external_notify_high"},
        terminal_equivalence_class=str(row["terminal_equivalence_hash"]),
        effect_vector=max_effect(effects),
        guard_decisions=guard_decisions,
        added_user_turns=sum(1 for name in names if name.startswith("ask_")),
        false_denial=False,
        model_proposed_actions=proposal["actions"],
        model_proposal_parse_status=proposal["status"],
        model_proposal_repair_log=proposal["repair_log"],
    )


def _base_policy(row: dict[str, Any], model_advice: str | None, proposal: dict[str, Any]) -> list[str]:
    if proposal["actions"]:
        return proposal["actions"]
    flags = hazard_flags(row)
    advice = (model_advice or "").lower()
    if "low" in advice and "high" not in advice:
        return ["read_record", "commit_low"]
    if flags["adversarial_effect"] or flags["stale_memory"] or flags["externality_sensitive"]:
        return ["read_record", "external_notify_high"]
    if flags["ambiguous_target"] or flags["payment_sensitive"]:
        return ["read_record", "commit_high"]
    if flags["contract_sensitive"]:
        return ["read_record", "commit_high"]
    return ["read_record", "commit_low"]


def _proj_guard_policy(row: dict[str, Any], proposal: dict[str, Any]) -> list[str]:
    flags = hazard_flags(row)
    proposed = proposal["actions"] or _base_policy(row, None, {"actions": []})
    proposed_terminal = _first_terminal(proposed)
    names = ["read_record"]
    if flags["ambiguous_target"]:
        names.append("ask_confirm")
    if flags["contract_sensitive"]:
        if _has_high_effect_terminal(proposed):
            names.append("draft_change")
        names.append("commit_contract_low")
    elif _has_high_effect_terminal(proposed) and (
        flags["adversarial_effect"] or flags["externality_sensitive"] or flags["payment_sensitive"]
    ):
        names.extend(["draft_change", "commit_low"])
    elif proposed_terminal == "external_notify_high":
        names.extend(["draft_change", "commit_low"])
    elif proposed_terminal in {"commit_low", "commit_high"}:
        names.append(proposed_terminal)
    else:
        names.append("commit_low")
    return names


def _effectguard_policy(row: dict[str, Any], proposal: dict[str, Any]) -> list[str]:
    flags = hazard_flags(row)
    proposed = proposal["actions"] or _base_policy(row, None, {"actions": []})
    names = ["read_record"]
    if flags["ambiguous_target"]:
        names.append("ask_confirm")
    if flags["adversarial_effect"] or flags["stale_memory"] or _has_high_effect_terminal(proposed):
        names.append("draft_change")
    if flags["contract_sensitive"]:
        names.append("commit_contract_low")
    else:
        names.append("commit_low")
    return names


def _rationale(system: str, action: str, row: dict[str, Any]) -> str:
    if system == "BASE":
        return "vanilla agent chose from full tool menu"
    if system == "PROJ_GUARD":
        return "projection guard applied local filters"
    if action in {"draft_change", "commit_low", "commit_contract_low"}:
        return "EffectGuard chose lower-effect admissible suffix"
    return "EffectGuard gathered currently necessary information"


def _guard_decisions(system: str, names: list[str], row: dict[str, Any], proposal: dict[str, Any]) -> list[dict[str, Any]]:
    if system == "BASE":
        return [
            {
                "decision": "model_proposal_executed",
                "parse_status": proposal["status"],
                "proposed_actions": proposal["actions"],
                "repair_log": proposal["repair_log"],
            }
        ] if proposal["actions"] else []
    decisions: list[dict[str, Any]] = []
    if proposal["actions"]:
        decisions.append(
            {
                "decision": "model_proposal_reviewed",
                "parse_status": proposal["status"],
                "proposed_actions": proposal["actions"],
                "executed_actions": names,
                "repair_log": proposal["repair_log"],
            }
        )
    if "ask_confirm" in names:
        decisions.append({"decision": "ask_or_read_missing_field", "reason": "target ambiguity under current turns"})
    if "draft_change" in names:
        decisions.append({"decision": "substitute_lower_effect", "reason": "reversible draft/write satisfies known obligation"})
    if "commit_contract_low" in names:
        decisions.append({"decision": "necessary_high", "reason": "contract artifact must be preserved"})
    return decisions


TERMINAL_ACTIONS = {"commit_low", "commit_contract_low", "commit_high", "external_notify_high"}
KNOWN_ACTIONS = set(ACTION_LIBRARY)
ACTION_ALIASES = {
    "read": "read_record",
    "read_minimal": "read_record",
    "lookup": "read_record",
    "ask": "ask_confirm",
    "confirm": "ask_confirm",
    "clarify": "ask_clarify",
    "draft": "draft_change",
    "stage": "draft_change",
    "low": "commit_low",
    "least_effect": "commit_low",
    "commit": "commit_low",
    "commit_contract": "commit_contract_low",
    "contract": "commit_contract_low",
    "high": "commit_high",
    "broad_write": "commit_high",
    "notify": "external_notify_high",
    "external_notify": "external_notify_high",
}


def _parse_model_proposal(raw: str | None, row: dict[str, Any]) -> dict[str, Any]:
    repair_log: list[str] = []
    if not raw:
        return {"actions": [], "status": "missing", "repair_log": ["no_model_proposal"]}

    raw_actions, status = _extract_raw_actions(raw)
    actions: list[str] = []
    for raw_action in raw_actions:
        normalized = _normalize_action(raw_action)
        if normalized in KNOWN_ACTIONS:
            actions.append(normalized)
        else:
            repair_log.append(f"dropped_unknown_action:{raw_action}")

    if not actions:
        fallback = _fallback_action_plan(row)
        return {
            "actions": fallback,
            "status": f"{status}:repair_fallback",
            "repair_log": [*repair_log, "no_valid_actions", "fallback_model_plan"],
        }

    repaired: list[str] = []
    if actions[0] != "read_record":
        repaired.append("read_record")
        repair_log.append("inserted_read_record")

    for action in actions:
        if action == "read_record" and "read_record" in repaired:
            continue
        repaired.append(action)
        if action in TERMINAL_ACTIONS:
            if repaired[-1] != action:
                repair_log.append("truncated_after_terminal")
            break

    if not _first_terminal(repaired):
        terminal = _fallback_terminal(row)
        repaired.append(terminal)
        repair_log.append(f"appended_terminal:{terminal}")

    return {"actions": repaired, "status": status, "repair_log": repair_log}


def _extract_raw_actions(raw: str) -> tuple[list[str], str]:
    payload = _extract_json(raw)
    if isinstance(payload, dict):
        for key in ("actions", "tool_actions", "action_sequence", "plan"):
            value = payload.get(key)
            if value:
                actions = _coerce_actions(value)
                terminal = _normalize_action(str(payload.get("terminal_action") or payload.get("terminal") or ""))
                if terminal in TERMINAL_ACTIONS and not _first_terminal(actions):
                    actions.append(terminal)
                return actions, "json"
        if payload.get("action"):
            actions = _coerce_actions(payload["action"])
            terminal = _normalize_action(str(payload.get("terminal_action") or payload.get("terminal") or ""))
            if terminal in TERMINAL_ACTIONS and not _first_terminal(actions):
                actions.append(terminal)
            return actions, "json"
    if isinstance(payload, list):
        return _coerce_actions(payload), "json"

    lowered = raw.lower()
    found = [action for action in KNOWN_ACTIONS if re.search(rf"\b{re.escape(action)}\b", lowered)]
    if found:
        ordered = sorted(found, key=lambda action: lowered.index(action))
        return ordered, "text_scan"
    if "low" in lowered and "high" not in lowered:
        return ["read_record", "commit_low"], "low_high_legacy"
    if "high" in lowered:
        return ["read_record", "commit_high"], "low_high_legacy"
    return [], "unparsed"


def _extract_json(raw: str) -> Any:
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw):
        if char not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(raw[index:])
            return value
        except json.JSONDecodeError:
            continue
    return None


def _coerce_actions(value: Any) -> list[str]:
    if isinstance(value, str):
        return [piece for piece in re.split(r"[\s,|>]+", value) if piece]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                result.extend(_coerce_actions(item.get("action") or item.get("name") or item.get("tool") or ""))
        return result
    return []


def _normalize_action(action: str) -> str:
    normalized = re.sub(r"[^a-z0-9_]+", "_", action.strip().lower()).strip("_")
    return ACTION_ALIASES.get(normalized, normalized)


def _first_terminal(actions: list[str]) -> str:
    return next((action for action in actions if action in TERMINAL_ACTIONS), "")


def _has_high_effect_terminal(actions: list[str]) -> bool:
    return any(action in {"commit_high", "external_notify_high"} for action in actions)


def _fallback_terminal(row: dict[str, Any]) -> str:
    flags = hazard_flags(row)
    if flags["contract_sensitive"]:
        return "commit_contract_low"
    return "commit_low"


def _fallback_action_plan(row: dict[str, Any]) -> list[str]:
    flags = hazard_flags(row)
    if flags["adversarial_effect"] or flags["stale_memory"] or flags["externality_sensitive"]:
        return ["read_record", "external_notify_high"]
    if flags["ambiguous_target"] or flags["payment_sensitive"] or flags["contract_sensitive"]:
        return ["read_record", "commit_high"]
    return ["read_record", "commit_low"]
