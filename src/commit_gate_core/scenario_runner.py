"""
Scenario runners for bounded, synthetic execution-boundary evidence.

Scope:
NON_EXEC / REVIEW_ONLY.

Claim boundary:
These runners demonstrate synthetic refusal behaviour on demonstrated paths only.
They do not prove production enforcement, external system control, compliance,
certification, deployment, adoption, or path-universal coverage.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

REQUIRED_FIELDS = [
    "actor",
    "action_type",
    "recipient_scope",
    "payload_hash",
    "authority_token",
    "expiry",
    "nonce",
]

SCENARIO_ID = "ESP-001"
FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "enterprise-shaped-scenarios"
    / "invalid_attempt_missing_authority.json"
)

INITIAL_STATE = {
    "sent_messages": [],
    "audit_receipts": [],
}


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def load_attempt(path: Path = FIXTURE_PATH) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def initial_state() -> Dict[str, Any]:
    return copy.deepcopy(INITIAL_STATE)


def write_receipt(attempt: Dict[str, Any], missing_field: str, state_hash: str) -> Dict[str, Any]:
    issued_at = datetime.now(timezone.utc).isoformat()
    receipt = {
        "receipt_id": f"RCP-{SCENARIO_ID}-RUN",
        "scenario_id": attempt.get("scenario_id", SCENARIO_ID),
        "attempt_id": attempt.get("attempt_id"),
        "attempted_action": attempt.get("action_type", "UNKNOWN"),
        "actor": attempt.get("actor", "UNKNOWN"),
        "action_type": attempt.get("action_type", "UNKNOWN"),
        "recipient_scope": attempt.get("recipient_scope", "UNKNOWN"),
        "payload_hash": attempt.get("payload_hash", "UNKNOWN"),
        "missing_field": missing_field,
        "decision": "DENY",
        "verdict": "DENY",
        "refusal_reason": (
            f"{missing_field} absent — no valid DecisionRecord for this actor, "
            "action_type, recipient_scope, and payload at gate time"
        ),
        "issued_at": issued_at,
        "refused_at": issued_at,
        "timestamp": issued_at,
        "downstream_send": False,
        "state_mutated": False,
        "before_state_hash": state_hash,
        "after_state_hash": state_hash,
        "evidence": [
            "missing authority_token",
            "downstream_send=false",
            "before_state_hash == after_state_hash",
        ],
    }
    receipt["receipt_hash"] = stable_hash(receipt)
    return receipt


def commit_gate(attempt: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """STRUCTURE_FIRST, FIRST_FAIL synthetic CommitGate."""
    state_before = copy.deepcopy(state)
    before_state_hash = stable_hash(state_before)

    for field in REQUIRED_FIELDS:
        if field not in attempt or attempt[field] in (None, ""):
            receipt = write_receipt(attempt, field, before_state_hash)
            state["audit_receipts"].append(receipt)
            return {
                "decision": "DENY",
                "verdict": "DENY",
                "missing_field": field,
                "downstream_send": False,
                "receipt_written": True,
                "receipt": receipt,
                "receipt_hash": receipt["receipt_hash"],
                "sent_messages": list(state["sent_messages"]),
                "before_state_hash": before_state_hash,
                "after_state_hash": before_state_hash,
                "state_mutated": False,
            }

    # ALLOW branch is intentionally not reached by ESP-001.
    state["sent_messages"].append(copy.deepcopy(attempt.get("payload")))
    after_state_hash = stable_hash(state)
    return {
        "decision": "ALLOW",
        "verdict": "ALLOW",
        "missing_field": None,
        "downstream_send": True,
        "receipt_written": False,
        "receipt": None,
        "receipt_hash": None,
        "sent_messages": list(state["sent_messages"]),
        "before_state_hash": before_state_hash,
        "after_state_hash": after_state_hash,
        "state_mutated": before_state_hash != after_state_hash,
    }


def run_scenario_001() -> Dict[str, Any]:
    attempt = load_attempt()
    state = initial_state()
    return commit_gate(attempt, state)
