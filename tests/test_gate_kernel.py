from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import pytest

from src.commit_gate_core.gate import CommitGate


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeSignatureVerifier:
    def __init__(self, valid: bool = True) -> None:
        self.valid = valid
        self.calls = 0

    def verify(self, record: Mapping[str, Any]) -> bool:
        self.calls += 1
        return self.valid


class InMemoryNonceLedger:
    def __init__(self) -> None:
        self.used: set[str] = set()
        self.consume_calls = 0
        self.rollback_calls = 0

    def contains(self, nonce: str) -> bool:
        return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> None:
        self.consume_calls += 1
        if nonce in self.used:
            raise RuntimeError("nonce already consumed")
        self.used.add(nonce)

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.rollback_calls += 1
        self.used.discard(nonce)


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[Mapping[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(event)


def make_record(**overrides: Any) -> dict[str, str]:
    record = {
        "decision_id": "dr_001",
        "actor_id": "agent_17",
        "action": "approve_invoice",
        "object_id": "invoice_778",
        "environment": "prod",
        "commit_hash": "sha256:abc123",
        "verdict": "ALLOW",
        "policy_version": "2026-04-27.1",
        "issued_at": "2026-04-27T05:00:00Z",
        "expires_at": "2026-04-27T05:05:00Z",
        "nonce": "nonce_001",
        "signature": "sig_valid",
    }
    record.update(overrides)
    return record


def mutation_spy():
    calls: list[Mapping[str, Any]] = []

    def mutate(record: Mapping[str, Any]) -> None:
        calls.append(record)

    return mutate, calls


def make_gate(
    *,
    verifier_valid: bool = True,
    ledger: InMemoryNonceLedger | None = None,
    audit: RecordingAuditSink | None = None,
    mutation=None,
    now: datetime | None = None,
):
    audit = audit or RecordingAuditSink()
    ledger = ledger or InMemoryNonceLedger()
    mutation, mutation_calls = (mutation or mutation_spy())
    gate = CommitGate(
        verifier=FakeSignatureVerifier(verifier_valid),
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=mutation,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(now or datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, ledger, audit, mutation_calls


def execute_valid_shape(gate: CommitGate, record: Mapping[str, Any] | None):
    return gate.execute(
        record=record,
        actor_id="agent_17",
        action="approve_invoice",
        object_id="invoice_778",
        environment="prod",
        commit_hash="sha256:abc123",
    )


def test_no_record_blocks():
    gate, ledger, audit, mutation_calls = make_gate()

    result = execute_valid_shape(gate, None)

    assert result.allowed is False
    assert result.code == "DENY:NO_DECISION_RECORD"
    assert result.decision_id is None
    assert mutation_calls == []
    assert ledger.used == set()
    assert ledger.consume_calls == 0
    assert len(audit.events) == 1
    assert audit.events[0]["code"] == result.code


def test_bad_signature_blocks():
    gate, ledger, audit, mutation_calls = make_gate(verifier_valid=False)
    record = make_record()

    result = execute_valid_shape(gate, record)

    assert result.allowed is False
    assert result.code == "DENY:INVALID_SIGNATURE"
    assert result.decision_id == "dr_001"
    assert mutation_calls == []
    assert ledger.used == set()
    assert ledger.consume_calls == 0
    assert len(audit.events) == 1
    assert audit.events[0]["code"] == result.code


def test_expired_blocks():
    gate, ledger, audit, mutation_calls = make_gate(
        now=datetime(2026, 4, 27, 5, 6, tzinfo=timezone.utc)
    )
    record = make_record()

    result = execute_valid_shape(gate, record)

    assert result.allowed is False
    assert result.code == "DENY:DECISION_EXPIRED"
    assert result.decision_id == "dr_001"
    assert mutation_calls == []
    assert ledger.used == set()
    assert ledger.consume_calls == 0
    assert len(audit.events) == 1
    assert audit.events[0]["code"] == result.code


def test_scope_mismatch_blocks():
    gate, ledger, audit, mutation_calls = make_gate()
    record = make_record(object_id="invoice_999")

    result = execute_valid_shape(gate, record)

    assert result.allowed is False
    assert result.code == "DENY:SCOPE_MISMATCH:object_id"
    assert result.decision_id == "dr_001"
    assert mutation_calls == []
    assert ledger.used == set()
    assert ledger.consume_calls == 0
    assert len(audit.events) == 1
    assert audit.events[0]["code"] == result.code


def test_replay_blocks():
    ledger = InMemoryNonceLedger()
    ledger.used.add("nonce_001")
    gate, ledger, audit, mutation_calls = make_gate(ledger=ledger)
    record = make_record()

    result = execute_valid_shape(gate, record)

    assert result.allowed is False
    assert result.code == "DENY:NONCE_REPLAYED"
    assert result.decision_id == "dr_001"
    assert mutation_calls == []
    assert ledger.used == {"nonce_001"}
    assert ledger.consume_calls == 0
    assert len(audit.events) == 1
    assert audit.events[0]["code"] == result.code


def test_success_allows_once():
    fixed_now = datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)
    gate, ledger, audit, mutation_calls = make_gate(now=fixed_now)
    record = make_record()

    first = execute_valid_shape(gate, record)
    second = execute_valid_shape(gate, record)

    assert first.allowed is True
    assert first.code == "ALLOW"
    assert first.decision_id == "dr_001"
    assert first.timestamp == "2026-04-27T05:01:00Z"

    assert second.allowed is False
    assert second.code == "DENY:NONCE_REPLAYED"
    assert second.decision_id == "dr_001"

    assert mutation_calls == [record]
    assert ledger.used == {"nonce_001"}
    assert ledger.consume_calls == 1
    assert len(audit.events) == 2
    assert audit.events[0]["code"] == "ALLOW"
    assert audit.events[1]["code"] == "DENY:NONCE_REPLAYED"
