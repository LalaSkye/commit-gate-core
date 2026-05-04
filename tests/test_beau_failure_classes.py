from __future__ import annotations

from datetime import datetime, timezone

from commit_gate_core.gate import CommitGate


class AcceptingVerifier:
    def verify(self, record):
        return True


class MemoryNonceLedger:
    def __init__(self):
        self.consumed = set()
        self.rolled_back = []

    def contains(self, nonce):
        return nonce in self.consumed

    def consume(self, nonce, decision_id):
        self.consumed.add(nonce)

    def rollback(self, nonce, decision_id):
        self.consumed.discard(nonce)
        self.rolled_back.append((nonce, decision_id))


class MemoryAudit:
    def __init__(self):
        self.events = []

    def append(self, event):
        self.events.append(dict(event))


class FailingAudit:
    def append(self, event):
        raise RuntimeError("audit unavailable")


class FixedClock:
    def now(self):
        return datetime(2026, 5, 4, 12, 0, 0, tzinfo=timezone.utc)


def valid_record(**overrides):
    record = {
        "decision_id": "decision-1",
        "actor_id": "actor-1",
        "action": "email.send",
        "object_id": "user@example.com",
        "environment": "demo",
        "commit_hash": "a" * 40,
        "verdict": "ALLOW",
        "policy_version": "v1",
        "issued_at": "2026-05-04T11:00:00Z",
        "expires_at": "2026-05-04T13:00:00Z",
        "nonce": "nonce-1",
        "signature": "sig-1",
    }
    record.update(overrides)
    return record


def make_gate(audit, mutation_callback, nonce_ledger=None):
    return CommitGate(
        verifier=AcceptingVerifier(),
        nonce_ledger=nonce_ledger or MemoryNonceLedger(),
        audit=audit,
        mutation_callback=mutation_callback,
        accepted_policy_versions=("v1",),
        clock=FixedClock(),
    )


def execute_valid(gate, record=None):
    record = record or valid_record()
    return gate.execute(
        record=record,
        actor_id="actor-1",
        action="email.send",
        object_id="user@example.com",
        environment="demo",
        commit_hash="a" * 40,
    )


def test_proof_consequence_ordering_exposes_mutation_before_durable_audit():
    effects = []

    def mutate(record):
        effects.append(("sent", record["object_id"]))

    gate = make_gate(audit=FailingAudit(), mutation_callback=mutate)

    result = execute_valid(gate)

    assert effects == [("sent", "user@example.com")]
    assert result.allowed is False
    assert result.code == "ERROR:UNEXPECTED:RuntimeError"


def test_proof_payload_binding_gap_allows_callback_to_create_unbound_effect():
    audit = MemoryAudit()
    effects = []

    def mutate(record):
        effects.append(
            {
                "authorised_object_id": record["object_id"],
                "actual_object_id": "attacker@example.com",
                "body": "unbound payload",
            }
        )

    gate = make_gate(audit=audit, mutation_callback=mutate)

    result = execute_valid(gate)

    assert result.allowed is True
    assert effects == [
        {
            "authorised_object_id": "user@example.com",
            "actual_object_id": "attacker@example.com",
            "body": "unbound payload",
        }
    ]
    assert audit.events[0]["record_scope"]["object_id"] == "user@example.com"


def test_atomic_commit_boundary_gap_when_audit_fails_after_nonce_and_mutation():
    nonce_ledger = MemoryNonceLedger()
    effects = []

    def mutate(record):
        effects.append("mutation-bound")

    gate = make_gate(
        audit=FailingAudit(),
        mutation_callback=mutate,
        nonce_ledger=nonce_ledger,
    )

    result = execute_valid(gate)

    assert effects == ["mutation-bound"]
    assert nonce_ledger.consumed == set()
    assert nonce_ledger.rolled_back == [("nonce-1", "decision-1")]
    assert result.allowed is False
    assert result.code == "ERROR:UNEXPECTED:RuntimeError"
