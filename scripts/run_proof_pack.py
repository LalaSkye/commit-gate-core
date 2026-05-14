"""Proof Pack v0.1 runner.

Runs four authority-before-mutation cases through the existing CommitGate
kernel in src/commit_gate_core/gate.py:

    1. valid DecisionRecord   -> ALLOW, mutation runs once
    2. expired authority      -> DENY:DECISION_EXPIRED, no mutation
    3. scope mismatch         -> DENY:SCOPE_MISMATCH:object_id, no mutation
    4. replayed nonce         -> DENY:NONCE_REPLAYED, no mutation

For each case, writes a receipt JSON to receipts/ and prints:
    case name, expected result, actual result, receipt path,
    receipt hash, mutation occurred (YES/NO).

Stdlib only. No install step.

Claim boundary:
    This is a bounded proof surface for authority-before-mutation on the
    demonstrated CommitGate path. Not production infrastructure, not
    certification, not adoption evidence, not universal runtime governance.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional


_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from commit_gate_core.gate import CommitGate, GateResult  # noqa: E402


DEMO_DIR = _REPO_ROOT / "demo"
RECEIPTS_DIR = _REPO_ROOT / "receipts" / "examples"


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class FixedClock:
    """Deterministic clock pinned just after the valid record's issued_at."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class AcceptingSignatureVerifier:
    """Treats any record with signature == 'sig_valid' as signed.

    Synthetic: the bounded proof does not exercise real crypto.
    """

    def verify(self, record: Mapping[str, Any]) -> bool:
        return record.get("signature") == "sig_valid"


class InMemoryNonceLedger:
    def __init__(self, preloaded: Optional[set[str]] = None) -> None:
        self.used: set[str] = set(preloaded or set())

    def contains(self, nonce: str) -> bool:
        return nonce in self.used

    def consume(self, nonce: str, decision_id: str) -> None:
        if nonce in self.used:
            raise RuntimeError("nonce already consumed")
        self.used.add(nonce)

    def rollback(self, nonce: str, decision_id: str) -> None:
        self.used.discard(nonce)


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))


class MutationCounter:
    def __init__(self) -> None:
        self.calls: list[Mapping[str, Any]] = []

    def __call__(self, record: Mapping[str, Any]) -> None:
        self.calls.append(dict(record))


def load_record(name: str) -> dict[str, Any]:
    return json.loads((DEMO_DIR / name).read_text(encoding="utf-8"))


def build_receipt(
    *,
    case_name: str,
    expected_result: str,
    record: Mapping[str, Any],
    gate_result: GateResult,
    audit_event: Mapping[str, Any],
    mutation_occurred: bool,
) -> dict[str, Any]:
    """Build an inspectable receipt for one case.

    Fields:
        receipt_id, case_name, expected_result, actual_result,
        input_hash, mutation_occurred, no_execution_marker,
        refusal_reason, gate_audit_event, schema_version, receipt_hash
    """
    actual_result = "ALLOW" if gate_result.allowed else "DENY"
    refusal_reason = None if gate_result.allowed else gate_result.code

    receipt: dict[str, Any] = {
        "schema_version": "proof-pack-v0.1",
        "receipt_id": f"RCP-PP-{case_name}",
        "case_name": case_name,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "decision_id": gate_result.decision_id,
        "timestamp": gate_result.timestamp,
        "input_hash": stable_hash(dict(record)),
        "mutation_occurred": mutation_occurred,
        "no_execution_marker": (not mutation_occurred),
        "refusal_reason": refusal_reason,
        "gate_audit_event": dict(audit_event),
        "claim_boundary": (
            "bounded proof surface for authority-before-mutation on the "
            "demonstrated CommitGate path; not production, not certification, "
            "not universal runtime governance"
        ),
    }
    receipt["receipt_hash"] = stable_hash(
        {k: v for k, v in receipt.items() if k != "receipt_hash"}
    )
    return receipt


def write_receipt(receipt: Mapping[str, Any], filename: str) -> Path:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS_DIR / filename
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def make_gate(
    *,
    preloaded_nonces: Optional[set[str]] = None,
    now: datetime,
) -> tuple[CommitGate, RecordingAuditSink, MutationCounter]:
    audit = RecordingAuditSink()
    mutation = MutationCounter()
    gate = CommitGate(
        verifier=AcceptingSignatureVerifier(),
        nonce_ledger=InMemoryNonceLedger(preloaded=preloaded_nonces),
        audit=audit,
        mutation_callback=mutation,
        accepted_policy_versions=("2026-04-27.1",),
        clock=FixedClock(now),
    )
    return gate, audit, mutation


