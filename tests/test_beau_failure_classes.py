"""Negative regressions for the retired mutation contract.

These tests previously encoded: execute may change the world, then misreport.
The supported contract is the opposite.
"""

from __future__ import annotations

from datetime import datetime, timezone

from commit_gate_core.authorize import payload_hash
from commit_gate_core.gate import CommitGate
from commit_gate_core.hmac_mac import HmacSha256Verifier

PAYLOAD = b"invoice-body"
KEY = b"lab-key-not-for-production"


class MemoryNonceLedger:
    def __init__(self):
        self.consumed = set()

    def contains(self, nonce):
        return nonce in self.consumed

    def consume(self, nonce, decision_id):
        self.consumed.add(nonce)

    def rollback(self, nonce, decision_id):
        self.consumed.discard(nonce)


class MemoryAudit:
    def __init__(self, fail_on=None):
        self.events = []
        self.fail_on = fail_on

    def append(self, event):
        if self.fail_on and event.get("event_type") == self.fail_on:
            raise RuntimeError("audit unavailable")
        self.events.append(dict(event))


class FixedClock:
    def now(self):
        return datetime(2026, 5, 4, 12, 0, 0, tzinfo=timezone.utc)


def signed_record(verifier):
    record = {
        "decision_id": "decision-1",
        "actor_id": "actor-1",
        "action": "email.send",
        "object_id": "user@example.com",
        "environment": "demo",
        "commit_hash": payload_hash(PAYLOAD),
        "verdict": "ALLOW",
        "policy_version": "v1",
        "issued_at": "2026-05-04T11:00:00Z",
        "expires_at": "2026-05-04T13:00:00Z",
        "nonce": "nonce-1",
        "signature": "",
    }
    record["signature"] = verifier.sign(record)
    return record


def make_gate(audit=None):
    verifier = HmacSha256Verifier(KEY)
    effects = []

    def mutate(record):
        effects.append(("sent", record.get("object_id")))

    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=MemoryNonceLedger(),
        audit=audit or MemoryAudit(),
        mutation_callback=mutate,
        accepted_policy_versions=("v1",),
        clock=FixedClock(),
    )
    return gate, effects, verifier


SCOPE = dict(
    actor_id="actor-1",
    action="email.send",
    object_id="user@example.com",
    environment="demo",
)


def test_execute_cannot_mutate_on_authorize_path():
    gate, effects, verifier = make_gate()
    result = gate.execute(record=signed_record(verifier), payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is True
    assert result.code == "AUTHORIZED"
    assert effects == []


def test_commit_hash_only_fails_closed_and_does_not_mutate():
    gate, effects, verifier = make_gate()
    result = gate.execute(
        record=signed_record(verifier),
        commit_hash=payload_hash(PAYLOAD),
        **SCOPE,
    )
    assert result.allowed is False
    assert result.code == "DENY:COMMIT_HASH_ONLY_FORBIDDEN"
    assert effects == []


def test_payload_binding_happens_inside_authorize():
    gate, effects, verifier = make_gate()
    result = gate.authorize(signed_record(verifier), b"other-bytes", **SCOPE)
    assert result.authorized is False
    assert result.code == "DENY:PAYLOAD_HASH_MISMATCH"
    assert effects == []


def test_audit_failure_leaves_world_unchanged():
    gate, effects, verifier = make_gate(audit=MemoryAudit(fail_on="GATE_AUTHORIZED"))
    result = gate.execute(record=signed_record(verifier), payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is False
    assert "AUTH_AUDIT_FAILED" in result.code
    assert effects == []
