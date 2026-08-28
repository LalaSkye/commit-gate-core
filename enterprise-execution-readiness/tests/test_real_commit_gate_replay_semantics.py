"""Real CommitGate replay semantics under the single-verb contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from commit_gate_core.authorize import payload_hash
from commit_gate_core.hmac_mac import HmacSha256Verifier

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
build_gate = commit_gate_bridge.build_gate
esp001_attempt = commit_gate_bridge.esp001_attempt

KEY = b"lab-key-not-for-production"
PAYLOAD = b"esp-001-body"


def signed_record(*, nonce: str = "nonce-valid-001") -> dict[str, str]:
    attempt = esp001_attempt()
    verifier = HmacSha256Verifier(KEY)
    record = {
        "decision_id": "decision-esp-001-valid",
        "actor_id": attempt["actor_id"],
        "action": attempt["action"],
        "object_id": attempt["object_id"],
        "environment": attempt["environment"],
        "commit_hash": payload_hash(PAYLOAD),
        "verdict": "ALLOW",
        "policy_version": "esp-v0.1",
        "issued_at": "2026-05-12T09:59:00Z",
        "expires_at": "2026-05-12T10:05:00Z",
        "nonce": nonce,
        "signature": "",
    }
    record["signature"] = verifier.sign(record)
    return record


def test_hash_only_execute_never_calls_adapter() -> None:
    adapter = MockEmailAdapter()
    attempt = esp001_attempt()
    sent = []

    def mutation_callback(record_snapshot):
        sent.append(record_snapshot)
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)
    result = gate.execute(
        record=signed_record(),
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
        commit_hash=attempt["commit_hash"],
    )
    assert result.allowed is False
    assert result.code == "DENY:COMMIT_HASH_ONLY_FORBIDDEN"
    assert adapter.send_call_count == 0
    assert sent == []


def test_authorize_does_not_call_adapter_and_replay_denies() -> None:
    attempt = esp001_attempt()
    adapter = MockEmailAdapter()
    verifier = HmacSha256Verifier(KEY)

    def mutation_callback(record_snapshot):
        adapter.send(
            recipient=attempt["object_id"],
            payload_hash=attempt["commit_hash"],
            actor=attempt["actor_id"],
        )

    gate, audit = build_gate(mutation_callback=mutation_callback)
    record = signed_record(nonce="nonce-replay-allow-001")
    first = gate.execute(
        record=record,
        payload_bytes=PAYLOAD,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
    )
    replay = gate.execute(
        record=record,
        payload_bytes=PAYLOAD,
        actor_id=attempt["actor_id"],
        action=attempt["action"],
        object_id=attempt["object_id"],
        environment=attempt["environment"],
    )
    assert first.allowed is True
    assert first.code == "AUTHORIZED"
    assert replay.allowed is False
    assert replay.code == "DENY:NONCE_REPLAYED"
    assert adapter.send_call_count == 0
    assert verifier.verify(record) is True
