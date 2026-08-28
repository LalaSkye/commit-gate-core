"""Canonical signed-bytes form for a DecisionRecord.

The kernel does not invent cryptography. It defines the *exact* octet
string a SignatureVerifier must authenticate. If two implementations
disagree on these bytes, they are not verifying the same object.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

SIGNED_FIELDS: tuple[str, ...] = (
    "decision_id",
    "actor_id",
    "action",
    "object_id",
    "environment",
    "commit_hash",
    "verdict",
    "policy_version",
    "issued_at",
    "expires_at",
    "nonce",
)


def signed_payload(record: Mapping[str, Any]) -> dict[str, str]:
    """Return only the fields that enter the signature."""
    missing = [name for name in SIGNED_FIELDS if name not in record]
    if missing:
        raise ValueError("MISSING_SIGNED_FIELD:" + ",".join(missing))
    payload: dict[str, str] = {}
    for name in SIGNED_FIELDS:
        value = record[name]
        if not isinstance(value, str) or value == "":
            raise ValueError(f"INVALID_SIGNED_FIELD:{name}")
        payload[name] = value
    return payload


def canonical_bytes(record: Mapping[str, Any]) -> bytes:
    """UTF-8 JSON, sorted keys, no extra whitespace.

    `signature` is excluded. Signing the signature is a loop.
    """
    payload = signed_payload(record)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
