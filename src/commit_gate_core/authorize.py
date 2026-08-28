"""Public authorisation kernel.

The gate decides whether a payload *may* be applied.
It does not apply it. COMMITTED is reserved for an executor
that can observe the world. This module never calls a mutation callback.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .canonical import SIGNED_FIELDS
from .gate import AuditSink, Clock, NonceLedger, SignatureVerifier, SystemClock


def payload_hash(payload_bytes: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload_bytes).hexdigest()


@dataclass(frozen=True)
class AuthorizationResult:
    authorized: bool
    phase: str
    code: str
    decision_id: Optional[str]
    nonce: Optional[str]
    payload_hash: Optional[str]
    timestamp: str
    ticket: Optional[Mapping[str, str]] = None


class Authorizer:
    """Nonce + receipt for a hashed payload. No world mutation."""

    def __init__(
        self,
        *,
        verifier: SignatureVerifier,
        nonce_ledger: NonceLedger,
        audit: AuditSink,
        accepted_policy_versions: tuple[str, ...],
        clock: Optional[Clock] = None,
    ) -> None:
        self._verifier = verifier
        self._nonce_ledger = nonce_ledger
        self._audit = audit
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
    ) -> AuthorizationResult:
        expected_hash = payload_hash(payload_bytes)
        attempted = {
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "environment": environment,
            "commit_hash": expected_hash,
        }
        if record is None:
            return self._refuse("DENY:NO_DECISION_RECORD", None, None, expected_hash, attempted)

        error = self._structural_error(record)
        if error:
            did = record.get("decision_id") if isinstance(record.get("decision_id"), str) else None
            return self._refuse(f"DENY:{error}", did, None, expected_hash, attempted)

        decision_id = str(record["decision_id"])
        nonce = str(record["nonce"])

        if record["commit_hash"] != expected_hash:
            return self._refuse(
                "DENY:PAYLOAD_HASH_MISMATCH", decision_id, nonce, expected_hash, attempted
            )
        if record["verdict"] != "ALLOW":
            return self._refuse(
                f"DENY:VERDICT_NOT_ALLOW:{record['verdict']}",
                decision_id,
                nonce,
                expected_hash,
                attempted,
            )
        if record["policy_version"] not in self._accepted_policy_versions:
            return self._refuse(
                f"DENY:POLICY_VERSION_REJECTED:{record['policy_version']}",
                decision_id,
                nonce,
                expected_hash,
                attempted,
            )
        if not self._verifier.verify(record):
            return self._refuse(
                "DENY:INVALID_SIGNATURE", decision_id, nonce, expected_hash, attempted
            )

        try:
            issued_at, expires_at = self._parse_times(record)
        except ValueError as exc:
            return self._refuse(f"DENY:{exc}", decision_id, nonce, expected_hash, attempted)

        now = self._clock.now()
        if now < issued_at:
            return self._refuse(
                "DENY:ISSUED_AT_IN_FUTURE", decision_id, nonce, expected_hash, attempted
            )
        if now > expires_at:
            return self._refuse(
                "DENY:DECISION_EXPIRED", decision_id, nonce, expected_hash, attempted
            )

        for field, value in attempted.items():
            if record[field] != value:
                return self._refuse(
                    f"DENY:SCOPE_MISMATCH:{field}", decision_id, nonce, expected_hash, attempted
                )

        if self._nonce_ledger.contains(nonce):
            return self._refuse(
                "DENY:NONCE_REPLAYED", decision_id, nonce, expected_hash, attempted
            )

        self._nonce_ledger.consume(nonce, decision_id)
        event = {
            "event_type": "GATE_AUTHORIZED",
            "phase": "AUTHORIZED",
            "authorized": True,
            "code": "AUTHORIZED",
            "decision_id": decision_id,
            "nonce": nonce,
            "payload_hash": expected_hash,
            "timestamp": self._ts(),
            "attempted": dict(attempted),
            "record_scope": {k: record.get(k) for k in SIGNED_FIELDS},
        }
        try:
            self._audit.append(event)
        except Exception as exc:
            try:
                self._nonce_ledger.rollback(nonce, decision_id)
            except Exception as rollback_exc:
                return AuthorizationResult(
                    authorized=False,
                    phase="REFUSED",
                    code=(
                        "ERROR:AUTH_AUDIT_FAILED_ROLLBACK_FAILED:"
                        f"{type(exc).__name__}:{type(rollback_exc).__name__}"
                    ),
                    decision_id=decision_id,
                    nonce=nonce,
                    payload_hash=expected_hash,
                    timestamp=self._ts(),
                )
            return self._refuse(
                f"DENY:AUTH_AUDIT_FAILED:{type(exc).__name__}",
                decision_id,
                nonce,
                expected_hash,
                attempted,
                already_refused_event=True,
            )

        ticket = {
            "decision_id": decision_id,
            "nonce": nonce,
            "payload_hash": expected_hash,
            "phase": "AUTHORIZED",
        }
        return AuthorizationResult(
            authorized=True,
            phase="AUTHORIZED",
            code="AUTHORIZED",
            decision_id=decision_id,
            nonce=nonce,
            payload_hash=expected_hash,
            timestamp=self._ts(),
            ticket=ticket,
        )

    def _refuse(
        self,
        code: str,
        decision_id: Optional[str],
        nonce: Optional[str],
        payload_hash_value: Optional[str],
        attempted: Mapping[str, str],
        *,
        already_refused_event: bool = False,
    ) -> AuthorizationResult:
        if not already_refused_event:
            try:
                self._audit.append(
                    {
                        "event_type": "GATE_REFUSED",
                        "phase": "REFUSED",
                        "authorized": False,
                        "code": code,
                        "decision_id": decision_id,
                        "nonce": nonce,
                        "payload_hash": payload_hash_value,
                        "timestamp": self._ts(),
                        "attempted": dict(attempted),
                    }
                )
            except Exception as exc:
                code = f"DENY:REFUSAL_AUDIT_FAILED:{type(exc).__name__}:{code}"
        return AuthorizationResult(
            authorized=False,
            phase="REFUSED",
            code=code,
            decision_id=decision_id,
            nonce=nonce,
            payload_hash=payload_hash_value,
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


def _parse_rfc3339(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("INVALID_TIMESTAMP_FORMAT")
    return parsed.astimezone(timezone.utc)
