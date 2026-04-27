"""Commit gate kernel v1.

Invariant:
    No state mutation is permitted unless a signed, scoped, unexpired,
    unreplayed DecisionRecord authorises the exact commit.

This module is intentionally self-contained for v1. Protocols are inline so
that the first public kernel has one inspection surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Optional, Protocol, Sequence


REQUIRED_FIELDS: tuple[str, ...] = (
    "decision_id",
    "actor_id",
    "action",
    "object_id",
    "environment",
    "commit_hash",
    "verdict",
    "policy_version",
    "issued_at",
    "expires_at",
    "nonce",
    "signature",
)


@dataclass(frozen=True)
class GateResult:
    """Frozen result shape returned by every gate exit."""

    allowed: bool
    code: str
    decision_id: Optional[str]
    timestamp: str


class SignatureVerifier(Protocol):
    """Verifies that the DecisionRecord signature is valid."""

    def verify(self, record: Mapping[str, Any]) -> bool:
        ...


class NonceLedger(Protocol):
    """Tracks one-use nonces.

    v1 requires rollback because nonce consumption occurs before mutation.
    A concrete ledger may implement this with a database transaction instead.
    """

    def contains(self, nonce: str) -> bool:
        ...

    def consume(self, nonce: str, decision_id: str) -> None:
        ...

    def rollback(self, nonce: str, decision_id: str) -> None:
        ...


class AuditSink(Protocol):
    """Receives audit entries for every gate exit."""

    def append(self, event: Mapping[str, Any]) -> None:
        ...


class Clock(Protocol):
    """Provides current UTC time."""

    def now(self) -> datetime:
        ...


class SystemClock:
    """Default UTC clock."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


MutationCallback = Callable[[Mapping[str, Any]], None]


