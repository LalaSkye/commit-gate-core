"""CCG-T02f M16 double-failure regression.
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


class ConsumeSucceedsRollbackFailsLedger:
    def __init__(self) -> None:
        self.consumed: list[tuple[str, str]] = []

    def contains(self, nonce: str) -> bool:
        return any(n == nonce for n, _ in self.consumed)

    def consume(self, nonce: str, decision_id: str) -> bool:
        self.consumed.append((nonce, decision_id))
        return True

    def rollback(self, nonce: str, decision_id: str) -> None:
        raise ValueError("injected rollback failure")


class RaisingAuditSink:
    def append(self, event: Mapping[str, Any]) -> None:
        raise RuntimeError("injected audit failure")


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


def make_gate():
    verifier = HmacSha256Verifier(KEY)
    ledger = ConsumeSucceedsRollbackFailsLedger()
    mutated = []

    def boom(record: Mapping[str, Any]) -> None:
        mutated.append(record)

    gate = CommitGate(
        verifier=verifier,
        nonce_ledger=ledger,
        audit=RaisingAuditSink(),
        mutation_callback=boom,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FakeClock(datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)),
    )
    return gate, mutated, verifier, ledger


def test_audit_and_rollback_failure_is_reported():
    gate, mutated, verifier, ledger = make_gate()
    record = signed_record(verifier)
    result = gate.authorize(
        record,
        PAYLOAD,
        actor_id="agent_17",
        action="approve_invoice",
        object_id="invoice_778",
        environment="prod",
    )
    assert ledger.consumed == [("nonce_001", "dr_001")]
    assert result.authorized is False
    assert result.phase == "REFUSED"
    assert result.code == "ERROR:AUTH_AUDIT_FAILED_ROLLBACK_FAILED:RuntimeError:ValueError"
    assert result.ticket is None
    assert mutated == []
