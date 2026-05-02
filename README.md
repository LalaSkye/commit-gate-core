# Commit Gate Core
New to this work? Start here:
[https://github.com/LalaSkye/start-here](https://github.com/LalaSkye/start-here)

**Reference kernel for execution-boundary governance.**

Commit Gate Core stops unauthorised consequences before execution.

Most governance systems review decisions after consequences happen.  
This repo demonstrates a smaller, harder control surface:

> **No state mutation is allowed unless a signed, scoped, unexpired, unreplayed `DecisionRecord` authorises the exact commit.**

If authority, scope, expiry, replay, or receipt checks fail, the action does not run.

It holds.

---

## Execution Boundary Test v1

Use the test to check whether a system can physically stop consequence at the point an action would become real.

See: [`docs/execution-boundary-test-v1.md`](docs/execution-boundary-test-v1.md)

Core question:

> Where does the system physically stop?

PASS:
The action cannot execute without valid proof.

FAIL:
The action still reaches consequence.

---

## Try it in 30 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

Expected output:

```text
Result: HOLD
Email sent: false
Receipt written: true
```

If the email sends, the gate is broken.

---

## The demo

```text
Attempt:        send external email
DecisionRecord: missing authority
Result:         HOLD
Email sent:     false
Receipt written: true
```

That is the shape.

The system refuses the unsafe state change before execution and writes a receipt proving why.

---

## What this repo proves

- Unsafe consequence can be refused before execution.
- Missing authority prevents mutation.
- Refusal can produce an auditable receipt.
- Bypass failure can be tested directly.

This is not governance commentary.

It is a small enforcement primitive.

---

## Boundary

This repo does **not** claim to be a full AI governance system.

It proves one narrow invariant:

> This path cannot execute without a valid `DecisionRecord`.

The invariant is deliberately small so it can be inspected, tested, and broken under hostile reading.

---

## Core rule

A valid `DecisionRecord` must be:

- signed
- scoped to the exact commit
- within its validity window
- unreplayed
- sufficient for the requested mutation

Failure at any check produces `HOLD`.

No silent continuation.

---

## Evidence shape

A useful governance gate must show:

1. what action was attempted
2. what proof was required
3. which check failed
4. whether execution occurred
5. what receipt was written

For this demo, the answer is simple:

```text
Execution occurred: false
Receipt written:    true
Verdict:            HOLD
```

---

## Status

`v0.1` — one invariant, hard-enforced.

Small surface. Clear failure mode. Receipts over reassurance.

---

## License

MIT. Use it. Break it. Tell me how.
