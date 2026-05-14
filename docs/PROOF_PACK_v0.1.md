# Proof Pack v0.1 — Authority-Before-Mutation

Bounded public proof that, on the demonstrated CommitGate path, state
mutation is refused unless the attached `DecisionRecord` is valid,
scoped, unexpired, signed, and unreplayed — and that every refusal
produces an inspectable receipt.

## How to run in 60 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python3 scripts/run_proof_pack.py
python3 scripts/verify_receipt.py
```

No install step. Stdlib only. The runner exercises four cases through
the existing kernel at `src/commit_gate_core/gate.py`:

| Case | Demo fixture | Expected | Receipt |
| --- | --- | --- | --- |
| valid DecisionRecord | `demo/valid_decision_record.json` | ALLOW | `receipts/examples/allow_receipt.json` |
| expired authority | `demo/expired_authority_refusal.json` | DENY_EXPIRED | `receipts/examples/deny_expired_receipt.json` |
| scope mismatch | `demo/scope_mismatch_refusal.json` | DENY_SCOPE | `receipts/examples/deny_scope_receipt.json` |
| replayed nonce | `demo/replayed_nonce_refusal.json` | DENY_REPLAY | `receipts/examples/deny_replay_receipt.json` |

## Expected output

`scripts/run_proof_pack.py` prints, for each case: case name, expected
result, actual result, receipt path, receipt hash, mutation occurred
(`YES` / `NO`). The run ends with:

```text
All four cases pass: YES
```

`scripts/verify_receipt.py` then checks each receipt in
`receipts/examples/` against five gates:

1. `receipt_hash_integrity` — sha256 over the receipt minus
   `receipt_hash` matches the stored value
2. `input_hash` — the hash of the input DecisionRecord is present and
   well-formed
3. `decision_result` — `actual_result` matches `expected_result`
4. `refusal_reason` — present and non-empty on DENY receipts, `null`
   on ALLOW receipts
5. `no_execution_marker` — `no_execution_marker` is the inverse of
   `mutation_occurred`; DENY receipts must show `mutation_occurred=false`

A clean run ends with:

```text
All receipts verified: YES
```

## What this proves

On the demonstrated CommitGate path:

- A signed, scoped, unexpired, unreplayed `DecisionRecord` is a hard
  precondition for the mutation callback to run.
- Each of the four failure modes — `DECISION_EXPIRED`,
  `SCOPE_MISMATCH:object_id`, `NONCE_REPLAYED`, and the ALLOW happy
  path — flows through the kernel in `src/commit_gate_core/gate.py`
  and produces a distinct, content-addressed receipt with an explicit
  no-execution marker.
- Refusal receipts can be inspected independently by
  `scripts/verify_receipt.py` without re-running the gate.

The receipts and DecisionRecord fixtures live in version control, so
the evidence object is reproducible byte-for-byte.

## What this does not prove

- Production readiness, certification, or compliance.
- Adoption, deployment, or coverage outside this repository.
- Universal runtime governance, path-universal enforcement, or
  non-bypassability outside the demonstrated path.
- Real cryptographic signature verification — the bundled
  `AcceptingSignatureVerifier` is synthetic and treats
  `signature == "sig_valid"` as signed for the purpose of the bounded
  surface.
- Real persistent nonce ledgers, atomic commit across systems, or
  downstream side-effect prevention beyond the in-process callback.

## Claim boundary

This proof pack demonstrates that, on the shown path, state mutation
is refused unless a DecisionRecord is valid, scoped, unexpired, signed,
and unreplayed; each refusal produces an inspectable receipt.

This is not production infrastructure, certification, adoption
evidence, or universal runtime governance. It is a bounded proof
surface for authority-before-mutation.
