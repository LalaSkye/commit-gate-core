"""CCG-T01 six regression tests for frozen mutants M1–M6.
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


class RaisingNonceLedger(InMemoryNonceLedger):
    def consume(self, nonce: str, decision_id: str) -> bool:
        raise RuntimeError("injected ledger failure")


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[Mapping[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(event)


KEY = b"lab-key-not-for-production"
PAYLOAD = b"invoice-778-body"
SCOPE = dict(
    actor_id="agent_17",
    action="approve_invoice",
    object_id="invoice_778",
    environment="prod",
)


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


def make_gate(*, ledger=None, clock=None):
    verifier = HmacSha256Verifier(KEY)
    audit = RecordingAuditSink()
    ledger = ledger or InMemoryNonceLedger()
    mutated: list[Any] = []

    def boom(record: Mapping[str, Any]) -> None:
        mutated.append(record)

    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=audit,
        mutation_callback=boom,
        accepted_policy_versions=("2026-04-27.1",),
        clock=clock or FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, mutated, verifier


def _assert_refused(result, expected_code: str, mutated: list) -> None:
    assert result.authorized is False
    assert result.phase == "REFUSED"
    assert result.code == expected_code
    assert result.ticket is None
    assert mutated == []


def test_m1_verdict_not_allow():
    gate, mutated, verifier = make_gate()
    record = signed_record(verifier, verdict="DENY")
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:VERDICT_NOT_ALLOW:DENY", mutated)


def test_m2_policy_version_rejected():
    gate, mutated, verifier = make_gate()
    record = signed_record(verifier, policy_version="2099-01-01.0")
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:POLICY_VERSION_REJECTED:2099-01-01.0", mutated)


def test_m3_issued_at_in_future():
    gate, mutated, verifier = make_gate()
    record = signed_record(
        verifier,
        issued_at="2026-04-27T06:00:00Z",
        expires_at="2026-04-27T07:00:00Z",
    )
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:ISSUED_AT_IN_FUTURE", mutated)


def test_m4_invalid_time_window():
    gate, mutated, verifier = make_gate()
    record = signed_record(
        verifier,
        issued_at="2026-04-27T05:00:00Z",
        expires_at="2026-04-27T04:00:00Z",
    )
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:INVALID_TIME_WINDOW", mutated)


def test_m5_nonce_ledger_failed():
    gate, mutated, verifier = make_gate(ledger=RaisingNonceLedger())
    record = signed_record(verifier)
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:NONCE_LEDGER_FAILED:RuntimeError", mutated)


def test_m6_empty_required_field_signature():
    gate, mutated, verifier = make_gate()
    record = signed_record(verifier)
    record["signature"] = ""
    result = gate.authorize(record, PAYLOAD, **SCOPE)
    _assert_refused(result, "DENY:INVALID_FIELD:signature", mutated)
