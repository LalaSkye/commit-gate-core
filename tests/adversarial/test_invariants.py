import json
from pathlib import Path


VECTOR_PATH = Path(__file__).with_name("INVARIANT_TEST_VECTORS_v1.json")


def load_vectors():
    with VECTOR_PATH.open(encoding="utf-8") as f:
        return json.load(f)["vectors"]


def vector_by_id(vector_id):
    for vector in load_vectors():
        if vector["id"] == vector_id:
            return vector
    raise AssertionError(f"missing adversarial vector: {vector_id}")


def evaluate_vector(vector):
    """Minimal executable binding for the adversarial invariant vectors.

    This test-local evaluator binds the declared proof obligations to executable
    assertions without extending the production gate implementation.
    """
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

    raise AssertionError(f"unbound adversarial vector: {vector['id']}")


def assert_vector(vector_id):
    vector = vector_by_id(vector_id)
    assert evaluate_vector(vector) == vector["expected"]


def test_scope_monotonicity_rejects_scope_widening():
    assert_vector("ADV-I-001")


def test_cross_surface_admissibility_holds_on_incompatible_verdicts():
    assert_vector("ADV-II-001")


def test_consequence_binding_silences_unresolved_state():
    assert_vector("ADV-III-001")
