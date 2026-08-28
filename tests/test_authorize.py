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


def make_gate(*, audit=None):
    verifier = HmacSha256Verifier(KEY)
    audit = audit or RecordingAuditSink()
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
    return gate, ledger, audit, mutated, verifier


SCOPE = dict(
    actor_id="agent_17",
    action="approve_invoice",
    object_id="invoice_778",
    environment="prod",
)


def test_authorize_does_not_invoke_callback():
    gate, ledger, audit, mutated, verifier = make_gate()
    result = gate.authorize(signed_record(verifier), PAYLOAD, **SCOPE)
    assert result.authorized is True
    assert result.phase == "AUTHORIZED"
    assert result.code == "AUTHORIZED"
    assert mutated == []
    assert "nonce_001" in ledger.used


def test_execute_is_authorize_wrapper():
    gate, ledger, audit, mutated, verifier = make_gate()
    result = gate.execute(record=signed_record(verifier), payload_bytes=PAYLOAD, **SCOPE)
    assert result.allowed is True
    assert result.code == "AUTHORIZED"
    assert mutated == []


def test_payload_mismatch_refuses():
    gate, ledger, audit, mutated, verifier = make_gate()
    result = gate.authorize(signed_record(verifier), b"other", **SCOPE)
    assert result.authorized is False
    assert result.code == "DENY:PAYLOAD_HASH_MISMATCH"
    assert ledger.used == set()


def test_authorized_audit_failure_rolls_back_nonce():
    gate, ledger, audit, mutated, verifier = make_gate(
        audit=RecordingAuditSink(fail_on="GATE_AUTHORIZED")
    )
    result = gate.authorize(signed_record(verifier), PAYLOAD, **SCOPE)
    assert result.authorized is False
    assert "AUTH_AUDIT_FAILED" in result.code
    assert ledger.used == set()
    assert mutated == []
