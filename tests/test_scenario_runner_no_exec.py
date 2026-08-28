from __future__ import annotations

import copy

from commit_gate_core.scenario_runner import REQUIRED_FIELDS, commit_gate, initial_state, run_scenario_001


def test_missing_authority_fixture_does_not_send() -> None:
    result = run_scenario_001()
    assert result["verdict"] == "DENY"
    assert result["downstream_send"] is False
    assert result["state_mutated"] is False
    assert result["sent_messages"] == []


def test_complete_input_path_cannot_execute_or_mutate_caller_state() -> None:
    state = initial_state()
    original = copy.deepcopy(state)
    attempt = {field: f"value-{field}" for field in REQUIRED_FIELDS}
    attempt["payload"] = {"body": "would-have-been-sent"}
    result = commit_gate(attempt, state)
    assert result["verdict"] == "DENY"
    assert result["downstream_send"] is False
    assert result["missing_field"] == "executor_removed"
    assert result["sent_messages"] == []
    assert state == original
