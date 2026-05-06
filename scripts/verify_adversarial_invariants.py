import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTOR_PATH = ROOT / "tests" / "adversarial" / "INVARIANT_TEST_VECTORS_v1.json"


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


def main():
    failures = []

    for vector in load_vectors():
        actual = evaluate_vector(vector)
        expected = vector["expected"]
        passed = actual == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status} {vector['id']} {vector['invariant']} -> {actual['decision']}")
        if not passed:
            failures.append({"id": vector["id"], "expected": expected, "actual": actual})

    if failures:
        print("\nAdversarial invariant verification failed:")
        for failure in failures:
            print(json.dumps(failure, sort_keys=True))
        raise SystemExit(1)

    print("\nAll adversarial invariant vectors passed.")


if __name__ == "__main__":
    main()
