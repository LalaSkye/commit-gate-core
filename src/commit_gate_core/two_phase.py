"""Two-phase commit gate.

v1 CommitGate.mutate-then-audit can change the world and then return
allowed=False. This module forbids that silent pair.

Phases:
    REFUSED     nonce free, world unchanged, refusal receipt
    PREPARED    nonce spent, world unchanged, PENDING receipt
    COMMITTED   nonce spent, world mutated, COMMITTED receipt
    UNRECEIPTED nonce spent, world mutated, COMMITTED receipt missing
    ABORTED     nonce rolled back after failed apply, abort receipt

`allowed` is True only for COMMITTED.
UNRECEIPTED sets world_changed=True so a caller cannot treat it as a no-op.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .canonical import SIGNED_FIELDS
from .gate import (
    AuditSink,
    Clock,
    MutationCallback,
    NonceLedger,
    SignatureVerifier,
    SystemClock,
)


@dataclass(frozen=True)
class PhaseResult:
    allowed: bool
    phase: str
    code: str
    decision_id: Optional[str]
    nonce: Optional[str]
    world_changed: bool
    timestamp: str
    ticket: Optional[Mapping[str, str]] = None


class TwoPhaseCommit:
    """Prepare (receipt + nonce) then apply (mutation + confirm)."""

    def __init__(
        self,
        *,
        verifier: SignatureVerifier,
        nonce_ledger: NonceLedger,
        audit: AuditSink,
        mutation_callback: MutationCallback,
        accepted_policy_versions: tuple[str, ...],
        clock: Optional[Clock] = None,
    ) -> None:
        self._verifier = verifier
        self._nonce_ledger = nonce_ledger
        self._audit = audit
        self._mutation_callback = mutation_callback
        self._accepted_policy_versions = frozenset(accepted_policy_versions)
        self._clock = clock or SystemClock()
        self._tickets: dict[str, dict[str, str]] = {}

    def prepare(
        self,
        *,
        record: Optional[Mapping[str, Any]],
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
        commit_hash: str,
    ) -> PhaseResult:
        attempted = {
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "environment": environment,
            "commit_hash": commit_hash,
        }
        if record is None:
            return self._refuse("DENY:NO_DECISION_RECORD", None, None, attempted)

        error = self._structural_error(record)
        if error:
            return self._refuse(f"DENY:{error}", _opt_str(record.get("decision_id")), None, attempted)

        decision_id = str(record["decision_id"])
        nonce = str(record["nonce"])

        if record["verdict"] != "ALLOW":
            return self._refuse(
                f"DENY:VERDICT_NOT_ALLOW:{record['verdict']}", decision_id, nonce, attempted
            )
        if record["policy_version"] not in self._accepted_policy_versions:
            return self._refuse(
                f"DENY:POLICY_VERSION_REJECTED:{record['policy_version']}",
                decision_id,
                nonce,
                attempted,
            )
        if not self._verifier.verify(record):
            return self._refuse("DENY:INVALID_SIGNATURE", decision_id, nonce, attempted)

        try:
            issued_at, expires_at = self._parse_times(record)
        except ValueError as exc:
            return self._refuse(f"DENY:{exc}", decision_id, nonce, attempted)

        now = self._clock.now()
        if now < issued_at:
            return self._refuse("DENY:ISSUED_AT_IN_FUTURE", decision_id, nonce, attempted)
        if now > expires_at:
            return self._refuse("DENY:DECISION_EXPIRED", decision_id, nonce, attempted)

        for field, value in attempted.items():
            if record[field] != value:
                return self._refuse(f"DENY:SCOPE_MISMATCH:{field}", decision_id, nonce, attempted)

        if self._nonce_ledger.contains(nonce):
            return self._refuse("DENY:NONCE_REPLAYED", decision_id, nonce, attempted)

        ticket = {
            "decision_id": decision_id,
            "nonce": nonce,
            "commit_hash": commit_hash,
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "environment": environment,
            "phase": "PREPARED",
        }

        pending = {
            "event_type": "GATE_PREPARED",
            "phase": "PREPARED",
            "allowed": False,
            "code": "PREPARED",
            "decision_id": decision_id,
            "nonce": nonce,
            "timestamp": self._ts(),
            "attempted": dict(attempted),
            "record_scope": {k: record.get(k) for k in SIGNED_FIELDS},
        }
        try:
            self._audit.append(pending)
        except Exception as exc:
            return PhaseResult(
                allowed=False,
                phase="REFUSED",
                code=f"DENY:PREPARE_AUDIT_FAILED:{type(exc).__name__}",
                decision_id=decision_id,
                nonce=nonce,
                world_changed=False,
                timestamp=self._ts(),
            )

        self._nonce_ledger.consume(nonce, decision_id)
        self._tickets[decision_id] = ticket
        return PhaseResult(
            allowed=False,
            phase="PREPARED",
            code="PREPARED",
            decision_id=decision_id,
            nonce=nonce,
            world_changed=False,
            timestamp=self._ts(),
            ticket=dict(ticket),
        )

    def apply(self, ticket: Mapping[str, str]) -> PhaseResult:
        decision_id = ticket.get("decision_id")
        nonce = ticket.get("nonce")
        stored = self._tickets.get(decision_id or "")
        if stored is None or stored.get("nonce") != nonce:
            return PhaseResult(
                allowed=False,
                phase="REFUSED",
                code="DENY:UNKNOWN_TICKET",
                decision_id=decision_id,
                nonce=nonce,
                world_changed=False,
                timestamp=self._ts(),
            )
        if stored.get("phase") != "PREPARED":
            return PhaseResult(
                allowed=False,
                phase=stored.get("phase", "REFUSED"),
                code=f"DENY:TICKET_NOT_PREPARED:{stored.get('phase')}",
                decision_id=decision_id,
                nonce=nonce,
                world_changed=stored.get("phase") == "COMMITTED",
                timestamp=self._ts(),
            )

        attempted = {
            "actor_id": stored["actor_id"],
            "action": stored["action"],
            "object_id": stored["object_id"],
            "environment": stored["environment"],
            "commit_hash": stored["commit_hash"],
        }

        try:
            self._mutation_callback(dict(stored))
        except Exception as exc:
            try:
                self._nonce_ledger.rollback(str(nonce), str(decision_id))
            except Exception as rollback_exc:
                return self._record_abort(
                    decision_id,
                    nonce,
                    attempted,
                    f"ERROR:MUTATION_FAILED_ROLLBACK_FAILED:{type(exc).__name__}:{type(rollback_exc).__name__}",
                    world_changed=False,
                )
            return self._record_abort(
                decision_id,
                nonce,
                attempted,
                f"ABORTED:MUTATION_FAILED:{type(exc).__name__}",
                world_changed=False,
            )

        committed = {
            "event_type": "GATE_COMMITTED",
            "phase": "COMMITTED",
            "allowed": True,
            "code": "COMMITTED",
            "decision_id": decision_id,
            "nonce": nonce,
            "timestamp": self._ts(),
            "attempted": attempted,
        }
        try:
            self._audit.append(committed)
        except Exception as exc:
            stored["phase"] = "UNRECEIPTED"
            return PhaseResult(
                allowed=False,
                phase="UNRECEIPTED",
                code=f"COMMIT_UNRECEIPTED:{type(exc).__name__}",
                decision_id=decision_id,
                nonce=nonce,
                world_changed=True,
                timestamp=self._ts(),
                ticket=dict(stored),
            )

        stored["phase"] = "COMMITTED"
        return PhaseResult(
            allowed=True,
            phase="COMMITTED",
            code="COMMITTED",
            decision_id=decision_id,
            nonce=nonce,
            world_changed=True,
            timestamp=self._ts(),
            ticket=dict(stored),
        )

    def _record_abort(
        self,
        decision_id: Optional[str],
        nonce: Optional[str],
        attempted: Mapping[str, str],
        code: str,
        *,
        world_changed: bool,
    ) -> PhaseResult:
        if decision_id and decision_id in self._tickets:
            self._tickets[decision_id]["phase"] = "ABORTED"
        try:
            self._audit.append(
                {
                    "event_type": "GATE_ABORTED",
                    "phase": "ABORTED",
                    "allowed": False,
                    "code": code,
                    "decision_id": decision_id,
                    "nonce": nonce,
                    "timestamp": self._ts(),
                    "attempted": dict(attempted),
                }
            )
        except Exception:
            pass
        return PhaseResult(
            allowed=False,
            phase="ABORTED",
            code=code,
            decision_id=decision_id,
            nonce=nonce,
            world_changed=world_changed,
            timestamp=self._ts(),
        )

    def _refuse(
        self,
        code: str,
        decision_id: Optional[str],
        nonce: Optional[str],
        attempted: Mapping[str, str],
    ) -> PhaseResult:
        try:
            self._audit.append(
                {
                    "event_type": "GATE_REFUSED",
                    "phase": "REFUSED",
                    "allowed": False,
                    "code": code,
                    "decision_id": decision_id,
                    "nonce": nonce,
                    "timestamp": self._ts(),
                    "attempted": dict(attempted),
                }
            )
        except Exception as exc:
            code = f"DENY:REFUSAL_AUDIT_FAILED:{type(exc).__name__}:{code}"
        return PhaseResult(
            allowed=False,
            phase="REFUSED",
            code=code,
            decision_id=decision_id,
            nonce=nonce,
            world_changed=False,
            timestamp=self._ts(),
        )

    def _structural_error(self, record: Mapping[str, Any]) -> Optional[str]:
        required = SIGNED_FIELDS + ("signature",)
        missing = [name for name in required if name not in record]
        if missing:
            return "MISSING_FIELD:" + ",".join(missing)
        for name in required:
            if not isinstance(record[name], str) or record[name] == "":
                return f"INVALID_FIELD:{name}"
        return None

    def _parse_times(self, record: Mapping[str, Any]) -> tuple[datetime, datetime]:
        issued_at = _parse_rfc3339(str(record["issued_at"]))
        expires_at = _parse_rfc3339(str(record["expires_at"]))
        if expires_at < issued_at:
            raise ValueError("INVALID_TIME_WINDOW")
        return issued_at, expires_at

    def _ts(self) -> str:
        return self._clock.now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value:
        return value
    return None


def _parse_rfc3339(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("INVALID_TIMESTAMP_FORMAT")
    return parsed.astimezone(timezone.utc)