class CommitGate:
    """Execution-bound mutation gate.

    Pipeline:
        1. validate structure
        2. verify signature
        3. verify timestamps
        4. verify exact scope
        5. verify nonce unused
        6. consume nonce
        7. call mutation callback
        8. append audit on every exit
    """

    def __init__(
        self,
        *,
        verifier: SignatureVerifier,
        nonce_ledger: NonceLedger,
        audit: AuditSink,
        mutation_callback: MutationCallback,
        accepted_policy_versions: Sequence[str],
        clock: Optional[Clock] = None,
    ) -> None:
        self._verifier = verifier
        self._nonce_ledger = nonce_ledger
        self._audit = audit
        self._mutation_callback = mutation_callback
        self._accepted_policy_versions = frozenset(accepted_policy_versions)
        self._clock = clock or SystemClock()

    def execute(
        self,
        *,
        record: Optional[Mapping[str, Any]],
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
        commit_hash: str,
    ) -> GateResult:
        """Evaluate one commit attempt.

        No exception from validation or mutation is allowed to bypass audit.
        """

        decision_id: Optional[str] = None
        nonce: Optional[str] = None
        nonce_consumed = False

        try:
            now = self._clock.now()

            # 1. validate structure
            if record is None:
                return self._deny(
                    code="DENY:NO_DECISION_RECORD",
                    decision_id=None,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                )

            structural_error = self._structural_error(record)
            if structural_error is not None:
                decision_id = self._safe_str(record.get("decision_id"))
                return self._deny(
                    code=f"DENY:{structural_error}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            decision_id = str(record["decision_id"])
            nonce = str(record["nonce"])

            if record["verdict"] != "ALLOW":
                return self._deny(
                    code=f"DENY:VERDICT_NOT_ALLOW:{record['verdict']}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            if record["policy_version"] not in self._accepted_policy_versions:
                return self._deny(
                    code=f"DENY:POLICY_VERSION_REJECTED:{record['policy_version']}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            # 2. verify signature
            if not self._verifier.verify(record):
                return self._deny(
                    code="DENY:INVALID_SIGNATURE",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            # 3. verify timestamps
            issued_at, expires_at = self._parse_times(record)
            if now < issued_at:
                return self._deny(
                    code="DENY:ISSUED_AT_IN_FUTURE",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )
            if now > expires_at:
                return self._deny(
                    code="DENY:DECISION_EXPIRED",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            # 4. verify exact scope
            scope_error = self._scope_error(
                record=record,
                actor_id=actor_id,
                action=action,
                object_id=object_id,
                environment=environment,
                commit_hash=commit_hash,
            )
            if scope_error is not None:
                return self._deny(
                    code=f"DENY:{scope_error}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            # 5. verify nonce unused
            if self._nonce_ledger.contains(nonce):
                return self._deny(
                    code="DENY:NONCE_REPLAYED",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record=record,
                )

            # 6 + 7. consume nonce then mutate. Roll back nonce if mutation fails.
            self._nonce_ledger.consume(nonce, decision_id)
            nonce_consumed = True

            try:
                self._mutation_callback(record)
            except Exception as exc:
                try:
                    self._nonce_ledger.rollback(nonce, decision_id)
                    nonce_consumed = False
                    return self._error(
                        code=f"ROLLBACK:MUTATION_FAILED:{type(exc).__name__}",
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record=record,
                    )
                except Exception as rollback_exc:
                    return self._error(
                        code=(
                            "ERROR:MUTATION_FAILED_ROLLBACK_FAILED:"
                            f"{type(exc).__name__}:{type(rollback_exc).__name__}"
                        ),
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record=record,
                    )

            return self._allow(
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record=record,
            )

        except ValueError as exc:
            return self._deny(
                code=f"DENY:{str(exc)}",
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record=record,
            )
        except Exception as exc:
            # Last-resort fail-closed path. Try to roll back a consumed nonce.
            if nonce_consumed and nonce is not None and decision_id is not None:
                try:
                    self._nonce_ledger.rollback(nonce, decision_id)
                    return self._error(
                        code=f"ROLLBACK:UNEXPECTED:{type(exc).__name__}",
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record=record,
                    )
                except Exception as rollback_exc:
                    return self._error(
                        code=(
                            "ERROR:UNEXPECTED_ROLLBACK_FAILED:"
                            f"{type(exc).__name__}:{type(rollback_exc).__name__}"
                        ),
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record=record,
                    )
            return self._error(
                code=f"ERROR:UNEXPECTED:{type(exc).__name__}",
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record=record,
            )

    def _structural_error(self, record: Mapping[str, Any]) -> Optional[str]:
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            return "MISSING_FIELD:" + ",".join(missing)
        for field in REQUIRED_FIELDS:
            if not isinstance(record[field], str) or record[field] == "":
                return f"INVALID_FIELD:{field}"
        return None

    def _parse_times(self, record: Mapping[str, Any]) -> tuple[datetime, datetime]:
        try:
            issued_at = self._parse_rfc3339(str(record["issued_at"]))
            expires_at = self._parse_rfc3339(str(record["expires_at"]))
        except ValueError:
            raise ValueError("INVALID_TIMESTAMP_FORMAT")
        if expires_at < issued_at:
            raise ValueError("INVALID_TIME_WINDOW")
        return issued_at, expires_at

    def _parse_rfc3339(self, value: str) -> datetime:
        normalised = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalised)
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        return parsed.astimezone(timezone.utc)

    def _scope_error(
        self,
        *,
        record: Mapping[str, Any],
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
        commit_hash: str,
    ) -> Optional[str]:
        expected = {
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "environment": environment,
            "commit_hash": commit_hash,
        }
        for field, value in expected.items():
            if record[field] != value:
                return f"SCOPE_MISMATCH:{field}"
        return None

    def _allow(
        self,
        *,
        decision_id: str,
        attempted: Mapping[str, Any],
        record: Mapping[str, Any],
    ) -> GateResult:
        return self._finish(
            allowed=True,
            code="ALLOW",
            decision_id=decision_id,
            attempted=attempted,
            record=record,
        )

    def _deny(
        self,
        *,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record: Optional[Mapping[str, Any]] = None,
    ) -> GateResult:
        return self._finish(
            allowed=False,
            code=code,
            decision_id=decision_id,
            attempted=attempted,
            record=record,
        )

    def _error(
        self,
        *,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record: Optional[Mapping[str, Any]] = None,
    ) -> GateResult:
        return self._finish(
            allowed=False,
            code=code,
            decision_id=decision_id,
            attempted=attempted,
            record=record,
        )

    def _finish(
        self,
        *,
        allowed: bool,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record: Optional[Mapping[str, Any]],
    ) -> GateResult:
        timestamp = self._clock.now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        result = GateResult(
            allowed=allowed,
            code=code,
            decision_id=decision_id,
            timestamp=timestamp,
        )
        audit_event = {
            "event_type": "GATE_EVALUATION",
            "allowed": result.allowed,
            "code": result.code,
            "decision_id": result.decision_id,
            "timestamp": result.timestamp,
            "attempted": dict(attempted),
        }
        if record is not None:
            audit_event["record_scope"] = {
                "actor_id": record.get("actor_id"),
                "action": record.get("action"),
                "object_id": record.get("object_id"),
                "environment": record.get("environment"),
                "commit_hash": record.get("commit_hash"),
                "policy_version": record.get("policy_version"),
            }
        self._audit.append(audit_event)
        return result

    def _attempt(
        self,
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
        commit_hash: str,
    ) -> Mapping[str, Any]:
        return {
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "environment": environment,
            "commit_hash": commit_hash,
        }

    def _safe_str(self, value: Any) -> Optional[str]:
        if isinstance(value, str) and value:
            return value
        return None
