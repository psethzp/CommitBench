from __future__ import annotations

from effectbench.kernel.enumerate_frontier import enumerate_admissible_sequences


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

