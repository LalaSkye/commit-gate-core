"""Public package surface for commit-gate-core."""

from .gate import (
    AuditSink,
    Clock,
    CommitGate,
    GateResult,
    MutationCallback,
    NonceLedger,
    SignatureVerifier,
    SystemClock,
)
from .hmac_mac import HmacSha256Verifier
from .two_phase import PhaseResult, TwoPhaseCommit
from .canonical import canonical_bytes, SIGNED_FIELDS

__version__ = "0.2.0-dev"

__all__ = [
    "AuditSink",
    "Clock",
    "CommitGate",
    "GateResult",
    "HmacSha256Verifier",
    "MutationCallback",
    "NonceLedger",
    "PhaseResult",
    "SIGNED_FIELDS",
    "SignatureVerifier",
    "SystemClock",
    "TwoPhaseCommit",
    "canonical_bytes",
    "__version__",
]
