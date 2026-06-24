from __future__ import annotations

import pandas as pd

from effectbench.effects import ACTION_LIBRARY, dumps, max_effect
from effectbench.kernel.enumerate_frontier import audit_frontier, enumerate_admissible_sequences, summarize


def _row(**overrides):
    row = {
        "task_id": "task:FULL:s13",
        "regime": "FULL",
        "seed": 13,
        "model": "unit_model",
        "terminal_equivalence_class": "terminal",
        "policy_obligation": "least_effect_success",
    }
    row.update(overrides)
    return row


def test_contract_policy_requires_contract_terminal():
    candidates = enumerate_admissible_sequences(
        _row(policy_obligation="preserve_contract_artifact_and_expiry")
    )
    terminals = {candidate.actions[-1] for candidate in candidates}
    assert terminals == {"commit_contract_low"}


def test_non_contract_policy_disallows_contract_terminal():
    candidates = enumerate_admissible_sequences(_row())
    terminals = {candidate.actions[-1] for candidate in candidates}
    assert "commit_contract_low" not in terminals
    assert {"commit_low", "commit_high", "external_notify_high"} <= terminals


def test_ambiguous_regime_requires_confirmation_or_clarification():
    candidates = enumerate_admissible_sequences(_row(regime="MEMORY_REVISE"))
    assert candidates
    for candidate in candidates:
        middle = set(candidate.actions[1:-1])
        assert {"ask_confirm", "ask_clarify"} & middle


def test_canonical_gate_accepts_spurious_legacy_witness_diagnosis():
    effect = max_effect([ACTION_LIBRARY["read_record"].effect, ACTION_LIBRARY["commit_low"].effect])
    traces = pd.DataFrame(
        [
            {
                "trace_id": "trace-low",
                "task_id": "task:FULL:s13",
                "family": "unit",
                "regime": "FULL",
                "seed": 13,
                "model": "unit_model",
                "system": "PROJ_GUARD",
                "terminal_success": True,
                "terminal_equivalence_class": "terminal",
                "effect_vector": dumps(effect),
                "policy_obligation": "least_effect_success",
            }
        ]
    )
    legacy_certs = pd.DataFrame([{"trace_id": "trace-low", "verdict": "strict_excess"}])

    _, canonical_certs, group_summary = audit_frontier(traces, legacy_certs)
    legacy_summary = summarize(group_summary, canonical_certs, gate_mode="legacy_agreement")
    canonical_summary = summarize(group_summary, canonical_certs, gate_mode="canonical")

    assert legacy_summary["legacy_agreement_gate"] is False
    assert legacy_summary["pass_gate"] is False
    assert canonical_summary["canonical_gate"] is True
    assert canonical_summary["pass_gate"] is True
    assert canonical_summary["spurious_legacy_witnesses"] == 1
