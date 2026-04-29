# Commit Gate Core

## Try in 30 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

**Expected output:**

```text
Result: HOLD
Email sent: false
Receipt written: true
```

The gate refused the unsafe action and logged a receipt.  
If the email actually sends, the gate is broken — file an issue.

---


Most governance systems review decisions after consequences happen.

Commit Gate Core stops unauthorised consequences before execution.

No state mutation is allowed unless a signed, scoped, unexpired, unreplayed DecisionRecord authorises the exact commit.

If authority, scope, expiry, replay, or receipt checks fail, the system does not continue.

It holds.

---

## Try in 30 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

Expected:

```
Result: HOLD
Email sent: false
Receipt written: true
```

The gate refused the unsafe state change and wrote a receipt proving why.

If the email sends, the gate is broken. File an issue.

---

## The killer demo

```
Attempt:        send external email
DecisionRecord: missing authority
Result:         HOLD
Email sent:     false
Receipt written: true
```

That is the shape. The system refuses the unsafe state change and writes a receipt proving why.

---

## Status

`v0.1` — one invariant, fully proven.

Not a full system. Not a roadmap. One rule, hard-enforced:

> This path cannot execute without a valid DecisionRecord.

---

## Run it in under 60 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

Expected output: `HOLD`. Email not sent. Receipt written to `./receipts/`.

If it executes the email, the gate is broken. File an issue.

---

## What this repo proves

- A system refusing unsafe state change.
- Receipts proving why.
- Tests proving bypass fails.

Not code. Not docs. Not demos. **Enforcement.**

---

## License

MIT. Use it. Break it. Tell me how.
