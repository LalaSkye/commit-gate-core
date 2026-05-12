"""
ESP-001 downstream non-call test.

This is a synthetic, in-memory pytest check.
It proves the mock email adapter is not called when authority_token is missing.
It does not prove live SMTP/API non-execution or enterprise readiness.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "adapters" / "mock_email_adapter.py"

spec = importlib.util.spec_from_file_location("mock_email_adapter", ADAPTER_PATH)
mock_email_adapter = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mock_email_adapter)
MockEmailAdapter = mock_email_adapter.MockEmailAdapter


PAYLOAD_HASH = "sha256:a3f8c2d1e7b904561ac38fd2e190bba47c2d3f8a1e056b7c9d4e2f1a8b3c7d90"


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
                "reason": f"{field} absent",
            }

    return {"decision": "ALLOW", "missing_field": None, "reason": "all required fields present"}


def dispatch_if_allowed(request: Dict[str, Any], adapter: MockEmailAdapter) -> Dict[str, Any]:
    verdict = evaluate_gate(request)

    if verdict["decision"] != "ALLOW":
        return {
            "decision": verdict["decision"],
            "missing_field": verdict["missing_field"],
            "downstream_send": False,
            "send_call_count": adapter.send_call_count,
            "receipt_written": True,
        }

    adapter.send(
        recipient=request["recipient_scope"],
        payload_hash=request["payload_hash"],
        actor=request["actor"],
    )
    return {
        "decision": "ALLOW",
        "missing_field": None,
        "downstream_send": True,
        "send_call_count": adapter.send_call_count,
        "receipt_written": False,
    }


def test_missing_authority_token_never_calls_mock_email_adapter() -> None:
    adapter = MockEmailAdapter()
    request = {
        "actor": "agent://morpheus-draft-bot-v1",
        "action_type": "SEND_EXTERNAL_EMAIL",
        "recipient_scope": "external:partner-domain.com",
        "payload_hash": PAYLOAD_HASH,
        "authority_token": None,
        "expiry": "2026-05-12T10:05:00Z",
        "nonce": "nonce-esp-001",
    }

    result = dispatch_if_allowed(request, adapter)

    assert result["decision"] == "DENY"
    assert result["missing_field"] == "authority_token"
    assert result["downstream_send"] is False
    assert result["send_call_count"] == 0
    assert adapter.sent_messages == []
    assert result["receipt_written"] is True


def test_valid_authority_calls_mock_email_adapter_once() -> None:
    adapter = MockEmailAdapter()
    request = {
        "actor": "agent://morpheus-draft-bot-v1",
        "action_type": "SEND_EXTERNAL_EMAIL",
        "recipient_scope": "external:partner-domain.com",
        "payload_hash": PAYLOAD_HASH,
        "authority_token": "signed:test-authority-token",
        "expiry": "2026-05-12T10:05:00Z",
        "nonce": "nonce-esp-001-valid",
    }

    result = dispatch_if_allowed(request, adapter)

    assert result["decision"] == "ALLOW"
    assert result["downstream_send"] is True
    assert result["send_call_count"] == 1
    assert len(adapter.sent_messages) == 1
