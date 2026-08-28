from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.commit_gate_core.authorize import payload_hash
from src.commit_gate_core.gate import CommitGate
from src.commit_gate_core.hmac_mac import HmacSha256Verifier

PAYLOAD = b"kernel-payload"
KEY = b"lab-key-not-for-production"


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class InMemoryNonceLedger:
    def __init__(self) -> None:
        self.used: set[str] = set()
        self.consume_calls = 0

    def contains(self, nonce: str) -> bool:
        return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> None:
        self.consume_calls += 1
        if nonce in self.used:
            raise RuntimeError("nonce already consumed")
        self.used.add(nonce)

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.used.discard(nonce)


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[Mapping[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(event)


def mutation_spy():
    calls: list[Mapping[str, Any]] = []

    def mutate(record: Mapping[str, Any]) -> None:
        calls.append(record)

    return mutate, calls


def signed_record(verifier: HmacSha256Verifier, **overrides: str) -> dict[str, str]:
    record = {
        "decision_id": "dr_001",
        "actor_id": "agent_17",
        "action": "approve_invoice",
        "object_id": "invoice_778",
        "environment": "prod",
        "commit_hash": payload_hash(PAYLOAD),
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


def make_gate(*):
    verifier = HmacSha256Verifier(KEY)
    audit = RecordingAuditSink()
    ledger = InMemoryNonceLedger()
    mutation, mutation_calls = mutation_spy()
    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=mutation,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, ledger, audit, mutation_calls, verifier


SCOPE = dict(
    actor_id="agent_17",
    action="approve_invoice",
    object_id="invoice_778",
    environment="prod",
)


def test_no_record_blocks():
    gate, ledger, audit, mutation_calls, verifier = make_gate()
    result = gate.execute(record=None, payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is False
    assert result.code == "DENY:NO_DECISION_RECORD"
    assert mutation_calls == []
    assert ledger.used == set()


def test_bad_mac_blocks():
    gate, ledger, audit, mutation_calls, verifier = make_gate()
    record = signed_record(verifier)
    record["signature"] = "hmac-sha256:" + ("00" * 32)
    result = gate.execute(record=record, payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is False
    assert result.code == "DENY:INVALID_SIGNATURE"
    assert mutation_calls == []


def test_expired_blocks():
    gate, ledger, audit, mutation_calls, verifier = make_gate()
    record = signed_record(verifier, expires_at="2026-04-27T05:00:30Z")
    # clock is 05:01, expires 05:00:30
    result = gate.execute(record=record, payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is False
    assert result.code == "DENY:DECISION_EXPIRED"
    assert mutation_calls == []


def test_scope_mismatch_blocks():
    gate, ledger, audit, mutation_calls, verifier = make_gate()
    record = signed_record(verifier, object_id="invoice_999")
    result = gate.execute(record=record, payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is False
    assert "SCOPE_MISMATCH" in result.code
    assert mutation_calls == []


def test_success_does_not_mutate():
    gate, ledger, audit, mutation_calls, verifier = make_gate()
    record = signed_record(verifier)
    first = gate.execute(record=record, payload_bytes=PAYLOAD, **SCOPE)
    second = gate.execute(record=record, payload_bytes=PAYLOAD, **SCOPE)
    assert first.allowed is True
    assert first.code == "AUTHORIZED"
    assert second.allowed is False
    assert second.code == "DENY:NONCE_REPLAYED"
    assert mutation_calls == []
    assert ledger.used == {"nonce_001"}
