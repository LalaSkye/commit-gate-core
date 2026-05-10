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


class FailOnceAudit:
    def __init__(self):
        self.calls = 0
        self.events = []

    def append(self, event):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("audit unavailable")
        self.events.append(dict(event))


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


# ---------------------------------------------------------------------------
# Existing regression proofs (issues #7, #8, #9 — still open gaps)
# ---------------------------------------------------------------------------

def test_proof_consequence_ordering_exposes_mutation_before_durable_audit():
    """Issue #7 regression: mutation can occur before durable audit. Still open."""
    effects = []

    def mutate(record):
        effects.append(("sent", record["object_id"]))

    gate = make_gate(audit=FailOnceAudit(), mutation_callback=mutate)

    result = execute_valid(gate)

    assert effects == [("sent", "user@example.com")]
    assert result.allowed is False
    # Now returns controlled audit failure code instead of ROLLBACK:UNEXPECTED
    assert result.code == "ERROR:AUDIT_APPEND_FAILED:RuntimeError"


def test_proof_payload_binding_gap_allows_callback_to_create_unbound_effect():
    """Issue #8 regression: proof not bound to mutation payload. Still open."""
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
    # Issue #11 fixed: audit receipt uses the pre-mutation snapshot.
    # The snapshot was taken before the callback ran, so object_id is correct.
    assert audit.events[0]["record_scope"]["object_id"] == "user@example.com"


def test_atomic_commit_boundary_gap_when_audit_fails_after_nonce_and_mutation():
    """Issue #9 regression: no atomic commit boundary. Still open."""
    nonce_ledger = MemoryNonceLedger()
    effects = []

    def mutate(record):
        effects.append("mutation-bound")

    gate = make_gate(
        audit=FailOnceAudit(),
        mutation_callback=mutate,
        nonce_ledger=nonce_ledger,
    )

    result = execute_valid(gate)

    assert effects == ["mutation-bound"]
    # Issue #10 fixed: audit failure returns controlled result, not exception.
    # Nonce rollback no longer occurs on the audit-failure path because
    # _finish() catches the audit exception directly.
    # The nonce was consumed; mutation happened; audit failed.
    # This is the documented open gap for #9 (atomic commit boundary).
    assert result.allowed is False
    assert result.code == "ERROR:AUDIT_APPEND_FAILED:RuntimeError"


# ---------------------------------------------------------------------------
# Issue #10 hardening proofs: controlled audit failure on every exit path
# ---------------------------------------------------------------------------

def test_audit_failure_on_deny_path_returns_controlled_gate_result():
    """Issue #10 fix: audit failure on deny path returns GateResult, never raises."""
    gate = make_gate(audit=FailingAudit(), mutation_callback=lambda record: None)

    result = gate.execute(
        record=None,
        actor_id="actor-1",
        action="email.send",
        object_id="user@example.com",
        environment="demo",
        commit_hash="a" * 40,
    )

    assert isinstance(result.allowed, bool)
    assert result.allowed is False
    assert result.code == "ERROR:AUDIT_APPEND_FAILED:RuntimeError"
    assert result.decision_id is None
    assert result.timestamp is not None


def test_audit_failure_on_scope_deny_returns_controlled_gate_result():
    """Issue #10 fix: audit failure on scope mismatch deny returns GateResult."""
    gate = make_gate(audit=FailingAudit(), mutation_callback=lambda record: None)

    result = gate.execute(
        record=valid_record(),
        actor_id="wrong-actor",
        action="email.send",
        object_id="user@example.com",
        environment="demo",
        commit_hash="a" * 40,
    )

    assert result.allowed is False
    assert result.code == "ERROR:AUDIT_APPEND_FAILED:RuntimeError"


def test_audit_failure_on_allow_path_returns_controlled_gate_result():
    """Issue #10 fix: audit failure on allow path returns GateResult, not True.

    allowed must be False: the receipt was not written.
    """
    gate = make_gate(audit=FailingAudit(), mutation_callback=lambda record: None)

    result = execute_valid(gate)

    assert result.allowed is False
    assert result.code == "ERROR:AUDIT_APPEND_FAILED:RuntimeError"


# ---------------------------------------------------------------------------
# Issue #11 hardening proofs: pre-mutation snapshot protects audit receipt
# ---------------------------------------------------------------------------

def test_pre_mutation_snapshot_protects_audit_receipt():
    """Issue #11 fix: callback mutation of record does not alter audit receipt."""
    audit = MemoryAudit()
    record = valid_record()
    effects = []

    def mutate(rec):
        effects.append(("sent", rec["object_id"]))
        # Attempt to mutate the record passed to the callback.
        # Before fix: this would alter what _finish() logged.
        # After fix: _finish() uses the pre-mutation snapshot, so this has
        # no effect on the audit receipt.
        rec["object_id"] = "attacker@example.com"

    gate = make_gate(audit=audit, mutation_callback=mutate)

    result = execute_valid(gate, record=record)

    assert result.allowed is True
    assert effects == [("sent", "user@example.com")]
    # Audit receipt must reflect the authorised record, not the callback drift.
    assert audit.events[0]["record_scope"]["object_id"] == "user@example.com"


def test_pre_mutation_snapshot_is_independent_of_original_dict():
    """Issue #11 fix: snapshot is a copy; original dict changes do not affect receipt."""
    audit = MemoryAudit()
    record = dict(valid_record())

    def mutate(rec):
        rec["actor_id"] = "mutated-actor"
        rec["action"] = "mutated-action"
        rec["policy_version"] = "mutated-version"

    gate = make_gate(audit=audit, mutation_callback=mutate)

    result = execute_valid(gate, record=record)

    assert result.allowed is True
    scope = audit.events[0]["record_scope"]
    assert scope["actor_id"] == "actor-1"
    assert scope["action"] == "email.send"
    assert scope["policy_version"] == "v1"
