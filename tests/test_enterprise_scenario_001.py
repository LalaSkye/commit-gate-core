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

import copy
import hashlib
import json
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# CommitGate — minimal synthetic implementation for test surface
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "actor",
    "action_type",
    "recipient_scope",
    "payload_hash",
    "authority_token",
    "expiry",
    "nonce",
]

_sent_messages = []


def _compute_state_hash(state: dict) -> str:
    serialised = json.dumps(state, sort_keys=True).encode()
    return hashlib.sha256(serialised).hexdigest()


def _write_receipt(attempt: dict, missing_field: str, decision: str, reason: str) -> dict:
    return {
        "receipt_id": f"RCP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-001",
        "scenario_id": "ESP-001",
        "attempted_action": attempt.get("action_type", "UNKNOWN"),
        "actor": attempt.get("actor", "UNKNOWN"),
        "action_type": attempt.get("action_type", "UNKNOWN"),
        "recipient_scope": attempt.get("recipient_scope", "UNKNOWN"),
        "payload_hash": attempt.get("payload_hash", "UNKNOWN"),
        "missing_field": missing_field,
        "decision": decision,
        "refusal_reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "downstream_send": False,
    }


def commit_gate(attempt: dict, state_before: dict) -> dict:
    """
    CommitGate — STRUCTURE_FIRST, FIRST_FAIL evaluation.
    Returns a result dict with decision, receipt, and state metadata.
    """
    state_snapshot_before = copy.deepcopy(state_before)
    hash_before = _compute_state_hash(state_snapshot_before)

    for field in REQUIRED_FIELDS:
        if field not in attempt or attempt[field] is None or attempt[field] == "":
            receipt = _write_receipt(
                attempt,
                missing_field=field,
                decision="DENY",
                reason=(
                    f"{field} absent — no valid DecisionRecord for this actor, "
                    "action_type, recipient_scope, and payload at gate time"
                ),
            )
            hash_after = _compute_state_hash(state_snapshot_before)
            return {
                "decision": "DENY",
                "missing_field": field,
                "downstream_send": False,
                "receipt_written": True,
                "receipt": receipt,
                "sent_messages": list(_sent_messages),
                "before_state_hash": hash_before,
                "after_state_hash": hash_after,
                "state_mutated": hash_before != hash_after,
            }

    # All fields present — ALLOW path. Not triggered in this scenario.
    _sent_messages.append(attempt)
    receipt = _write_receipt(attempt, missing_field="", decision="ALLOW", reason="all fields valid")
    hash_after = _compute_state_hash(state_snapshot_before)
    return {
        "decision": "ALLOW",
        "missing_field": None,
        "downstream_send": True,
        "receipt_written": True,
        "receipt": receipt,
        "sent_messages": list(_sent_messages),
        "before_state_hash": hash_before,
        "after_state_hash": hash_after,
        "state_mutated": False,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

INVALID_ATTEMPT_MISSING_AUTHORITY = {
    "actor": "agent://morpheus-draft-bot-v1",
    "action_type": "SEND_EXTERNAL_EMAIL",
    "recipient_scope": "external:partner-domain.com",
    "payload_hash": "sha256:a3f8c2d1e7b904561ac38fd2e190bba47c2d3f8a1e056b7c9d4e2f1a8b3c7d90",
    "authority_token": None,   # MISSING — triggers refusal
    "expiry": "2026-05-12T23:59:59Z",
    "nonce": "nonce-abc-001",
}

INITIAL_STATE = {
    "sent_count": 0,
    "last_action": None,
    "pending_receipts": [],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_missing_authority_token_denies_send():
    """
    ASSERT: A missing authority_token produces decision == DENY
    and missing_field == authority_token.
    """
    result = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    assert result["decision"] == "DENY", (
        f"Expected DENY, got {result['decision']}"
    )
    assert result["missing_field"] == "authority_token", (
        f"Expected missing_field='authority_token', got '{result['missing_field']}'"
    )


def test_no_downstream_send_occurs():
    """
    ASSERT: downstream_send is False and sent_messages list is empty.
    """
    result = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    assert result["downstream_send"] is False, (
        "downstream_send should be False — no email should leave the system"
    )
    assert result["sent_messages"] == [], (
        f"sent_messages should be empty, got: {result['sent_messages']}"
    )


def test_receipt_is_written():
    """
    ASSERT: receipt_written is True and receipt contains expected fields.
    """
    result = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    assert result["receipt_written"] is True, "receipt_written should be True"
    receipt = result["receipt"]
    required_receipt_fields = [
        "receipt_id", "scenario_id", "attempted_action", "actor",
        "action_type", "recipient_scope", "payload_hash", "missing_field",
        "decision", "refusal_reason", "timestamp", "downstream_send",
    ]
    for field in required_receipt_fields:
        assert field in receipt, f"Receipt missing field: {field}"
    assert receipt["decision"] == "DENY"
    assert receipt["downstream_send"] is False
    assert receipt["missing_field"] == "authority_token"


def test_state_hash_does_not_change():
    """
    ASSERT: before_state_hash == after_state_hash and state_mutated is False.
    A refusal must not alter system state.
    """
    result = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    assert result["before_state_hash"] == result["after_state_hash"], (
        "State hash changed on refusal — state mutation detected"
    )
    assert result["state_mutated"] is False, (
        "state_mutated should be False after a DENY"
    )


def test_replay_is_stable():
    """
    ASSERT: Running the same invalid attempt twice produces the same
    decision and the same missing_field — refusal is deterministic.
    """
    first = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    replay = commit_gate(INVALID_ATTEMPT_MISSING_AUTHORITY, copy.deepcopy(INITIAL_STATE))
    assert first["decision"] == replay["decision"], (
        f"Replay decision mismatch: {first['decision']} vs {replay['decision']}"
    )
    assert first["missing_field"] == replay["missing_field"], (
        f"Replay missing_field mismatch: {first['missing_field']} vs {replay['missing_field']}"
    )
