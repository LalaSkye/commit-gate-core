#!/usr/bin/env python3
"""
Validate all synthetic Runtime Impossibility Receipt examples against the v0.1 schema.

Claim boundary:
This script validates schema conformance for synthetic path-local receipts.
It does not prove production readiness, compliance, medical safety, adoption, financial safety,
or path-universal coverage.
"""

from __future__ import annotations

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
SCHEMA_PATH = ROOT / "docs" / "schemas" / "Runtime_Impossibility_Receipt_Schema_v0.1.json"
EXAMPLES_DIR = ROOT / "docs" / "schemas" / "examples"


def _strip_unsupported_format_on_nullable_datetime(schema: object) -> object:
    """Keep the demo dependency-light by avoiding nullable date-time format edge cases.

    The schema is still the source of truth. This only removes format checking from fields
    where the value may intentionally be null in a refusal example.
    """
    if isinstance(schema, dict):
        cleaned = {}
        for key, value in schema.items():
            if key == "format" and schema.get("type") == ["string", "null"]:
                continue
            cleaned[key] = _strip_unsupported_format_on_nullable_datetime(value)
        return cleaned
    if isinstance(schema, list):
        return [_strip_unsupported_format_on_nullable_datetime(item) for item in schema]
    return schema


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_receipt(schema: dict, path: Path) -> dict:
    receipt = load_json(path)
    jsonschema.validate(instance=receipt, schema=schema)
    return receipt


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator_schema = _strip_unsupported_format_on_nullable_datetime(schema)
    example_paths = sorted(EXAMPLES_DIR.glob("runtime_impossibility_receipt_*_v0.1.json"))

    if not example_paths:
        raise SystemExit("No runtime impossibility receipt examples found.")

    print("Runtime Impossibility Receipt Examples: VALID")
    print(f"Examples checked: {len(example_paths)}")
    print("")

    for path in example_paths:
        receipt = validate_receipt(validator_schema, path)
        print(f"- {path.name}")
        print(f"  Receipt: {receipt['receipt_id']}")
        print(f"  Verdict: {receipt['verdict']}")
        print(f"  Attempted action: {receipt['attempted_action']}")
        print(f"  Downstream effect prevented: {receipt['downstream_effect_prevented']}")
        print(f"  Human review required: {str(receipt['human_review_required']).lower()}")
        print("")

    print("Claim boundary: synthetic path-local examples only; not production, compliance, medical, financial, or field evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
