#!/usr/bin/env python3
"""
Validate Runtime Refusal Receipt v0.2 examples.

This validator performs two checks:
1. JSON Schema validation.
2. Local semantic checks for the synthetic receipt examples.

Claim boundary:
This validates receipt shape and internal semantic consistency only.
It does not prove downstream non-execution, production enforcement, compliance,
medical safety, financial safety, adoption, or path-universal coverage.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: jsonschema\n"
        "Install it with: python -m pip install jsonschema"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "Runtime_Refusal_Receipt_Schema_v0.2.json"
EXAMPLES_DIR = ROOT / "docs" / "schemas" / "examples"
HASH_PLACEHOLDER = "sha256:SELF_HASH_EXCLUDED"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def expected_receipt_hash(receipt: dict) -> str:
    copied = copy.deepcopy(receipt)
    copied["receipt_hash"] = HASH_PLACEHOLDER
    return "sha256:" + hashlib.sha256(canonical_json(copied).encode("utf-8")).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def semantic_checks(receipt: dict) -> None:
    verdict = receipt["verdict"]
    state = receipt["state"]
    scope = receipt["scope"]
    replay = receipt["replay"]
    downstream_status = receipt["claimed_downstream_effect_status"]

    require(verdict != "ALLOW", "ALLOW is not permitted in Runtime Refusal Receipt v0.2.")

    if verdict in {"REFUSE", "BLOCKED", "STATE_CONFLICT", "OUT_OF_SCOPE", "REPLAY_BLOCKED"}:
        require(state["execution_permitted"] is False, f"{verdict} requires state.execution_permitted=false.")

    if verdict == "OUT_OF_SCOPE":
        require(scope["scope_match"] is False, "OUT_OF_SCOPE requires scope.scope_match=false.")

    if verdict == "REPLAY_BLOCKED":
        require(replay["replay_detected"] is True, "REPLAY_BLOCKED requires replay.replay_detected=true.")

    if verdict == "STATE_CONFLICT":
        require(state["execution_permitted"] is False, "STATE_CONFLICT requires execution_permitted=false.")

    if downstream_status == "VERIFIED_NOT_COMMITTED":
        evidence_types = {item["type"] for item in receipt["evidence"]}
        require(
            "EXTERNAL_VERIFICATION" in evidence_types or "CODE_EXECUTION" in evidence_types,
            "VERIFIED_NOT_COMMITTED requires EXTERNAL_VERIFICATION or CODE_EXECUTION evidence.",
        )

    require(
        receipt["receipt_hash"] == expected_receipt_hash(receipt),
        "receipt_hash does not match canonical hash with receipt_hash excluded.",
    )


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    example_paths = sorted(EXAMPLES_DIR.glob("runtime_refusal_receipt_*_v0.2.json"))

    if not example_paths:
        raise SystemExit("No Runtime Refusal Receipt v0.2 examples found.")

    print("Runtime Refusal Receipt v0.2 Examples: VALID")
    print(f"Examples checked: {len(example_paths)}")
    print("")

    for path in example_paths:
        receipt = load_json(path)
        jsonschema.validate(instance=receipt, schema=schema)
        semantic_checks(receipt)
        print(f"- {path.name}")
        print(f"  Receipt: {receipt['id']}")
        print(f"  Verdict: {receipt['verdict']}")
        print(f"  Action class: {receipt['action_class']}")
        print(f"  Downstream status: {receipt['claimed_downstream_effect_status']}")
        print("")

    print("Claim boundary: schema-valid and semantically consistent synthetic receipts only.")
    print("This does not prove downstream non-execution or production enforcement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
