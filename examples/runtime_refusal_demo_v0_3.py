#!/usr/bin/env python3
"""
Runtime Refusal Demo v0.3

Smallest runnable path-local demo connecting:
1. a claimed v0.2 refusal receipt,
2. an execution-layer event with mutation_committed=false,
3. a before/after state hash check showing no mutation occurred on this path.

Claim boundary:
This is an in-memory synthetic demonstration only. It does not prove production readiness,
compliance, medical safety, financial safety, adoption, or path-universal coverage.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

HASH_PLACEHOLDER = "sha256:SELF_HASH_EXCLUDED"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_json(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def receipt_hash(receipt: dict) -> str:
    copied = copy.deepcopy(receipt)
    copied["receipt_hash"] = HASH_PLACEHOLDER
    return sha256_json(copied)


def snapshot_state(state: dict) -> dict:
    return copy.deepcopy(state)


def gate_check(action: dict) -> dict:
    """Return a path-local gate decision for one attempted mutation."""
    authority_valid = bool(action.get("authority_valid"))
    scope_match = action.get("requested_action_class") == action.get("allowed_action_class")

    if not authority_valid:
        return {
            "verdict": "REFUSE",
            "reason": "No valid authority was present for the requested mutation.",
            "authority_valid": False,
            "scope_match": scope_match,
            "execution_permitted": False,
        }

    if not scope_match:
        return {
            "verdict": "OUT_OF_SCOPE",
            "reason": "The authority did not cover the requested mutation class.",
            "authority_valid": True,
            "scope_match": False,
            "execution_permitted": False,
        }

    return {
        "verdict": "ALLOW",
        "reason": "Authority and scope matched.",
        "authority_valid": True,
        "scope_match": True,
        "execution_permitted": True,
    }


def execution_layer(action: dict, decision: dict, state: dict) -> dict:
    """Apply mutation only if the gate permits execution."""
    event = {
        "event_id": str(uuid4()),
        "observed_at": now_iso(),
        "action_class": action["requested_action_class"],
        "mutation_committed": False,
        "reason": "Gate refused execution before mutation.",
    }

    if decision["execution_permitted"]:
        state["records"][action["record_id"]] = action["new_value"]
        state["version"] += 1
        event["mutation_committed"] = True
        event["reason"] = "Gate allowed execution and mutation committed."

    return event


def build_v0_2_receipt(action: dict, decision: dict, before_state: dict, execution_event: dict) -> dict:
    issued_at = now_iso()
    payload_hash = sha256_json(action)
    state_snapshot_hash = sha256_json(before_state)
    evidence_hash = sha256_json(execution_event)

    receipt = {
        "schema_version": "0.2",
        "id": str(uuid4()),
        "issued_at": issued_at,
        "refused_at": execution_event["observed_at"],
        "verdict": decision["verdict"],
        "action_class": action["requested_action_class"],
        "payload_hash": payload_hash,
        "receipt_hash": HASH_PLACEHOLDER,
        "previous_receipt_hash": None,
        "authority": {
            "present": bool(action.get("authority_present")),
            "source": action.get("authority_source", "synthetic_missing_authority"),
            "valid": decision["authority_valid"],
            "issuer": "synthetic_policy_engine",
            "signature": None,
            "verification_method": "synthetic_local_gate_check",
        },
        "scope": {
            "scope_match": decision["scope_match"],
            "requested_action_class": action["requested_action_class"],
            "allowed_action_class": action.get("allowed_action_class"),
        },
        "freshness": {
            "fresh": True,
            "checked_at": issued_at,
            "clock_source": "synthetic_utc_clock",
        },
        "replay": {
            "nonce": action["nonce"],
            "replay_detected": False,
            "nonce_registry_reference": "synthetic_nonce_registry:runtime_refusal_demo_v0_3",
            "idempotency_key": action["idempotency_key"],
        },
        "state": {
            "execution_permitted": decision["execution_permitted"],
            "current_state": "mutation_not_permitted",
            "observed_at": issued_at,
            "state_snapshot_hash": state_snapshot_hash,
        },
        "evidence": [
            {
                "type": "CODE_EXECUTION",
                "uri": None,
                "hash": evidence_hash,
                "verifier": "runtime_refusal_demo_v0_3",
                "verification_method": "in_memory_execution_event_and_state_hash_check",
                "verified_at": execution_event["observed_at"],
            }
        ],
        "claimed_downstream_effect_status": "VERIFIED_NOT_COMMITTED"
        if execution_event["mutation_committed"] is False
        else "COMMITTED_DESPITE_REFUSAL",
        "reason": decision["reason"],
        "claim_boundary": "Synthetic in-memory path-local demo. Shows receipt consistency plus execution-layer event and state hash equality on one path only. Not production, compliance, medical, financial, or field evidence.",
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    return receipt


def main() -> int:
    state = {
        "version": 1,
        "records": {
            "customer_status": "draft"
        },
    }

    action = {
        "attempted_action": "mutate_record",
        "requested_action_class": "mutate_record",
        "allowed_action_class": "draft_only",
        "record_id": "customer_status",
        "new_value": "published",
        "authority_present": False,
        "authority_valid": False,
        "authority_source": "synthetic_missing_authority",
        "nonce": "demo_nonce_runtime_refusal_v0_3_001",
        "idempotency_key": "demo_idempotency_runtime_refusal_v0_3_001",
    }

    before_state = snapshot_state(state)
    before_hash = sha256_json(before_state)

    decision = gate_check(action)
    execution_event = execution_layer(action, decision, state)

    after_state = snapshot_state(state)
    after_hash = sha256_json(after_state)

    receipt = build_v0_2_receipt(action, decision, before_state, execution_event)

    state_unchanged = before_hash == after_hash
    receipt_hash_valid = receipt["receipt_hash"] == receipt_hash(receipt)

    assert decision["verdict"] == "REFUSE"
    assert execution_event["mutation_committed"] is False
    assert state_unchanged is True
    assert receipt_hash_valid is True

    print("Runtime Refusal Demo v0.3: PASS")
    print(f"Gate verdict: {decision['verdict']}")
    print(f"Mutation committed: {str(execution_event['mutation_committed']).lower()}")
    print(f"Before state hash: {before_hash}")
    print(f"After state hash:  {after_hash}")
    print(f"State unchanged: {str(state_unchanged).lower()}")
    print(f"Receipt hash valid: {str(receipt_hash_valid).lower()}")
    print(f"Receipt verdict: {receipt['verdict']}")
    print(f"Downstream status: {receipt['claimed_downstream_effect_status']}")
    print("Claim boundary: synthetic path-local demo only; not production or path-universal evidence.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
