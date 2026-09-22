from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier, Lock
from typing import Any, Mapping

import pytest

from src.commit_gate_core.authorize import payload_hash
from src.commit_gate_core.canonical import SIGNED_FIELDS
from src.commit_gate_core.gate import CommitGate
from src.commit_gate_core.hmac_mac import HmacSha256Verifier


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class MutatingClock:
    def __init__(self, record: dict[str, str]) -> None:
        self._record = record

    def now(self) -> datetime:
        self._record["object_id"] = "invoice_999"
        return datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)


class ScopeRepairingVerifier:
    def __init__(self, delegate: HmacSha256Verifier) -> None:
        self._delegate = delegate

    def verify(self, record: Mapping[str, Any]) -> bool:
        verified = self._delegate.verify(record)
        record["object_id"] = "invoice_999"
        return verified


class InMemoryNonceLedger:
    def __init__(self) -> None:
        self.used: set[str] = set()
        self._owners: dict[str, str] = {}
        self._lock = Lock()

    def contains(self, nonce: str) -> bool:
        with self._lock:
            return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> bool:
        with self._lock:
            if nonce in self.used:
                return False
            self.used.add(nonce)
            self._owners[nonce] = decision_id
            return True

    def rollback(self, nonce: str, decision_id: str) -> None:
        with self._lock:
            if self._owners.get(nonce) == decision_id:
                self.used.discard(nonce)
                self._owners.pop(nonce, None)


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


def test_authenticated_record_state_cannot_change_before_scope_check():
    verifier = HmacSha256Verifier(KEY)
    record = signed_record(verifier)
    ledger = InMemoryNonceLedger()
    audit = RecordingAuditSink()

    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=lambda record: None,
        accepted_policy_versions=("2026-04-27.1",),
        clock=MutatingClock(record),
    )

    result = gate.authorize(
        record,
        PAYLOAD,
        actor_id="agent_17",
        action="approve_invoice",
        object_id="invoice_999",
        environment="prod",
    )

    assert result.authorized is False


def test_concurrent_authorize_same_nonce_one_winner():
    verifier = HmacSha256Verifier(KEY)
    ledger = InMemoryNonceLedger()
    audit = RecordingAuditSink()
    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=lambda record: None,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    record = signed_record(verifier)
    workers = 8
    barrier = Barrier(workers)

    def attempt(_: int):
        barrier.wait()
        return gate.authorize(dict(record), PAYLOAD, **SCOPE)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(attempt, range(workers)))

    assert sum(result.authorized for result in results) == 1
    assert sum(result.code == "AUTHORIZED" for result in results) == 1
    assert sum(result.code == "DENY:NONCE_REPLAYED" for result in results) == workers - 1
    assert ledger.used == {"nonce_001"}


def test_verifier_cannot_widen_scope_after_authentication():
    verifier = HmacSha256Verifier(KEY)
    record = signed_record(verifier)
    ledger = InMemoryNonceLedger()
    audit = RecordingAuditSink()

    gate = CommitGate(
        verifier=ScopeRepairingVerifier(verifier),
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=lambda record: None,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )

    result = gate.authorize(
        record,
        PAYLOAD,
        actor_id="agent_17",
        action="approve_invoice",
        object_id="invoice_999",
        environment="prod",
    )

    assert result.authorized is False
    assert result.code == "DENY:VERIFIER_MUTATED_RECORD"
    assert ledger.used == set()


def test_authorization_ticket_binds_frozen_scope_and_payload():
    gate, ledger, audit, mutated, verifier = make_gate()
    record = signed_record(verifier)

    result = gate.authorize(record, PAYLOAD, **SCOPE)

    assert result.authorized is True
    assert result.ticket is not None
    assert set(result.ticket) == set(SIGNED_FIELDS) | {"payload_hash", "phase"}
    assert result.ticket["decision_id"] == "dr_001"
    assert result.ticket["actor_id"] == "agent_17"
    assert result.ticket["action"] == "approve_invoice"
    assert result.ticket["object_id"] == "invoice_778"
    assert result.ticket["environment"] == "prod"
    assert result.ticket["policy_version"] == "2026-04-27.1"
    assert result.ticket["commit_hash"] == payload_hash(PAYLOAD)
    assert result.ticket["payload_hash"] == payload_hash(PAYLOAD)
    assert result.ticket["nonce"] == "nonce_001"
    assert result.ticket["phase"] == "AUTHORIZED"

    record["object_id"] = "invoice_999"
    assert result.ticket["object_id"] == "invoice_778"

    with pytest.raises(TypeError):
        result.ticket["object_id"] = "invoice_999"
