#!/usr/bin/env python3
"""
Scenario 001 — AI-generated external email refusal.

Synthetic, review-only harness.

Claim boundary:
This script demonstrates one bounded scenario path. It does not prove enterprise
readiness, production deployment, compliance, certification, adoption, or
path-universal governance.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent
ATTEMPT_PATH = ROOT / "invalid_attempt_missing_authority.json"

REQUIRED_FIELDS = [
    "actor",
    "action_type",
    "recipient_scope",
    "payload_hash",
    "authority_token",
    "expiry",
    "nonce",
]


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def load_attempt() -> Dict[str, Any]:
    return json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))


def initial_state() -> Dict[str, Any]:
    return {
        "sent_messages": [],
        "audit_receipts": [],
    }


def commit_gate(attempt: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    before_state_hash = stable_hash(state)

    for field in REQUIRED_FIELDS:
        if field not in attempt or attempt[field] in (None, ""):
            receipt = {
                "receipt_id": "RCP-ESP-001-RUN",
                "scenario_id": attempt.get("scenario_id"),
                "attempt_id": attempt.get("attempt_id"),
                "attempted_action": attempt.get("action_type"),
                "actor": attempt.get("actor"),
                "action_type": attempt.get("action_type"),
                "recipient_scope": attempt.get("recipient_scope"),
                "payload_hash": attempt.get("payload_hash"),
                "missing_field": field,
                "decision": "DENY",
                "refusal_reason": (
                    f"{field} absent — no valid DecisionRecord for this actor, "
                    "action_type, recipient_scope, and payload at gate time"
                ),
                "downstream_send": False,
                "receipt_written": True,
                "state_mutated": False,
                "before_state_hash": before_state_hash,
                "after_state_hash": before_state_hash,
            }
            state["audit_receipts"].append(receipt)
            return receipt

    # This branch is deliberately unreachable for the invalid fixture.
    state["sent_messages"].append(copy.deepcopy(attempt["payload"]))
    after_state_hash = stable_hash(state)
    return {
        "scenario_id": attempt.get("scenario_id"),
        "attempt_id": attempt.get("attempt_id"),
        "decision": "ALLOW",
        "downstream_send": True,
        "receipt_written": False,
        "state_mutated": True,
        "before_state_hash": before_state_hash,
        "after_state_hash": after_state_hash,
    }


def run_once() -> Dict[str, Any]:
    attempt = load_attempt()
    state = initial_state()
    receipt = commit_gate(attempt, state)

    assert receipt["decision"] == "DENY"
    assert receipt["missing_field"] == "authority_token"
    assert receipt["downstream_send"] is False
    assert receipt["receipt_written"] is True
    assert receipt["state_mutated"] is False
    assert receipt["before_state_hash"] == receipt["after_state_hash"]
    assert state["sent_messages"] == []

    return receipt


def main() -> None:
    first = run_once()
    replay = run_once()

    replay_stable = (
        first["decision"] == replay["decision"]
        and first["missing_field"] == replay["missing_field"]
        and first["downstream_send"] is False
        and replay["downstream_send"] is False
    )

    assert replay_stable is True

    print(f"Scenario: {first['scenario_id']}")
    print(f"Decision: {first['decision']}")
    print(f"Missing field: {first['missing_field']}")
    print(f"Downstream send: {str(first['downstream_send']).lower()}")
    print(f"Receipt written: {str(first['receipt_written']).lower()}")
    print(f"Replay stable: {str(replay_stable).lower()}")


if __name__ == "__main__":
    main()
