"""
tests/test_changed_condition_refusal.py

Enterprise Scenario Pack — Changed-Condition Refusal Proof Surface
commit-gate-core / LalaSkye

CLAIM:
Yesterday's permission is not today's authority.
When conditions change, previously valid authority becomes inadmissible.
The gate refuses before mutation and writes a receipt.

SCOPE: NON_EXEC / REVIEW_ONLY
BOUNDARY: Synthetic proof surface only.
Not production deployment. Not enterprise adoption.
Not compliance certification. Not production enforcement.
"""

import copy
import hashlib
import json
from datetime import datetime, timezone


# ── Gate configuration ───────────────────────────────────────────────────────

BASELINE = {
    "actor": "agent://morpheus-draft-bot-v1",
    "action_type": "SEND_EXTERNAL_EMAIL",
    "recipient_scope": "external:partner-domain.com",
    "payload_hash": "sha256:aabbcc001",
    "authority_token": "tok-valid-001",
    "expiry": "2099-12-31T23:59:59Z",
    "nonce": "nonce-cc-001",
    "state_version": "v1.0.0",
}

TRUSTED_SCOPE    = "external:partner-domain.com"
TRUSTED_PAYLOAD  = "sha256:aabbcc001"
TRUSTED_STATE    = "v1.0.0"
EXPIRY_THRESHOLD = "2026-01-01T00:00:00Z"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _receipt(attempt, decision, refusal_reason, changed_condition,
             expected_value, actual_value, mutation_committed=False,
             previous_receipt_hash=None):
    r = {
        "receipt_id": f"RCP-CC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "scenario_id": "ESP-CC-001",
        "attempted_action": attempt.get("action_type", "UNKNOWN"),
        "actor": attempt.get("actor", "UNKNOWN"),
        "authority_token_ref": attempt.get("authority_token", "MISSING"),
        "recipient_scope": attempt.get("recipient_scope", "UNKNOWN"),
        "payload_hash": attempt.get("payload_hash", "UNKNOWN"),
        "state_version": attempt.get("state_version", "UNKNOWN"),
        "changed_condition": changed_condition,
        "expected_value": expected_value,
        "actual_value": actual_value,
        "decision": decision,
        "refusal_reason": refusal_reason,
        "mutation_committed": mutation_committed,
        "timestamp": _ts(),
    }
    if previous_receipt_hash is not None:
        r["previous_receipt_hash"] = previous_receipt_hash
    return r


def changed_condition_gate(attempt: dict) -> dict:
    """
    CommitGate — changed-condition variant.
    Checks scope, payload hash, state version, and expiry against trusted baseline.
    Returns decision, refusal_reason, receipt, and mutation_committed.
    NOTE: previous_receipt_hash is optional in this proof surface.
    Full receipt-chain continuity is a separate proof concern.
    """
    scope   = attempt.get("recipient_scope", "")
    payload = attempt.get("payload_hash", "")
    state   = attempt.get("state_version", "")
    expiry  = attempt.get("expiry", "")
    token   = attempt.get("authority_token")

    if not token:
        r = _receipt(attempt, "DENY", "authority_token absent",
                     "authority_token", "present", "missing")
        return {"decision": "DENY", "refusal_reason": "authority_token absent",
                "receipt": r, "mutation_committed": False}

    if expiry <= EXPIRY_THRESHOLD:
        r = _receipt(attempt, "REFUSE_AUTHORITY_EXPIRED",
                     "authority token expired at gate time",
                     "expiry", f"> {EXPIRY_THRESHOLD}", expiry)
        return {"decision": "REFUSE_AUTHORITY_EXPIRED",
                "refusal_reason": "authority token expired at gate time",
                "receipt": r, "mutation_committed": False}

    if scope != TRUSTED_SCOPE:
        r = _receipt(attempt, "REFUSE_SCOPE_MISMATCH",
                     "recipient_scope does not match authority scope",
                     "recipient_scope", TRUSTED_SCOPE, scope)
        return {"decision": "REFUSE_SCOPE_MISMATCH",
                "refusal_reason": "recipient_scope does not match authority scope",
                "receipt": r, "mutation_committed": False}

    if payload != TRUSTED_PAYLOAD:
        r = _receipt(attempt, "REFUSE_PAYLOAD_HASH_MISMATCH",
                     "payload_hash does not match authorised payload",
                     "payload_hash", TRUSTED_PAYLOAD, payload)
        return {"decision": "REFUSE_PAYLOAD_HASH_MISMATCH",
                "refusal_reason": "payload_hash does not match authorised payload",
                "receipt": r, "mutation_committed": False}

    if state != TRUSTED_STATE:
        r = _receipt(attempt, "REFUSE_STATE_VERSION_MISMATCH",
                     "state_version changed since authority was granted",
                     "state_version", TRUSTED_STATE, state)
        return {"decision": "REFUSE_STATE_VERSION_MISMATCH",
                "refusal_reason": "state_version changed since authority was granted",
                "receipt": r, "mutation_committed": False}

    r = _receipt(attempt, "ALLOW", "", "none", "all conditions unchanged",
                 "all conditions unchanged", mutation_committed=False)
    return {"decision": "ALLOW", "refusal_reason": None,
            "receipt": r, "mutation_committed": False}


