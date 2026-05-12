"""
Bridge ESP-001 into the real commit_gate_core CommitGate.

This is still a synthetic, in-memory harness.
The important difference from the local toy gate is that this bridge calls
src.commit_gate_core.gate.CommitGate.execute directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from commit_gate_core.gate import CommitGate, GateResult


@dataclass
class StaticSignatureVerifier:
    valid: bool = True

    def verify(self, record: Mapping[str, Any]) -> bool:
        return self.valid


@dataclass
class InMemoryNonceLedger:
    consumed: Dict[str, str] = field(default_factory=dict)

    def contains(self, nonce: str) -> bool:
        return nonce in self.consumed

    def consume(self, nonce: str, decision_id: str) -> None:
        self.consumed[nonce] = decision_id

    def rollback(self, nonce: str, decision_id: str) -> None:
        if self.consumed.get(nonce) == decision_id:
            del self.consumed[nonce]


@dataclass
class InMemoryAuditSink:
    events: List[Mapping[str, Any]] = field(default_factory=list)

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))


@dataclass
class FixedClock:
    fixed: datetime = datetime(2026, 5, 12, 10, 1, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self.fixed


@dataclass
class CommitGateBridgeResult:
    gate_result: GateResult
    audit_events: List[Mapping[str, Any]]
    downstream_send: bool
    send_call_count: int
    receipt_written: bool


def build_gate(*, mutation_callback, audit: Optional[InMemoryAuditSink] = None) -> tuple[CommitGate, InMemoryAuditSink]:
    audit_sink = audit or InMemoryAuditSink()
    gate = CommitGate(
        verifier=StaticSignatureVerifier(valid=True),
        nonce_ledger=InMemoryNonceLedger(),
        audit=audit_sink,
        mutation_callback=mutation_callback,
        accepted_policy_versions=("esp-v0.1",),
        clock=FixedClock(),
    )
    return gate, audit_sink


def esp001_attempt() -> Dict[str, Any]:
    return {
        "actor_id": "agent://morpheus-draft-bot-v1",
        "action": "SEND_EXTERNAL_EMAIL",
        "object_id": "external:partner-domain.com",
        "environment": "enterprise-shaped-synthetic-harness",
        "commit_hash": "sha256:a3f8c2d1e7b904561ac38fd2e190bba47c2d3f8a1e056b7c9d4e2f1a8b3c7d90",
    }


def esp001_missing_decision_record() -> None:
    return None


def dispatch_esp001_through_real_gate(adapter) -> CommitGateBridgeResult:
    attempt = esp001_attempt()

    def mutation_callback(record: Mapping[str, Any]) -> None:
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)
    gate_result = gate.execute(
        record=esp001_missing_decision_record(),
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )

    return CommitGateBridgeResult(
        gate_result=gate_result,
        audit_events=audit.events,
        downstream_send=adapter.send_call_count > 0,
        send_call_count=adapter.send_call_count,
        receipt_written=len(audit.events) == 1,
    )
