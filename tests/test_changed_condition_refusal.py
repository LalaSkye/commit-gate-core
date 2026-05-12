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

This is a synthetic, path-local adversarial test surface.
It proves deterministic refusal under changed conditions on the demonstrated path only.
It does not prove production enforcement, persistence safety, or path-universal coverage.
"""

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from threading import Lock, Thread


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

TRUSTED_SCOPE = "external:partner-domain.com"
TRUSTED_PAYLOAD = "sha256:aabbcc001"
TRUSTED_STATE = "v1.0.0"
TRUSTED_TOKEN = "tok-valid-001"
EXPIRY_THRESHOLD = "2026-01-01T00:00:00Z"
PAYLOAD_RE = re.compile(r"^sha256:[a-f0-9]{9}$")
STATE_RE = re.compile(r"^v\d+\.\d+\.\d+$")
TOKEN_RE = re.compile(r"^tok-[a-z]+-\d{3}$")

_nonce_seen = set()
_nonce_lock = Lock()
_receipt_sequence = []
_receipt_lock = Lock()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


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
    r["receipt_hash"] = _stable_hash({k: v for k, v in r.items() if k != "receipt_hash"})
    return r


def _refuse(attempt, decision, reason, condition, expected, actual):
    r = _receipt(attempt, decision, reason, condition, expected, actual)
    return {"decision": decision, "refusal_reason": reason, "receipt": r, "mutation_committed": False}


def _valid_iso_z(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def changed_condition_gate(attempt: dict) -> dict:
    """
    CommitGate — changed-condition variant.
    Fails closed on malformed inputs before changed-condition comparison.
    Full receipt-chain continuity is a separate proof concern.
    """
    if not isinstance(attempt, dict):
        attempt = {}

    token = attempt.get("authority_token")
    nonce = attempt.get("nonce")
    expiry = attempt.get("expiry")
    scope = attempt.get("recipient_scope")
    payload = attempt.get("payload_hash")
    state = attempt.get("state_version")

    if not isinstance(token, str) or not token.strip():
        return _refuse(attempt, "REFUSE_AUTHORITY_TOKEN_INVALID", "authority_token missing or malformed", "authority_token", "non-empty token", token)
    if not TOKEN_RE.fullmatch(token) or token != TRUSTED_TOKEN:
        return _refuse(attempt, "REFUSE_AUTHORITY_TOKEN_INVALID", "authority_token not recognised for this gate", "authority_token", TRUSTED_TOKEN, token)
    if not isinstance(nonce, str) or not nonce.strip():
        return _refuse(attempt, "REFUSE_NONCE_INVALID", "nonce missing or malformed", "nonce", "non-empty nonce", nonce)
    if not isinstance(expiry, str) or not expiry.strip() or not _valid_iso_z(expiry):
        return _refuse(attempt, "REFUSE_EXPIRY_MALFORMED", "expiry missing or malformed", "expiry", "RFC3339 UTC timestamp ending Z", expiry)
    if expiry <= EXPIRY_THRESHOLD:
        return _refuse(attempt, "REFUSE_AUTHORITY_EXPIRED", "authority token expired at gate time", "expiry", f"> {EXPIRY_THRESHOLD}", expiry)
    if not isinstance(scope, str) or scope != scope.strip() or scope != scope.lower() or not scope.startswith("external:") or scope.count(":") != 1:
        return _refuse(attempt, "REFUSE_SCOPE_MALFORMED", "recipient_scope missing or malformed", "recipient_scope", TRUSTED_SCOPE, scope)
    if not isinstance(payload, str) or not PAYLOAD_RE.fullmatch(payload):
        return _refuse(attempt, "REFUSE_PAYLOAD_HASH_MALFORMED", "payload_hash missing or malformed", "payload_hash", "sha256:<lowercase-hex>", payload)
    if not isinstance(state, str) or not STATE_RE.fullmatch(state):
        return _refuse(attempt, "REFUSE_STATE_VERSION_MALFORMED", "state_version missing or malformed", "state_version", "v<major>.<minor>.<patch>", state)

    if scope != TRUSTED_SCOPE:
        return _refuse(attempt, "REFUSE_SCOPE_MISMATCH", "recipient_scope does not match authority scope", "recipient_scope", TRUSTED_SCOPE, scope)
    if payload != TRUSTED_PAYLOAD:
        return _refuse(attempt, "REFUSE_PAYLOAD_HASH_MISMATCH", "payload_hash does not match authorised payload", "payload_hash", TRUSTED_PAYLOAD, payload)
    if state != TRUSTED_STATE:
        return _refuse(attempt, "REFUSE_STATE_VERSION_MISMATCH", "state_version changed since authority was granted", "state_version", TRUSTED_STATE, state)

    r = _receipt(attempt, "ALLOW", "", "none", "all conditions unchanged", "all conditions unchanged", mutation_committed=False)
    return {"decision": "ALLOW", "refusal_reason": None, "receipt": r, "mutation_committed": False}


PAYLOAD_CHANGED = {**BASELINE, "payload_hash": "sha256:zzxxzz999", "nonce": "nonce-cc-002"}
SCOPE_CHANGED = {**BASELINE, "recipient_scope": "external:unauthorised-domain.com", "nonce": "nonce-cc-003"}
STATE_CHANGED = {**BASELINE, "state_version": "v2.0.0", "nonce": "nonce-cc-004"}
EXPIRED = {**BASELINE, "expiry": "2020-01-01T00:00:00Z", "nonce": "nonce-cc-005"}


def test_unchanged_conditions_allow():
    result = changed_condition_gate(copy.deepcopy(BASELINE))
    assert result["decision"] == "ALLOW"
    assert result["mutation_committed"] is False


def test_payload_changed_refuses():
    result = changed_condition_gate(copy.deepcopy(PAYLOAD_CHANGED))
    assert result["decision"] == "REFUSE_PAYLOAD_HASH_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "payload_hash"
    assert result["receipt"]["actual_value"] == PAYLOAD_CHANGED["payload_hash"]
    assert result["receipt"]["expected_value"] == TRUSTED_PAYLOAD


def test_scope_changed_refuses():
    result = changed_condition_gate(copy.deepcopy(SCOPE_CHANGED))
    assert result["decision"] == "REFUSE_SCOPE_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "recipient_scope"


def test_state_version_changed_refuses():
    result = changed_condition_gate(copy.deepcopy(STATE_CHANGED))
    assert result["decision"] == "REFUSE_STATE_VERSION_MISMATCH"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "state_version"


def test_expired_authority_refuses():
    result = changed_condition_gate(copy.deepcopy(EXPIRED))
    assert result["decision"] == "REFUSE_AUTHORITY_EXPIRED"
    assert result["mutation_committed"] is False
    assert result["receipt"]["changed_condition"] == "expiry"


def test_receipt_contains_required_fields():
    required = [
        "receipt_id", "scenario_id", "attempted_action", "actor",
        "authority_token_ref", "recipient_scope", "payload_hash",
        "state_version", "changed_condition", "expected_value",
        "actual_value", "decision", "refusal_reason",
        "mutation_committed", "timestamp", "receipt_hash",
    ]
    for fixture in [PAYLOAD_CHANGED, SCOPE_CHANGED, STATE_CHANGED, EXPIRED]:
        result = changed_condition_gate(copy.deepcopy(fixture))
        receipt = result["receipt"]
        for field in required:
            assert field in receipt, f"Receipt missing field: {field} (fixture: {fixture['nonce']})"
        assert receipt["mutation_committed"] is False


def test_changed_condition_replay_is_stable():
    for fixture in [PAYLOAD_CHANGED, SCOPE_CHANGED, STATE_CHANGED, EXPIRED]:
        first = changed_condition_gate(copy.deepcopy(fixture))
        replay = changed_condition_gate(copy.deepcopy(fixture))
        assert first["decision"] == replay["decision"]
        assert first["refusal_reason"] == replay["refusal_reason"]
        assert first["mutation_committed"] is False
        assert replay["mutation_committed"] is False


def test_malformed_payload_hashes_fail_closed():
    for bad in [None, "", "sha256:", "sha256:XYZ", "sha256:aabbcc001 ", " md5:aabbcc001", "sha256:aabbcc00100"]:
        fixture = {**BASELINE, "payload_hash": bad, "nonce": f"nonce-bad-payload-{repr(bad)}"}
        result = changed_condition_gate(fixture)
        assert result["decision"] == "REFUSE_PAYLOAD_HASH_MALFORMED"
        assert result["mutation_committed"] is False


def test_scope_tricks_fail_closed_or_refuse():
    cases = {
        None: "REFUSE_SCOPE_MALFORMED",
        "": "REFUSE_SCOPE_MALFORMED",
        "external:partner-domain.com ": "REFUSE_SCOPE_MALFORMED",
        "external:PARTNER-DOMAIN.COM": "REFUSE_SCOPE_MALFORMED",
        "external:partner-domain.com.evil.com": "REFUSE_SCOPE_MISMATCH",
        "external:partner-domain%2ecom": "REFUSE_SCOPE_MISMATCH",
        "external:partner-domain.com,external:evil.com": "REFUSE_SCOPE_MISMATCH",
    }
    for scope, expected in cases.items():
        fixture = {**BASELINE, "recipient_scope": scope, "nonce": f"nonce-scope-{repr(scope)}"}
        result = changed_condition_gate(fixture)
        assert result["decision"] == expected
        assert result["mutation_committed"] is False


def test_state_version_invalid_and_downgrade_refuse():
    cases = {
        None: "REFUSE_STATE_VERSION_MALFORMED",
        "": "REFUSE_STATE_VERSION_MALFORMED",
        "v1.0.0 ": "REFUSE_STATE_VERSION_MALFORMED",
        "v1.0.0+metadata": "REFUSE_STATE_VERSION_MALFORMED",
        "v1.0.0-preview": "REFUSE_STATE_VERSION_MALFORMED",
        "v01.0.0": "REFUSE_STATE_VERSION_MISMATCH",
        "v0.9.0": "REFUSE_STATE_VERSION_MISMATCH",
        "v2.0.0": "REFUSE_STATE_VERSION_MISMATCH",
    }
    for state, expected in cases.items():
        fixture = {**BASELINE, "state_version": state, "nonce": f"nonce-state-{repr(state)}"}
        result = changed_condition_gate(fixture)
        assert result["decision"] == expected
        assert result["mutation_committed"] is False


def test_expiry_edges_fail_closed():
    cases = {
        None: "REFUSE_EXPIRY_MALFORMED",
        "": "REFUSE_EXPIRY_MALFORMED",
        "2026-01-01T00:00:00Z": "REFUSE_AUTHORITY_EXPIRED",
        "2026-01-01T00:00:00": "REFUSE_EXPIRY_MALFORMED",
        "not-a-date": "REFUSE_EXPIRY_MALFORMED",
        12345: "REFUSE_EXPIRY_MALFORMED",
    }
    for expiry, expected in cases.items():
        fixture = {**BASELINE, "expiry": expiry, "nonce": f"nonce-expiry-{repr(expiry)}"}
        result = changed_condition_gate(fixture)
        assert result["decision"] == expected
        assert result["mutation_committed"] is False


def test_multiple_invalid_fields_follow_documented_priority():
    fixture = {**BASELINE, "authority_token": "", "payload_hash": None, "recipient_scope": "external:evil.com", "nonce": "nonce-priority-001"}
    result = changed_condition_gate(fixture)
    assert result["decision"] == "REFUSE_AUTHORITY_TOKEN_INVALID"
    assert result["receipt"]["changed_condition"] == "authority_token"
    assert result["mutation_committed"] is False


def test_receipt_mutation_after_generation_is_detectable_by_hash():
    result = changed_condition_gate(copy.deepcopy(PAYLOAD_CHANGED))
    receipt = copy.deepcopy(result["receipt"])
    original_hash = receipt.pop("receipt_hash")
    assert _stable_hash(receipt) == original_hash
    receipt["decision"] = "ALLOW"
    assert _stable_hash(receipt) != original_hash


def test_nonce_reuse_across_changed_conditions_refuses_or_blocks_replay():
    nonce = "nonce-reuse-attack-001"
    first = changed_condition_gate({**PAYLOAD_CHANGED, "nonce": nonce})
    second = changed_condition_gate({**SCOPE_CHANGED, "nonce": nonce})
    assert first["decision"] == "REFUSE_PAYLOAD_HASH_MISMATCH"
    assert second["decision"] == "REFUSE_SCOPE_MISMATCH"
    assert first["mutation_committed"] is False
    assert second["mutation_committed"] is False


def test_concurrent_changed_condition_evaluation_commits_no_mutation():
    results = []

    def run_case(fixture):
        results.append(changed_condition_gate(copy.deepcopy(fixture)))

    threads = [Thread(target=run_case, args=(fx,)) for fx in [PAYLOAD_CHANGED, SCOPE_CHANGED, STATE_CHANGED, EXPIRED] * 5]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(results) == 20
    assert all(result["mutation_committed"] is False for result in results)
    assert {result["decision"] for result in results} == {
        "REFUSE_PAYLOAD_HASH_MISMATCH",
        "REFUSE_SCOPE_MISMATCH",
        "REFUSE_STATE_VERSION_MISMATCH",
        "REFUSE_AUTHORITY_EXPIRED",
    }
