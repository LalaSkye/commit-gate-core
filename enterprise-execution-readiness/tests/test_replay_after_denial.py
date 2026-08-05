"""
Replay-after-denial synthetic test.

This test proves deterministic replay refusal behaviour inside the synthetic
enterprise-shaped harness.
It does not prove production persistence or path-universal replay protection.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "adapters" / "replay_ledger.py"

spec = importlib.util.spec_from_file_location("replay_ledger", LEDGER_PATH)
replay_ledger = importlib.util.module_from_spec(spec)
assert spec.loader is not None
# Register the module in sys.modules before executing it.
# Without this, any @dataclass in the loaded module fails at import time:
# dataclasses resolves sys.modules[cls.__module__].__dict__, which is None
# for a module built by module_from_spec but never registered.
# Recorded 2026-08-05.
sys.modules[spec.name] = replay_ledger
spec.loader.exec_module(replay_ledger)
ReplayLedger = replay_ledger.ReplayLedger


NONCE = "esp-001-replay-test"


def synthetic_gate(*, nonce: str, ledger: ReplayLedger) -> str:
    if ledger.contains(nonce):
        return "DENY:NONCE_REPLAYED"

    ledger.record(
        nonce=nonce,
        decision_id="decision-esp-001",
        result_code="DENY:NO_DECISION_RECORD",
    )

    return "DENY:NO_DECISION_RECORD"


def test_replay_after_denial_is_deterministically_refused() -> None:
    ledger = ReplayLedger()

    first = synthetic_gate(nonce=NONCE, ledger=ledger)
    second = synthetic_gate(nonce=NONCE, ledger=ledger)

    assert first == "DENY:NO_DECISION_RECORD"
    assert second == "DENY:NONCE_REPLAYED"
    assert ledger.count() == 1
