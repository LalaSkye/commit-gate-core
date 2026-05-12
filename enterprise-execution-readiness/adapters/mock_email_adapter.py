"""
Mock downstream email adapter for ESP-001.

This adapter is intentionally synthetic and in-memory.
It proves whether the send connector would be called inside the test harness.
It does not prove live SMTP/API non-execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MockEmailAdapter:
    """In-memory stand-in for an external email connector."""

    sent_messages: List[Dict[str, Any]] = field(default_factory=list)

    def send(self, *, recipient: str, payload_hash: str, actor: str) -> Dict[str, Any]:
        event = {
            "recipient": recipient,
            "payload_hash": payload_hash,
            "actor": actor,
            "dispatched": True,
        }
        self.sent_messages.append(event)
        return event

    @property
    def send_call_count(self) -> int:
        return len(self.sent_messages)
