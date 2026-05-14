"""Proof Pack v0.1 receipt verifier.

Checks for every receipt file passed on the command line:

    1. receipt hash integrity     (recompute sha256 over all fields except
                                   receipt_hash and compare)
    2. input hash                 (present, well-formed sha256:<hex>)
    3. decision result            (actual_result matches expected_result, with
                                   DENY_* expected mapping to actual DENY)
    4. refusal reason             (present and non-empty for DENY; null for ALLOW)
    5. no-execution marker        (mutation_occurred is the inverse of
                                   no_execution_marker; for DENY cases,
                                   no_execution_marker must be True and
                                   mutation_occurred must be False)

Exit status:
    0 — all receipts verified
    1 — at least one check failed

If no paths are given, verifies every JSON file in receipts/examples/.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = _REPO_ROOT / "receipts" / "examples"

SHA256_HEX = re.compile(r"^sha256:[0-9a-f]{64}$")


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _check_hash_integrity(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    stored = receipt.get("receipt_hash")
    if not isinstance(stored, str) or not SHA256_HEX.match(stored):
        return False, "receipt_hash missing or malformed"
    recomputed = stable_hash({k: v for k, v in receipt.items() if k != "receipt_hash"})
    if recomputed != stored:
        return False, f"receipt_hash mismatch: stored={stored} recomputed={recomputed}"
    return True, "ok"


def _check_input_hash(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    input_hash = receipt.get("input_hash")
    if not isinstance(input_hash, str) or not SHA256_HEX.match(input_hash):
        return False, "input_hash missing or malformed"
    return True, "ok"


def _check_decision_result(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    expected = receipt.get("expected_result")
    actual = receipt.get("actual_result")
    if not isinstance(expected, str) or not isinstance(actual, str):
        return False, "expected_result or actual_result missing"
    if expected == "ALLOW":
        ok = actual == "ALLOW"
    elif expected.startswith("DENY"):
        ok = actual == "DENY"
    else:
        return False, f"unknown expected_result: {expected}"
    if not ok:
        return False, f"expected {expected} but actual is {actual}"
    return True, "ok"


def _check_refusal_reason(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    actual = receipt.get("actual_result")
    reason = receipt.get("refusal_reason")
    if actual == "ALLOW":
        if reason is not None:
            return False, f"ALLOW receipt must have null refusal_reason, got {reason!r}"
        return True, "ok"
    if actual == "DENY":
        if not isinstance(reason, str) or not reason:
            return False, "DENY receipt must have non-empty refusal_reason"
        return True, "ok"
    return False, f"unknown actual_result: {actual}"


def _check_no_execution_marker(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    mutation = receipt.get("mutation_occurred")
    marker = receipt.get("no_execution_marker")
    actual = receipt.get("actual_result")
    if not isinstance(mutation, bool) or not isinstance(marker, bool):
        return False, "mutation_occurred / no_execution_marker must be booleans"
    if marker == mutation:
        return False, "no_execution_marker must be the inverse of mutation_occurred"
    if actual == "DENY":
        if mutation is not False or marker is not True:
            return (
                False,
                "DENY receipt must have mutation_occurred=False and no_execution_marker=True",
            )
    if actual == "ALLOW":
        if mutation is not True or marker is not False:
            return (
                False,
                "ALLOW receipt must have mutation_occurred=True and no_execution_marker=False",
            )
    return True, "ok"


CHECKS = (
    ("receipt_hash_integrity", _check_hash_integrity),
    ("input_hash", _check_input_hash),
    ("decision_result", _check_decision_result),
    ("refusal_reason", _check_refusal_reason),
    ("no_execution_marker", _check_no_execution_marker),
)


def verify_file(path: Path) -> bool:
    print(f"Verifying: {path.relative_to(_REPO_ROOT) if path.is_relative_to(_REPO_ROOT) else path}")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  ERROR: could not parse JSON: {exc}")
        return False
    if not isinstance(receipt, dict):
        print("  ERROR: receipt root must be an object")
        return False

    file_ok = True
    for name, check in CHECKS:
        ok, detail = check(receipt)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}: {detail}")
        if not ok:
            file_ok = False
    return file_ok


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(arg) for arg in argv]
    else:
        if not DEFAULT_DIR.is_dir():
            print(f"No paths given and {DEFAULT_DIR} does not exist")
            return 1
        paths = sorted(p for p in DEFAULT_DIR.iterdir() if p.suffix == ".json")
        if not paths:
            print(f"No JSON receipts found in {DEFAULT_DIR}")
            return 1

    all_ok = True
    for path in paths:
        ok = verify_file(path)
        all_ok = all_ok and ok
        print()

    print("=" * 60)
    print(f"All receipts verified: {'YES' if all_ok else 'NO'}")
    print("=" * 60)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
