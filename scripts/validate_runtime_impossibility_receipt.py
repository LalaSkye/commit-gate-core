#!/usr/bin/env python3
"""
Validate the synthetic Runtime Impossibility Receipt example against the v0.1 schema.

Claim boundary:
This script validates schema conformance for a synthetic path-local receipt.
It does not prove production readiness, compliance, medical safety, adoption, or path-universal coverage.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: jsonschema\n"
        "Install it with: python -m pip install jsonschema"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "Runtime_Impossibility_Receipt_Schema_v0.1.json"
RECEIPT_PATH = ROOT / "docs" / "schemas" / "examples" / "runtime_impossibility_receipt_email_refusal_v0.1.json"


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


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    receipt = load_json(RECEIPT_PATH)

    validator_schema = _strip_unsupported_format_on_nullable_datetime(schema)
    jsonschema.validate(instance=receipt, schema=validator_schema)

    print("Runtime Impossibility Receipt: VALID")
    print(f"Verdict: {receipt['verdict']}")
    print(f"Attempted action: {receipt['attempted_action']}")
    print(f"Downstream effect prevented: {receipt['downstream_effect_prevented']}")
    print(f"Human review required: {str(receipt['human_review_required']).lower()}")
    print(f"Claim boundary: {receipt['claim_boundary']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
