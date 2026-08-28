# Two-phase commit (v0.2 draft)

v1 `CommitGate.execute` can mutate the world and then return `allowed=False`
if the audit sink fails. That return value is a lie.

v0.2 splits the act:

1. `prepare` writes `GATE_PREPARED`, then spends the nonce. No mutation.
2. `apply` mutates, then writes `GATE_COMMITTED`.

If step 1 cannot write the receipt, the nonce stays free.
If step 2 mutates and cannot write `COMMITTED`, the result is
`phase=UNRECEIPTED`, `allowed=False`, `world_changed=True`.
Callers must treat that code as "do not retry the mutation; reconcile the receipt."

`HmacSha256Verifier` authenticates `canonical_bytes(record)`. It is a MAC,
not an asymmetric signature. Replace it without changing `TwoPhaseCommit`.
