# Threat Model

## Scope

This threat model covers the commit gate boundary only. It does not cover upstream orchestration, key management infrastructure, or network transport.

---

## Threat classes

### T1 — No record presented
An agent attempts a state mutation with no `DecisionRecord`.

**Gate response:** `DENY` immediately. No record = no authority.

---

### T2 — Invalid signature
A `DecisionRecord` is presented with a signature that does not verify against the authorised key.

**Gate response:** `DENY`. Structural failure — evaluation stops.

---

### T3 — Replay attack
A valid, previously used `DecisionRecord` is re-submitted to authorise a second mutation.

**Gate response:** `DENY`. Nonce already present in ledger.

---

### T4 — Scope mismatch
A `DecisionRecord` authorises commit `A` but is presented at commit `B`.

**Gate response:** `DENY`. Scope binding is exact — no generalisation permitted.

---

### T5 — Parameter tampering
The commit payload is modified after the `DecisionRecord` was signed.

**Gate response:** `DENY`. Signature verification fails against altered params.

---

### T6 — Expired record
A `DecisionRecord` is presented after its execution window has closed.

**Gate response:** `DENY`. Timestamp out of permitted range.

---

## Non-threats (out of scope)

- Key compromise — handled by infrastructure layer, not gate
- Denial of service against the gate process itself
- Social engineering of the human authority

## Residual risk

All gate decisions are written to the audit trail regardless of outcome. Denial events are logged with reason code.
