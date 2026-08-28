"""Commit gate kernel.

v1 `execute` is deprecated as an executor. It no longer invokes
mutation_callback. The promoted path is `authorize` in authorize.py.

Invariant:
    Authorisation does not mutate the world.
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

_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "actor_id",
    "action",
    "object_id",
    "environment",
    "commit_hash",
    "policy_version",
)


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    code: str
    decision_id: Optional[str]
    timestamp: str


class SignatureVerifier(Protocol):
    def verify(self, record: Mapping[str, Any]) -> bool:
        ...


class NonceLedger(Protocol):
    def contains(self, nonce: str) -> bool:
        ...

    def consume(self, nonce: str, decision_id: str) -> None:
        ...

    def rollback(self, nonce: str, decision_id: str) -> None:
        ...


class AuditSink(Protocol):
    def append(self, event: Mapping[str, Any]) -> None:
        ...


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


MutationCallback = Callable[[Mapping[str, Any]], None]


class CommitGate:
    """Deprecated executor surface. Use authorize(). Does not mutate."""

    def __init__(
        self,
        *,
        verifier: SignatureVerifier,
        nonce_ledger: NonceLedger,
        audit: AuditSink,
        mutation_callback: Optional[MutationCallback] = None,
        accepted_policy_versions: Sequence[str] = (),
        clock: Optional[Clock] = None,
    ) -> None:
        if not accepted_policy_versions:
            raise ValueError("accepted_policy_versions is required")
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
        decision_id: Optional[str] = None
        nonce: Optional[str] = None
        nonce_consumed = False
        record_snapshot: Optional[Mapping[str, Any]] = None
        try:
            now = self._clock.now()
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
                    record_snapshot=self._snapshot(record),
                )
            decision_id = str(record["decision_id"])
            nonce = str(record["nonce"])
            if record["verdict"] != "ALLOW":
                return self._deny(
                    code=f"DENY:VERDICT_NOT_ALLOW:{record['verdict']}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
            if record["policy_version"] not in self._accepted_policy_versions:
                return self._deny(
                    code=f"DENY:POLICY_VERSION_REJECTED:{record['policy_version']}",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
            if not self._verifier.verify(record):
                return self._deny(
                    code="DENY:INVALID_SIGNATURE",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
            issued_at, expires_at = self._parse_times(record)
            if now < issued_at:
                return self._deny(
                    code="DENY:ISSUED_AT_IN_FUTURE",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
            if now > expires_at:
                return self._deny(
                    code="DENY:DECISION_EXPIRED",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
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
                    record_snapshot=self._snapshot(record),
                )
            if self._nonce_ledger.contains(nonce):
                return self._deny(
                    code="DENY:NONCE_REPLAYED",
                    decision_id=decision_id,
                    attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                    record_snapshot=self._snapshot(record),
                )
            record_snapshot = self._snapshot(record)
            self._nonce_ledger.consume(nonce, decision_id)
            nonce_consumed = True
            return self._allow(
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record_snapshot=record_snapshot,
            )
        except ValueError as exc:
            return self._deny(
                code=f"DENY:{str(exc)}",
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record_snapshot=record_snapshot,
            )
        except Exception as exc:
            if nonce_consumed and nonce is not None and decision_id is not None:
                try:
                    self._nonce_ledger.rollback(nonce, decision_id)
                    return self._error(
                        code=f"ROLLBACK:UNEXPECTED:{type(exc).__name__}",
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record_snapshot=record_snapshot,
                    )
                except Exception as rollback_exc:
                    return self._error(
                        code=(
                            "ERROR:UNEXPECTED_ROLLBACK_FAILED:"
                            f"{type(exc).__name__}:{type(rollback_exc).__name__}"
                        ),
                        decision_id=decision_id,
                        attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                        record_snapshot=record_snapshot,
                    )
            return self._error(
                code=f"ERROR:UNEXPECTED:{type(exc).__name__}",
                decision_id=decision_id,
                attempted=self._attempt(actor_id, action, object_id, environment, commit_hash),
                record_snapshot=record_snapshot,
            )

    def authorize(
        self,
        record: Optional[Mapping[str, Any]],
        payload_bytes: bytes,
        *,
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
    ):
        from .authorize import Authorizer

        return Authorizer(
            verifier=self._verifier,
            nonce_ledger=self._nonce_ledger,
            audit=self._audit,
            accepted_policy_versions=tuple(self._accepted_policy_versions),
            clock=self._clock,
        ).authorize(
            record,
            payload_bytes,
            actor_id=actor_id,
            action=action,
            object_id=object_id,
            environment=environment,
        )

    def _snapshot(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {field: record.get(field) for field in _SNAPSHOT_FIELDS}

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
        record_snapshot: Optional[Mapping[str, Any]],
    ) -> GateResult:
        return self._finish(
            allowed=True,
            code="ALLOW",
            decision_id=decision_id,
            attempted=attempted,
            record_snapshot=record_snapshot,
        )

    def _deny(
        self,
        *,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record_snapshot: Optional[Mapping[str, Any]] = None,
    ) -> GateResult:
        return self._finish(
            allowed=False,
            code=code,
            decision_id=decision_id,
            attempted=attempted,
            record_snapshot=record_snapshot,
        )

    def _error(
        self,
        *,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record_snapshot: Optional[Mapping[str, Any]] = None,
    ) -> GateResult:
        return self._finish(
            allowed=False,
            code=code,
            decision_id=decision_id,
            attempted=attempted,
            record_snapshot=record_snapshot,
        )

    def _finish(
        self,
        *,
        allowed: bool,
        code: str,
        decision_id: Optional[str],
        attempted: Mapping[str, Any],
        record_snapshot: Optional[Mapping[str, Any]],
    ) -> GateResult:
        timestamp = self._clock.now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        result = GateResult(
            allowed=allowed,
            code=code,
            decision_id=decision_id,
            timestamp=timestamp,
        )
        audit_event: dict[str, Any] = {
            "event_type": "GATE_EVALUATION",
            "allowed": result.allowed,
            "code": result.code,
            "decision_id": result.decision_id,
            "timestamp": result.timestamp,
            "attempted": dict(attempted),
        }
        if record_snapshot is not None:
            audit_event["record_scope"] = dict(record_snapshot)
        try:
            self._audit.append(audit_event)
        except Exception as audit_exc:
            audit_fail_timestamp = (
                self._clock.now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            return GateResult(
                allowed=False,
                code=f"ERROR:AUDIT_APPEND_FAILED:{type(audit_exc).__name__}",
                decision_id=decision_id,
                timestamp=audit_fail_timestamp,
            )
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
