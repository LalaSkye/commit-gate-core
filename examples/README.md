# Examples

This folder contains small runnable demonstrations for inspecting execution-boundary behaviour.

## Runtime Refusal Demo v0.3

Run:

```bash
python examples/runtime_refusal_demo_v0_3.py
```

Runtime Refusal Demo v0.3 is a minimal, in-memory path-local demonstration.

It shows that on one controlled path:

- a mutation is attempted
- the gate refuses execution because authority is missing
- the execution layer records `mutation_committed=false`
- before/after tracked state hashes are compared
- a v0.2 Runtime Refusal Receipt is generated
- the receipt hash is checked

Expected output shape:

```text
Runtime Refusal Demo v0.3: PASS
Gate verdict: REFUSE
Mutation committed: false
State unchanged: true
Receipt hash valid: true
Downstream status: VERIFIED_NOT_COMMITTED
```

## Claim boundary

This is a path-local synthetic demonstration.

It proves only that, on this controlled in-memory path, the refused mutation did not change the tracked state and a refusal receipt was generated.

It does not prove production enforcement, external tool control, persistence-layer enforcement, concurrency safety, compliance, adoption, or path-universal coverage.
