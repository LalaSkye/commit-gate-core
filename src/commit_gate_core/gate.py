"""Commit gate kernel.

Public verbs:
    authorize(record, payload_bytes, ...)  — promoted
    execute(..., payload_bytes=...)       — deprecated wrapper, same path

`commit_hash` without `payload_bytes` is refused.
`mutation_callback` is never invoked.
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
    """Authorisation surface. Does not mutate the world."""

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

    def execute(
        self,
        *,
        record: Optional[Mapping[str, Any]] = None,
        actor_id: str,
        action: str,
        object_id: str,
        environment: str,
        payload_bytes: Optional[bytes] = None,
        commit_hash: Optional[str] = None,
    ) -> GateResult:
        """Deprecated wrapper. Requires payload_bytes. Calls authorize only."""
        if payload_bytes is None:
            code = (
                "DENY:COMMIT_HASH_ONLY_FORBIDDEN"
                if commit_hash is not None
                else "DENY:PAYLOAD_BYTES_REQUIRED"
            )
            timestamp = self._ts()
            try:
                self._audit.append(
                    {
                        "event_type": "GATE_REFUSED",
                        "phase": "REFUSED",
                        "allowed": False,
                        "code": code,
                        "decision_id": None,
                        "timestamp": timestamp,
                        "attempted": {
                            "actor_id": actor_id,
                            "action": action,
                            "object_id": object_id,
                            "environment": environment,
                        },
                    }
                )
            except Exception as exc:
                return GateResult(
                    allowed=False,
                    code=f"ERROR:AUDIT_APPEND_FAILED:{type(exc).__name__}",
                    decision_id=None,
                    timestamp=self._ts(),
                )
            return GateResult(
                allowed=False,
                code=code,
                decision_id=None,
                timestamp=timestamp,
            )

        auth = self.authorize(
            record,
            payload_bytes,
            actor_id=actor_id,
            action=action,
            object_id=object_id,
            environment=environment,
        )
        return GateResult(
            allowed=auth.authorized,
            code=auth.code,
            decision_id=auth.decision_id,
            timestamp=auth.timestamp,
        )

    def _ts(self) -> str:
        return self._clock.now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
