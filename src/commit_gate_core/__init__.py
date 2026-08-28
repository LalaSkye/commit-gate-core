"""Public package surface for commit-gate-core.

Promoted path: CommitGate.authorize / Authorizer.authorize
TwoPhaseCommit.apply is experimental and is not exported.
"""

from .authorize import AuthorizationResult, Authorizer, payload_hash
from .canonical import SIGNED_FIELDS, canonical_bytes
from .gate import (
    AuditSink,
    Clock,
    CommitGate,
    GateResult,
    NonceLedger,
    SignatureVerifier,
    SystemClock,
)
from .hmac_mac import HmacSha256Verifier

__version__ = "0.2.0a1"

__all__ = [
    "AuditSink",
    "AuthorizationResult",
    "Authorizer",
    "Clock",
    "CommitGate",
    "GateResult",
    "HmacSha256Verifier",
    "NonceLedger",
    "SIGNED_FIELDS",
    "SignatureVerifier",
    "SystemClock",
    "canonical_bytes",
    "payload_hash",
    "__version__",
]
