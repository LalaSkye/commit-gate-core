"""
Persistent replay ledger scaffold.

This is an in-memory replay surface for deterministic refusal replay tests.
It is not a production persistence layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ReplayLedgerEntry:
    nonce: str
    decision_id: str
    result_code: str


@dataclass
class ReplayLedger:
    entries: List[ReplayLedgerEntry] = field(default_factory=list)
    index: Dict[str, ReplayLedgerEntry] = field(default_factory=dict)

    def record(self, *, nonce: str, decision_id: str, result_code: str) -> None:
        entry = ReplayLedgerEntry(
            nonce=nonce,
            decision_id=decision_id,
            result_code=result_code,
        )
        self.entries.append(entry)
        self.index[nonce] = entry

    def contains(self, nonce: str) -> bool:
        return nonce in self.index

    def count(self) -> int:
        return len(self.entries)
