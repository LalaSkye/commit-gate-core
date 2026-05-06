import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTOR_PATH = ROOT / "tests" / "adversarial" / "INVARIANT_TEST_VECTORS_v1.json"
DEFAULT_RECEIPT_PATH = ROOT / "tests" / "adversarial" / "latest_verification_receipt.json"


def load_vectors():
    with VECTOR_PATH.open(encoding="utf-8") as f:
        return json.load(f)["vectors"]


def evaluate_vector(vector):
    inputs = vector["input"]

    if vector["id"] == "ADV-I-001":
        delegator_scope = set(inputs["delegator_scope"])
        delegate_scope = set(inputs["delegate_scope"])
        if not delegate_scope.issubset(delegator_scope):
            return {"decision": "DENY", "execution_allowed": False, "receipt_required": True}
        return {"decision": "ALLOW", "execution_allowed": True, "receipt_required": True}

    if vector["id"] == "ADV-II-001":
        verdicts = [value for value in inputs.values() if value is not None]
        if "DENY" in verdicts:
            return {"decision": "DENY", "execution_allowed": False, "receipt_required": True}
        if len(set(verdicts)) > 1:
            return {"decision": "HOLD", "execution_allowed": False, "receipt_required": True}
        return {"decision": verdicts[0], "execution_allowed": verdicts[0] == "ALLOW", "receipt_required": True}

    if vector["id"] == "ADV-III-001":
        if any(value is None for value in inputs.values()):
            return {"decision": "SILENCE", "execution_allowed": False, "receipt_required": True}
        return {"decision": "ALLOW", "execution_allowed": True, "receipt_required": True}

    raise ValueError(f"unbound adversarial vector: {vector['id']}")


def build_receipt(results, failures):
    return {
        "receipt_type": "ADVERSARIAL_INVARIANT_VERIFICATION",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "vector_file": str(VECTOR_PATH.relative_to(ROOT)),
        "result": "PASS" if not failures else "FAIL",
        "vectors_checked": len(results),
        "results": results,
        "failures": failures,
        "claim_limit": "This receipt proves only local evaluation of declared adversarial vectors. It does not prove production runtime enforcement or CI success.",
    }


def write_receipt(receipt, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Verify adversarial invariant vectors.")
    parser.add_argument(
        "--receipt",
        nargs="?",
        const=str(DEFAULT_RECEIPT_PATH),
        default=None,
        help="Write a JSON verification receipt. Optionally pass a path.",
    )
    args = parser.parse_args()

    failures = []
    results = []

    for vector in load_vectors():
        actual = evaluate_vector(vector)
        expected = vector["expected"]
        passed = actual == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status} {vector['id']} {vector['invariant']} -> {actual['decision']}")

        result = {
            "id": vector["id"],
            "invariant": vector["invariant"],
            "passed": passed,
            "expected": expected,
            "actual": actual,
        }
        results.append(result)

        if not passed:
            failures.append(result)

    receipt = build_receipt(results, failures)

    if args.receipt:
        receipt_path = Path(args.receipt)
        if not receipt_path.is_absolute():
            receipt_path = ROOT / receipt_path
        write_receipt(receipt, receipt_path)
        print(f"\nReceipt written: {receipt_path.relative_to(ROOT)}")

    if failures:
        print("\nAdversarial invariant verification failed:")
        for failure in failures:
            print(json.dumps(failure, sort_keys=True))
        raise SystemExit(1)

    print("\nAll adversarial invariant vectors passed.")


if __name__ == "__main__":
    main()
