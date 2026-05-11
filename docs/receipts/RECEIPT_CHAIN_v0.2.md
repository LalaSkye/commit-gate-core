# RECEIPT_CHAIN_v0.2

Status: Design and test artefact only.

Scope: Narrow, path-local proof surface for hash-linked refusal receipts.

Claim boundary: This does not claim production readiness, compliance, tamper-proofing, or path-universal governance. It describes one bounded receipt-chain pattern for inspection and testing.

## Purpose

A refusal receipt should not only say that an action was refused.

It should also be possible to inspect whether that receipt belongs to a coherent receipt chain, whether the attempted payload and decision record are bound to the receipt, and whether the system recorded that no mutation was committed.

This artefact defines the smallest useful receipt-chain brick for `commit-gate-core`.

## Core invariant

No consequence-producing mutation is permitted unless the gate returns an admissible decision.

If the gate refuses, the refusal must be recorded before mutation and the receipt must bind:

1. the attempted payload,
2. the decision record,
3. the refusal reason,
4. the previous receipt hash,
5. the current receipt hash,
6. evidence that mutation did not commit.

## Minimal receipt fields

```json
{
  "receipt_id": "rcpt_0002",
  "previous_receipt_hash": "sha256:...",
  "payload_hash": "sha256:...",
  "decision_record_hash": "sha256:...",
  "decision": "REFUSE",
  "refusal_reason": "missing_valid_authority",
  "mutation_committed": false,
  "state_snapshot_hash": "sha256:...",
  "timestamp_utc": "2026-05-11T00:00:00Z",
  "receipt_hash": "sha256:...",
  "signature": null
}
```

## Hashing rule

`receipt_hash` is calculated over the canonical receipt body excluding `receipt_hash` and `signature`.

Canonicalisation must be deterministic.

The minimum acceptable test is:

1. Same receipt body produces the same hash.
2. Any payload change changes `payload_hash`.
3. Any decision record change changes `decision_record_hash`.
4. Any receipt body change changes `receipt_hash`.
5. Any broken `previous_receipt_hash` breaks chain verification.

## State snapshot rule

`mutation_committed: false` is only accepted when paired with a `state_snapshot_hash` taken after refusal and verified against the expected unchanged state for the tested path.

The `state_snapshot_hash` proves only that the tested path's expected post-refusal state remained unchanged on this synthetic run.

The snapshot is path-local. It does not prove that every downstream or external mutation route was blocked.

## Verification procedure

A verifier should check:

1. `decision` is `REFUSE`.
2. `mutation_committed` is `false`.
3. `state_snapshot_hash` matches the expected unchanged post-refusal state for the tested path.
4. `payload_hash` matches the attempted payload.
5. `decision_record_hash` matches the DecisionRecord used by the gate.
6. `previous_receipt_hash` matches the prior receipt in the chain.
7. `receipt_hash` recomputes correctly from the canonical receipt body.
8. Optional signature verifies against the declared signing key, if signatures are enabled.

## Signature status

Signature support is optional in v0.2.

If used, the signature must bind the canonical receipt body and declared key identity.

Key rotation must be logged as its own audit event before any new signing key is treated as active.

## What this does not prove

This artefact does not prove that:

- the system is production-ready,
- the chain is tamper-proof,
- every possible execution path is covered,
- the implementation satisfies any compliance regime,
- downstream systems cannot mutate by another route.

It only defines a small, inspectable receipt-chain pattern for refused actions.

## Clean line

Do not call it hardened.
Make it harder to fool.
