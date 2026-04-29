"""Observable refusal demo.

Attempts an unsafe email send through CommitGate with no DecisionRecord.
The gate denies internally with code DENY:NO_DECISION_RECORD; this demo
maps that to the public label HOLD. No email is sent. One audit receipt
is captured. Stdlib only. Runs from a clean clone with no install step.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src/ importable from a clean clone without an install step.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from commit_gate_core.gate import CommitGate  # noqa: E402


class _RejectingVerifier:
    def verify(self, record):
        return False


class _EmptyNonceLedger:
    def contains(self, nonce):
        return False

    def consume(self, nonce, decision_id):
        return None

    def rollback(self, nonce, decision_id):
        return None


class _InMemoryAudit:
    def __init__(self):
        self.events = []

    def append(self, event):
        self.events.append(dict(event))


def _refuse_email(_record):
    # The mutation callback is never invoked on a deny path.
    # Present here only to make the gate construction explicit.
    raise AssertionError("mutation must not run on a denied commit")


def main() -> int:
    audit = _InMemoryAudit()
    gate = CommitGate(
        verifier=_RejectingVerifier(),
        nonce_ledger=_EmptyNonceLedger(),
        audit=audit,
        mutation_callback=_refuse_email,
        accepted_policy_versions=("v1",),
    )

    email_sent = False
    result = gate.execute(
        record=None,
        actor_id="demo-actor",
        action="email.send",
        object_id="user@example.com",
        environment="demo",
        commit_hash="0" * 40,
    )

    # Internal code is DENY:NO_DECISION_RECORD. Public demo label is HOLD.
    public_label = "HOLD" if not result.allowed else "ALLOW"
    receipt_written = len(audit.events) == 1

    print(f"Result: {public_label}")
    print(f"Email sent: {'true' if email_sent else 'false'}")
    print(f"Receipt written: {'true' if receipt_written else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
