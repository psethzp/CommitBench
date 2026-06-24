import pytest

from effectbench.guard.no_oracle import FORBIDDEN_RUNTIME_FIELDS, assert_no_oracle, strip_oracle_fields


def test_forbidden_field_set_matches_handoff():
    assert FORBIDDEN_RUNTIME_FIELDS == {
        "future_user_turns",
        "gold_terminal_state",
        "offline_terminal_frontier_id",
        "evaluator_label",
        "final_outcome",
        "posthoc_witness_bundle",
    }


@pytest.mark.parametrize("field", sorted(FORBIDDEN_RUNTIME_FIELDS))
def test_no_oracle_sentinel_rejects_each_forbidden_field(field):
    with pytest.raises(RuntimeError, match="oracle fields"):
        assert_no_oracle({"observed_user_turns_so_far": [], field: "fake"})


def test_no_oracle_accepts_allowed_runtime_context():
    assert_no_oracle(
        {
            "observed_user_turns_so_far": [],
            "prior_tool_observations": [],
            "policy_preconditions": "least_effect_success",
            "current_abstract_state": {"target_id": "x"},
        }
    )


def test_strip_oracle_fields_removes_sentinels():
    context = {"observed_user_turns_so_far": [], "gold_terminal_state": "fake"}
    stripped = strip_oracle_fields(context)
    assert "gold_terminal_state" not in stripped
    assert stripped["observed_user_turns_so_far"] == []
