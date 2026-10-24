"""CCG-T02e M08 post-verification regression.
Test-only. Kernel unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.commit_gate_core.authorize import payload_hash
from src.commit_gate_core.gate import CommitGate
from src.commit_gate_core.hmac_mac import HmacSha256Verifier


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

    def consume(self, nonce: str, decision_id: str) -> bool:
        if nonce in self.used:
            return False
        self.used.add(nonce)
        return True

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.used.discard(nonce)


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[Mapping[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(event)


class FieldRemovingVerifier:
    def __init__(self, delegate: HmacSha256Verifier) -> None:
        self._delegate = delegate

    def verify(self, record: Mapping[str, Any]) -> bool:
        verified = self._delegate.verify(record)
        if isinstance(record, dict):
            record.pop("object_id", None)
        return verified


KEY = b"lab-key-not-for-production"
PAYLOAD = b"invoice-778-body"


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


def make_gate(*, verifier):
    audit = RecordingAuditSink()
    ledger = InMemoryNonceLedger()
    mutated = []

    def boom(record: Mapping[str, Any]) -> None:
        mutated.append(record)

    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=boom,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, mutated, audit


def test_verifier_removes_signed_field_is_refused():
    signer = HmacSha256Verifier(KEY)
    record = signed_record(signer)
    gate, mutated, audit = make_gate(verifier=FieldRemovingVerifier(signer))
    result = gate.authorize(
        record,
        PAYLOAD,
        actor_id="agent_17",
        action="approve_invoice",
        object_id="invoice_778",
        environment="prod",
    )
    assert result.authorized is False
    assert result.phase == "REFUSED"
    assert result.code == "DENY:VERIFIER_MUTATED_RECORD"
    assert result.ticket is None
    assert mutated == []
    refused = [e for e in audit.events if e.get("event_type") == "GATE_REFUSED"]
    assert len(refused) == 1
    assert refused[0]["code"] == "DENY:VERIFIER_MUTATED_RECORD"