def run_case(
    *,
    case_name: str,
    record_file: str,
    expected_result: str,
    receipt_filename: str,
    preloaded_nonces: Optional[set[str]] = None,
    now: datetime,
    scope_override: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    record = load_record(record_file)
    gate, audit, mutation = make_gate(preloaded_nonces=preloaded_nonces, now=now)

    # Caller's claimed scope: always the canonical scope. The record may diverge
    # (scope_override is unused — we keep caller scope fixed and let the record
    # disagree to drive scope_mismatch).
    scope = {
        "actor_id": "agent_17",
        "action": "approve_invoice",
        "object_id": "invoice_778",
        "environment": "prod",
        "commit_hash": "sha256:abc123",
    }
    if scope_override is not None:
        scope.update(scope_override)

    gate_result = gate.execute(record=record, **scope)
    audit_event = audit.events[-1] if audit.events else {}
    mutation_occurred = len(mutation.calls) > 0

    receipt = build_receipt(
        case_name=case_name,
        expected_result=expected_result,
        record=record,
        gate_result=gate_result,
        audit_event=audit_event,
        mutation_occurred=mutation_occurred,
    )
    receipt_path = write_receipt(receipt, receipt_filename)

    return {
        "case_name": case_name,
        "expected_result": expected_result,
        "actual_result": receipt["actual_result"],
        "receipt_path": str(receipt_path.relative_to(_REPO_ROOT)),
        "receipt_hash": receipt["receipt_hash"],
        "mutation_occurred": mutation_occurred,
        "gate_code": gate_result.code,
    }


def main() -> int:
    now = datetime(2026, 4, 27, 5, 1, tzinfo=timezone.utc)

    cases = []

    cases.append(
        run_case(
            case_name="valid_decision_record",
            record_file="valid_decision_record.json",
            expected_result="ALLOW",
            receipt_filename="allow_receipt.json",
            preloaded_nonces=None,
            now=now,
        )
    )

    cases.append(
        run_case(
            case_name="expired_authority",
            record_file="expired_authority_refusal.json",
            expected_result="DENY_EXPIRED",
            receipt_filename="deny_expired_receipt.json",
            preloaded_nonces=None,
            now=now,
        )
    )

    cases.append(
        run_case(
            case_name="scope_mismatch",
            record_file="scope_mismatch_refusal.json",
            expected_result="DENY_SCOPE",
            receipt_filename="deny_scope_receipt.json",
            preloaded_nonces=None,
            now=now,
        )
    )

    cases.append(
        run_case(
            case_name="replayed_nonce",
            record_file="replayed_nonce_refusal.json",
            expected_result="DENY_REPLAY",
            receipt_filename="deny_replay_receipt.json",
            preloaded_nonces={"nonce_already_used_001"},
            now=now,
        )
    )

    expected_codes = {
        "valid_decision_record": "ALLOW",
        "expired_authority": "DENY:DECISION_EXPIRED",
        "scope_mismatch": "DENY:SCOPE_MISMATCH:object_id",
        "replayed_nonce": "DENY:NONCE_REPLAYED",
    }

    all_pass = True
    print("=" * 72)
    print("Proof Pack v0.1 — authority-before-mutation on CommitGate path")
    print("=" * 72)
    for case in cases:
        expected_code = expected_codes[case["case_name"]]
        code_ok = case["gate_code"] == expected_code
        if case["case_name"] == "valid_decision_record":
            mutation_ok = case["mutation_occurred"] is True
        else:
            mutation_ok = case["mutation_occurred"] is False
        case_pass = code_ok and mutation_ok
        all_pass = all_pass and case_pass

        print()
        print(f"Case:               {case['case_name']}")
        print(f"Expected result:    {case['expected_result']}")
        print(f"Actual result:      {case['actual_result']} ({case['gate_code']})")
        print(f"Receipt path:       {case['receipt_path']}")
        print(f"Receipt hash:       {case['receipt_hash']}")
        print(f"Mutation occurred:  {'YES' if case['mutation_occurred'] else 'NO'}")
        print(f"Case pass:          {'YES' if case_pass else 'NO'}")

    print()
    print("=" * 72)
    print(f"All four cases pass: {'YES' if all_pass else 'NO'}")
    print("=" * 72)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
