"""ESP-001 real CommitGate bridge test.

Hash-only execute is forbidden. The mock adapter must not be called.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "adapters" / "mock_email_adapter.py"
BRIDGE_PATH = ROOT / "adapters" / "commit_gate_bridge.py"

adapter_spec = importlib.util.spec_from_file_location("mock_email_adapter", ADAPTER_PATH)
mock_email_adapter = importlib.util.module_from_spec(adapter_spec)
assert adapter_spec.loader is not None
sys.modules[adapter_spec.name] = mock_email_adapter
adapter_spec.loader.exec_module(mock_email_adapter)
MockEmailAdapter = mock_email_adapter.MockEmailAdapter

bridge_spec = importlib.util.spec_from_file_location("commit_gate_bridge", BRIDGE_PATH)
commit_gate_bridge = importlib.util.module_from_spec(bridge_spec)
assert bridge_spec.loader is not None
sys.modules[bridge_spec.name] = commit_gate_bridge
bridge_spec.loader.exec_module(commit_gate_bridge)
dispatch_esp001_through_real_gate = commit_gate_bridge.dispatch_esp001_through_real_gate


def test_real_commit_gate_hash_only_execute_blocks_mock_email_send() -> None:
    adapter = MockEmailAdapter()
    result = dispatch_esp001_through_real_gate(adapter)

    assert result.gate_result.allowed is False
    assert result.gate_result.code == "DENY:COMMIT_HASH_ONLY_FORBIDDEN"
    assert result.downstream_send is False
    assert result.send_call_count == 0
    assert adapter.sent_messages == []
    assert result.receipt_written is True
    assert len(result.audit_events) == 1
    audit_event = result.audit_events[0]
    assert audit_event["event_type"] == "GATE_REFUSED"
    assert audit_event["allowed"] is False
    assert audit_event["code"] == "DENY:COMMIT_HASH_ONLY_FORBIDDEN"
