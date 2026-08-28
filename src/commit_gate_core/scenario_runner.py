"""Refusal-only synthetic scenario runner.

NON_EXEC / REVIEW_ONLY.

Every path leaves caller-supplied state unchanged and reports
downstream_send=False. There is no ALLOW / send branch.
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
    Path(__file__).resolve().parent
    / "data"
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
            f"{missing_field} — this runner never applies payloads"
        ),
        "issued_at": issued_at,
        "refused_at": issued_at,
        "timestamp": issued_at,
        "downstream_send": False,
        "state_mutated": False,
        "before_state_hash": state_hash,
        "after_state_hash": state_hash,
        "evidence": [
            "refusal-only runner",
            "downstream_send=false",
            "caller state unchanged",
        ],
    }
    receipt["receipt_hash"] = stable_hash({k: v for k, v in receipt.items() if k != "receipt_hash"})
    return receipt


def commit_gate(attempt: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """STRUCTURE_FIRST refusal runner. Never sends. Never writes caller state."""
    state_before = copy.deepcopy(state)
    before_state_hash = stable_hash(state_before)

    missing = None
    for field in REQUIRED_FIELDS:
        if field not in attempt or attempt[field] in (None, ""):
            missing = field
            break
    if missing is None:
        missing = "executor_removed"

    receipt = write_receipt(attempt, missing, before_state_hash)
    return {
        "decision": "DENY",
        "verdict": "DENY",
        "missing_field": missing,
        "downstream_send": False,
        "receipt_written": True,
        "receipt": receipt,
        "receipt_hash": receipt["receipt_hash"],
        "sent_messages": list(state_before["sent_messages"]),
        "before_state_hash": before_state_hash,
        "after_state_hash": before_state_hash,
        "state_mutated": False,
    }


def run_scenario_001() -> Dict[str, Any]:
    attempt = load_attempt()
    state = initial_state()
    return commit_gate(attempt, state)
