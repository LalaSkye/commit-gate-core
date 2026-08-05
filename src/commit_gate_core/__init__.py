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

__version__ = "0.1.1"

__all__ = [
    "AuditSink",
    "Clock",
    "CommitGate",
    "GateResult",
    "MutationCallback",
    "NonceLedger",
    "SignatureVerifier",
    "SystemClock",
    "__version__",
]
