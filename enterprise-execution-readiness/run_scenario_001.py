#!/usr/bin/env python3
"""
ESP-001 synthetic execution trace harness.

This is a synthetic, in-memory, path-local demonstration.
It does not prove live runtime enforcement or downstream non-execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict


PAYLOAD_HASH = "sha256:a3f8c2d1e7b904561ac38fd2e190bba47c2d3f8a1e056b7c9d4e2f1a8b3c7d90"
STATE_HASH = "sha256:6b91c6e31efb40ecdd5a23346b5d84a028f47cae91ad9ed4e6b75b8579d4bd2f"


def canonical_hash(value: Dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def evaluate_gate(request: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = [
        "actor",
        "action_type",
        "recipient_scope",
        "payload_hash",
        "authority_token",
        "expiry",
        "nonce",
    ]

    for field in required_fields:
        if not request.get(field):
            return {
                "decision": "DENY",
                "missing_field": field,
                "reason": f"{field} absent — no valid DecisionRecord for this actor, action_type, recipient_scope, and payload at gate time",
            }

    return {
        "decision": "ALLOW",
        "missing_field": None,
        "reason": "all required fields present in synthetic request",
    }


def main() -> None:
    before_state = {
        "external_email_outbox": [],
        "sent_count": 0,
        "last_downstream_send": False,
    }

    request = {
        "actor": "agent://morpheus-draft-bot-v1",
        "action_type": "SEND_EXTERNAL_EMAIL",
        "recipient_scope": "external:partner-domain.com",
        "payload_hash": PAYLOAD_HASH,
        "authority_token": None,
        "expiry": "2026-05-12T10:05:00Z",
        "nonce": "nonce-esp-001",
    }

    before_hash = canonical_hash(before_state)
    refusal = evaluate_gate(request)

    after_state = copy.deepcopy(before_state)

    downstream_send = False
    receipt_written = refusal["decision"] == "DENY"
    after_hash = canonical_hash(after_state)

    trace = {
        "scenario_id": "ESP-001",
        "claim_boundary": "synthetic path-local refusal trace only; no live runtime enforcement or downstream non-execution proof",
        "before_state": before_state,
        "before_state_hash": before_hash,
        "request": request,
        "refusal_event": refusal,
        "after_state": after_state,
        "after_state_hash": after_hash,
        "receipt": {
            "receipt_id": "RCP-2026-0512-001",
            "scenario_id": "ESP-001",
            "gate_version": "synthetic-gate-v0.1",
            "policy_reference": "ESP-001 policy rule: external messages may not be sent without fresh, scoped authority",
            "execution_layer_event": {
                "event_type": "synthetic_refusal_trace",
                "environment": "in_memory_synthetic_harness",
                "synthetic": True,
                "state_before_hash": before_hash,
                "state_after_hash": after_hash,
                "mutation_observed": before_hash != after_hash,
            },
            "attempted_action": "SEND_EXTERNAL_EMAIL",
            "actor": request["actor"],
            "action_type": request["action_type"],
            "recipient_scope": request["recipient_scope"],
            "payload_hash": request["payload_hash"],
            "missing_field": refusal["missing_field"],
            "decision": refusal["decision"],
            "refusal_reason": refusal["reason"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "downstream_send": downstream_send,
            "downstream_effect_claimed_status": "synthetic_no_effect_observed",
            "evidence": [
                {
                    "type": "state_hash_match",
                    "description": "Synthetic before_state and after_state hashes match; no mutation observed in in-memory harness.",
                    "hash": before_hash,
                },
                {
                    "type": "missing_authority_token",
                    "description": "authority_token absent at gate time; synthetic gate returns DENY before send.",
                },
            ],
            "claim_boundary": "synthetic path-local refusal evidence only; no enterprise deployment, certification, compliance, production readiness, live runtime enforcement, downstream non-execution outside the synthetic trace, or path-universal governance claim",
        },
    }

    assert refusal["decision"] == "DENY"
    assert refusal["missing_field"] == "authority_token"
    assert downstream_send is False
    assert receipt_written is True
    assert before_hash == after_hash
    assert trace["receipt"]["execution_layer_event"]["mutation_observed"] is False

    print(json.dumps(trace, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
