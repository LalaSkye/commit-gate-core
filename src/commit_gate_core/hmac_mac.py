"""Reference MAC over canonical_bytes.

This is a *symmetric* authenticator for tests and local labs.
It is not Ed25519. Do not call it a public-key signature in READMEs.
The authorize-only kernel accepts a verifier by dependency injection;
this helper does not apply payloads or provide production key management.
"""

from __future__ import annotations

import hmac
from hashlib import sha256
from typing import Any, Mapping

from .canonical import canonical_bytes


class HmacSha256Verifier:
    def __init__(self, key: bytes) -> None:
        if not key:
            raise ValueError("HMAC key must be non-empty")
        self._key = key

    def sign(self, record: Mapping[str, Any]) -> str:
        digest = hmac.new(self._key, canonical_bytes(record), sha256).hexdigest()
        return "hmac-sha256:" + digest

    def verify(self, record: Mapping[str, Any]) -> bool:
        offered = record.get("signature")
        if not isinstance(offered, str) or not offered.startswith("hmac-sha256:"):
            return False
        expected = self.sign(record)
        return hmac.compare_digest(offered, expected)
