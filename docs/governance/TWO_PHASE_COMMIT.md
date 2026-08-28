> **Warning:** This document describes a retired/experimental executor and not the public authorize-only kernel. Two-phase code is not a package export.

# Two-phase commit (v0.2 draft)

v1 `CommitGate.execute` could mutate the world and then return `allowed=False`
if the audit sink failed. That return value is a lie. The public kernel no
longer invokes `mutation_callback`.

The experimental split was:

1. `prepare` writes `GATE_PREPARED`, then spends the nonce. No mutation.
2. `apply` mutates, then writes `GATE_COMMITTED`.

If step 1 cannot write the receipt, the nonce stays free.
If step 2 mutates and cannot write `COMMITTED`, the result is
`phase=UNRECEIPTED`, `allowed=False`, `world_changed=True`.
Callers must treat that code as "do not retry the mutation; reconcile the receipt."

`HmacSha256Verifier` authenticates `canonical_bytes(record)`. It is a lab MAC,
not an asymmetric signature.
