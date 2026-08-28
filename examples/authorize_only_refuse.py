"""Authorize-only inspection example.

Calls authorize with payload_bytes and no DecisionRecord.
Does not apply a payload. Does not use mutation_callback.
Prints the real gate code. Does not relabel refusals as HOLD.
"""

from __future__ import annotations

from commit_gate_core.gate import CommitGate
from commit_gate_core.hmac_mac import HmacSha256Verifier


class MemoryNonce:
    def __init__(self) -> None:
        self.used: set[str] = set()

    def contains(self, nonce: str) -> bool:
        return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> None:
        self.used.add(nonce)

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.used.discard(nonce)


class MemoryAudit:
    def __init__(self) -> None:
        self.events: list = []

    def append(self, event) -> None:
        self.events.append(dict(event))


def main() -> int:
    gate = CommitGate(
        verifier=HmacSha256Verifier(b"lab-key-not-for-production"),
        nonce_ledger=MemoryNonce(),
        audit=MemoryAudit(),
        accepted_policy_versions=("v1",),
    )
    result = gate.authorize(
        None,
        b"demo-payload",
        actor_id="demo-actor",
        action="email.send",
        object_id="user@example.com",
        environment="demo",
    )
    print(f"authorized: {result.authorized}")
    print(f"phase: {result.phase}")
    print(f"code: {result.code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