# ── Fixtures ──────────────────────────────────────────────────────────────────

PAYLOAD_CHANGED = {**BASELINE, "payload_hash": "sha256:zzxxzz999", "nonce": "nonce-cc-002"}
SCOPE_CHANGED   = {**BASELINE, "recipient_scope": "external:unauthorised-domain.com", "nonce": "nonce-cc-003"}
STATE_CHANGED   = {**BASELINE, "state_version": "v2.0.0", "nonce": "nonce-cc-004"}
EXPIRED         = {**BASELINE, "expiry": "2020-01-01T00:00:00Z", "nonce": "nonce-cc-005"}


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_unchanged_conditions_allow():
    """Baseline: all conditions match → ALLOW."""
    result = changed_condition_gate(copy.deepcopy(BASELINE))
    assert result["decision"] == "ALLOW"
    assert result["mutation_committed"] is False


def test_payload_changed_refuses():
    """Payload hash changed → REFUSE_PAYLOAD_HASH_MISMATCH, no mutation."""
    result = changed_condition_gate(copy.deepcopy(PAYLOAD_CHANGED))
    assert result["decision"] == "REFUSE_PAYLOAD_HASH_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "payload_hash"
    assert result["receipt"]["actual_value"] == PAYLOAD_CHANGED["payload_hash"]
    assert result["receipt"]["expected_value"] == TRUSTED_PAYLOAD


def test_scope_changed_refuses():
    """Recipient scope changed → REFUSE_SCOPE_MISMATCH, no mutation."""
    result = changed_condition_gate(copy.deepcopy(SCOPE_CHANGED))
    assert result["decision"] == "REFUSE_SCOPE_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "recipient_scope"


def test_state_version_changed_refuses():
    """State version changed → REFUSE_STATE_VERSION_MISMATCH, no mutation."""
    result = changed_condition_gate(copy.deepcopy(STATE_CHANGED))
    assert result["decision"] == "REFUSE_STATE_VERSION_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "state_version"


def test_expired_authority_refuses():
    """Authority token expired → REFUSE_AUTHORITY_EXPIRED, no mutation."""
    result = changed_condition_gate(copy.deepcopy(EXPIRED))
    assert result["decision"] == "REFUSE_AUTHORITY_EXPIRED"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "expiry"


def test_receipt_contains_required_fields():
    """Every refusal receipt contains all required fields."""
    required = [
        "receipt_id", "scenario_id", "attempted_action", "actor",
        "authority_token_ref", "recipient_scope", "payload_hash",
        "state_version", "changed_condition", "expected_value",
        "actual_value", "decision", "refusal_reason",
        "mutation_committed", "timestamp",
    ]
    for fixture in [PAYLOAD_CHANGED, SCOPE_CHANGED, STATE_CHANGED, EXPIRED]:
        result = changed_condition_gate(copy.deepcopy(fixture))
        receipt = result["receipt"]
        for field in required:
            assert field in receipt, f"Receipt missing field: {field} (fixture: {fixture['nonce']})"
        assert receipt["mutation_committed"] is False


def test_changed_condition_replay_is_stable():
    """
    Replay stability: same changed-condition attempt run twice must produce
    same decision class, same refusal reason, mutation_committed false both times.
    """
    for fixture in [PAYLOAD_CHANGED, SCOPE_CHANGED, STATE_CHANGED, EXPIRED]:
        first  = changed_condition_gate(copy.deepcopy(fixture))
        replay = changed_condition_gate(copy.deepcopy(fixture))
        assert first["decision"] == replay["decision"], (
            f"Replay decision mismatch for {fixture['nonce']}: "
            f"{first['decision']} vs {replay['decision']}"
        )
        assert first["refusal_reason"] == replay["refusal_reason"], (
            f"Replay refusal_reason mismatch for {fixture['nonce']}"
        )
        assert first["mutation_committed"] is False
        assert replay["mutation_committed"] is False
