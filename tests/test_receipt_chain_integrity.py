import copy
import hashlib
import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "refusal_receipt_chain_v0.2.json"
SHA_PREFIX = "sha256:"


def canonical_sha256(value):
    """Return sha256 over deterministic JSON with sorted keys and compact separators."""
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return f"{SHA_PREFIX}{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def receipt_body_for_hash(receipt):
    """receipt_hash excludes receipt_hash and signature."""
    body = copy.deepcopy(receipt)
    body.pop("receipt_hash", None)
    body.pop("signature", None)
    return body


def load_fixture():
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture:
        return json.load(fixture)


def test_valid_receipt_chain_hashes_recompute():
    fixture = load_fixture()
    chain = fixture["valid_chain"]

    payloads = [
        fixture["attempted_payloads"]["payload_0001"],
        fixture["attempted_payloads"]["payload_0002"],
    ]
    decision_records = [
        fixture["decision_records"]["dec_0001"],
        fixture["decision_records"]["dec_0002"],
    ]
    state_snapshots = [
        fixture["post_refusal_state_snapshots"]["state_after_rcpt_0001"],
        fixture["post_refusal_state_snapshots"]["state_after_rcpt_0002"],
    ]

    for index, receipt in enumerate(chain):
        assert receipt["decision"] == "REFUSE"
        assert receipt["mutation_committed"] is False
        assert receipt["payload_hash"] == canonical_sha256(payloads[index])
        assert receipt["decision_record_hash"] == canonical_sha256(decision_records[index])
        assert receipt["state_snapshot_hash"] == canonical_sha256(state_snapshots[index])
        assert receipt["receipt_hash"] == canonical_sha256(receipt_body_for_hash(receipt))


def test_receipt_chain_links_to_previous_receipt_hash():
    fixture = load_fixture()
    chain = fixture["valid_chain"]

    assert chain[0]["previous_receipt_hash"] == fixture["genesis_previous_receipt_hash"]
    assert chain[1]["previous_receipt_hash"] == chain[0]["receipt_hash"]


def test_broken_previous_receipt_hash_is_rejected():
    fixture = load_fixture()
    chain = fixture["valid_chain"]
    broken_receipt = fixture["broken_chain_examples"][0]["receipt"]

    assert broken_receipt["previous_receipt_hash"] != chain[0]["receipt_hash"]
