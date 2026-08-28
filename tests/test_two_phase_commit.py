from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.commit_gate_core.hmac_mac import HmacSha256Verifier
from src.commit_gate_core.two_phase import TwoPhaseCommit


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class InMemoryNonceLedger:
    def __init__(self) -> None:
        self.used: set[str] = set()

    def contains(self, nonce: str) -> bool:
        return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> None:
        if nonce in self.used:
            raise RuntimeError("nonce already consumed")
        self.used.add(nonce)

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.used.discard(nonce)


class RecordingAuditSink:
    def __init__(self, fail_on: str | None = None) -> None:
        self.events: list[Mapping[str, Any]] = []
        self.fail_on = fail_on

    def append(self, event: Mapping[str, Any]) -> None:
        if self.fail_on and event.get("event_type") == self.fail_on:
            raise IOError("audit down")
        self.events.append(event)


def mutation_spy():
    calls: list[Mapping[str, Any]] = []

    def mutate(record: Mapping[str, Any]) -> None:
        calls.append(record)

    return mutate, calls


KEY = b"lab-key-not-for-production"


def signed_record(verifier: HmacSha256Verifier, **overrides: str) -> dict[str, str]:
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
        "signature": "",
    }
    record.update(overrides)
    record["signature"] = verifier.sign(record)
    return record


def make_gate(*, audit=None, ledger=None, mutation=None):
    verifier = HmacSha256Verifier(KEY)
    audit = audit or RecordingAuditSink()
    ledger = ledger or InMemoryNonceLedger()
    if mutation is None:
        mutation, calls = mutation_spy()
    else:
        calls = []
    gate = TwoPhaseCommit(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=mutation,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, ledger, audit, calls, verifier


SCOPE = dict(
    actor_id="agent_17",
    action="approve_invoice",
    object_id="invoice_778",
    environment="prod",
    commit_hash="sha256:abc123",
)


def test_prepare_does_not_mutate():
    gate, ledger, audit, calls, verifier = make_gate()
    result = gate.prepare(record=signed_record(verifier), **SCOPE)
    assert result.phase == "PREPARED"
    assert result.allowed is False
    assert result.world_changed is False
    assert calls == []
    assert "nonce_001" in ledger.used
    assert audit.events[0]["event_type"] == "GATE_PREPARED"


def test_apply_commits_and_mutates_once():
    gate, ledger, audit, calls, verifier = make_gate()
    prepared = gate.prepare(record=signed_record(verifier), **SCOPE)
    applied = gate.apply(prepared.ticket)
    assert applied.phase == "COMMITTED"
    assert applied.allowed is True
    assert applied.world_changed is True
    assert len(calls) == 1
    second = gate.apply(prepared.ticket)
    assert second.allowed is False
    assert "TICKET_NOT_PREPARED" in second.code


def test_prepare_audit_failure_does_not_spend_or_mutate():
    gate, ledger, audit, calls, verifier = make_gate(
        audit=RecordingAuditSink(fail_on="GATE_PREPARED")
    )
    result = gate.prepare(record=signed_record(verifier), **SCOPE)
    assert result.world_changed is False
    assert "PREPARE_AUDIT_FAILED" in result.code
    assert ledger.used == set()
    assert calls == []


def test_commit_audit_failure_does_not_pretend_noop():
    gate, ledger, audit, calls, verifier = make_gate(
        audit=RecordingAuditSink(fail_on="GATE_COMMITTED")
    )
    prepared = gate.prepare(record=signed_record(verifier), **SCOPE)
    applied = gate.apply(prepared.ticket)
    assert applied.phase == "UNRECEIPTED"
    assert applied.allowed is False
    assert applied.world_changed is True
    assert len(calls) == 1
    assert "nonce_001" in ledger.used


def test_bad_hmac_never_prepares():
    gate, ledger, audit, calls, verifier = make_gate()
    record = signed_record(verifier)
    record["signature"] = "hmac-sha256:" + ("00" * 32)
    result = gate.prepare(record=record, **SCOPE)
    assert result.phase == "REFUSED"
    assert result.code == "DENY:INVALID_SIGNATURE"
    assert calls == []
    assert ledger.used == set()


def test_apply_mutation_failure_rolls_back_nonce():
    def boom(record: Mapping[str, Any]) -> None:
        raise RuntimeError("disk")

    gate, ledger, audit, calls, verifier = make_gate(mutation=boom)
    prepared = gate.prepare(record=signed_record(verifier), **SCOPE)
    applied = gate.apply(prepared.ticket)
    assert applied.phase == "ABORTED"
    assert applied.world_changed is False
    assert "nonce_001" not in ledger.used
