"""
Real CommitGate replay semantics tests for enterprise-shaped ESP-001.

These tests call commit_gate_core.gate.CommitGate directly through the bridge.
They remain synthetic and in-memory. They do not prove live runtime enforcement,
production non-execution, enterprise readiness, or path-universal governance.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "adapters" / "mock_email_adapter.py"
BRIDGE_PATH = ROOT / "adapters" / "commit_gate_bridge.py"

adapter_spec = importlib.util.spec_from_file_location("mock_email_adapter", ADAPTER_PATH)
mock_email_adapter = importlib.util.module_from_spec(adapter_spec)
assert adapter_spec.loader is not None
# Register the module in sys.modules before executing it.
# Without this, any @dataclass in the loaded module fails at import time:
# dataclasses resolves sys.modules[cls.__module__].__dict__, which is None
# for a module built by module_from_spec but never registered.
# Recorded 2026-08-05.
sys.modules[adapter_spec.name] = mock_email_adapter
adapter_spec.loader.exec_module(mock_email_adapter)
MockEmailAdapter = mock_email_adapter.MockEmailAdapter

bridge_spec = importlib.util.spec_from_file_location("commit_gate_bridge", BRIDGE_PATH)
commit_gate_bridge = importlib.util.module_from_spec(bridge_spec)
assert bridge_spec.loader is not None
sys.modules[bridge_spec.name] = commit_gate_bridge
bridge_spec.loader.exec_module(commit_gate_bridge)

build_gate = commit_gate_bridge.build_gate
esp001_attempt = commit_gate_bridge.esp001_attempt


def valid_decision_record(*, nonce: str = "nonce-valid-001") -> dict[str, str]:
    attempt = esp001_attempt()
    return {
        "decision_id": "decision-esp-001-valid",
        "actor_id": attempt["actor_id"],
        "action": attempt["action"],
        "object_id": attempt["object_id"],
        "environment": attempt["environment"],
        "commit_hash": attempt["commit_hash"],
        "verdict": "ALLOW",
        "policy_version": "esp-v0.1",
        "issued_at": "2026-05-12T09:59:00Z",
        "expires_at": "2026-05-12T10:05:00Z",
        "nonce": nonce,
        "signature": "signed:test-signature",
    }


def execute_with_record(adapter, record):
    attempt = esp001_attempt()

    def mutation_callback(record_snapshot):
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)
    result = gate.execute(
        record=record,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )
    return result, audit


def test_real_commit_gate_allows_valid_record_and_calls_adapter_once() -> None:
    adapter = MockEmailAdapter()
    result, audit = execute_with_record(adapter, valid_decision_record())

    assert result.allowed is True
    assert result.code == "ALLOW"
    assert adapter.send_call_count == 1
    assert len(adapter.sent_messages) == 1
    assert len(audit.events) == 1
    assert audit.events[0]["allowed"] is True
    assert audit.events[0]["code"] == "ALLOW"


def test_real_commit_gate_replay_after_allow_denies_and_does_not_call_adapter_again() -> None:
    attempt = esp001_attempt()
    adapter = MockEmailAdapter()

    def mutation_callback(record_snapshot):
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)
    record = valid_decision_record(nonce="nonce-replay-allow-001")

    first = gate.execute(
        record=record,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )
    replay = gate.execute(
        record=record,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )

    assert first.allowed is True
    assert first.code == "ALLOW"
    assert replay.allowed is False
    assert replay.code == "DENY:NONCE_REPLAYED"
    assert adapter.send_call_count == 1
    assert len(adapter.sent_messages) == 1
    assert len(audit.events) == 2
    assert audit.events[0]["code"] == "ALLOW"
    assert audit.events[1]["code"] == "DENY:NONCE_REPLAYED"


def test_real_commit_gate_missing_record_denial_is_stable_and_does_not_consume_nonce() -> None:
    attempt = esp001_attempt()
    adapter = MockEmailAdapter()

    def mutation_callback(record_snapshot):
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)

    first = gate.execute(
        record=None,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )
    second = gate.execute(
        record=None,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )

    assert first.allowed is False
    assert second.allowed is False
    assert first.code == "DENY:NO_DECISION_RECORD"
    assert second.code == "DENY:NO_DECISION_RECORD"
    assert adapter.send_call_count == 0
    assert adapter.sent_messages == []
    assert len(audit.events) == 2
    assert audit.events[0]["code"] == audit.events[1]["code"] == "DENY:NO_DECISION_RECORD"
