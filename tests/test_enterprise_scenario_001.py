"""
tests/test_enterprise_scenario_001.py

Enterprise Scenario Pack v0.1 — Scenario 001
AI-Generated External Email — Missing Authority Token

SCOPE: NON_EXEC / REVIEW_ONLY
CLAIM: Synthetic refusal test. Not enterprise-certified. Not deployed. Not compliance proof.

This test suite demonstrates a repeatable synthetic refusal for one bounded
enterprise-shaped scenario. It proves refusal, receipt generation, and replay
stability on the demonstrated path only. It does not prove production
enforcement, external system control, compliance, or path-universal coverage.
"""

from commit_gate_core.scenario_runner import run_scenario_001


def test_missing_authority_token_denies_send():
    """Missing authority_token must produce DENY."""
    result = run_scenario_001()

    assert result["verdict"] == "DENY"
    assert result["decision"] == "DENY"
    assert result["missing_field"] == "authority_token"
    assert result["downstream_send"] is False
    assert result["receipt_written"] is True


def test_no_downstream_send_occurs():
    """No email is sent when authority is missing."""
    result = run_scenario_001()

    assert result["downstream_send"] is False
    assert result["sent_messages"] == []


def test_state_hash_does_not_change():
    """State snapshot proves no mutation occurred on the tested path."""
    result = run_scenario_001()

    assert result["before_state_hash"] == result["after_state_hash"]
    assert result["state_mutated"] is False


def test_replay_is_stable():
    """Replay of the same invalid attempt produces identical refusal class."""
    first = run_scenario_001()
    replay = run_scenario_001()

    assert first["verdict"] == replay["verdict"]
    assert first["decision"] == replay["decision"]
    assert first["missing_field"] == replay["missing_field"]
    assert first["downstream_send"] is False
    assert replay["downstream_send"] is False


def test_receipt_structure_is_valid():
    """Receipt contains required fields and correct refusal metadata."""
    result = run_scenario_001()
    receipt = result["receipt"]

    assert receipt["verdict"] == "DENY"
    assert receipt["decision"] == "DENY"
    assert receipt["missing_field"] == "authority_token"
    assert receipt["payload_hash"] is not None
    assert receipt["receipt_hash"] is not None
    assert "issued_at" in receipt
    assert "refused_at" in receipt
    assert receipt["evidence"]
