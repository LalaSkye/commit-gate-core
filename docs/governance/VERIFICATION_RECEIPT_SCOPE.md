# VERIFICATION RECEIPT SCOPE

Status: ACTIVE  
Class: CLAIM_BOUNDARY_NOTE  
Scope: `scripts/verify_adversarial_invariants.py --receipt`

---

## What the receipt proves

A JSON verification receipt proves that the local verifier evaluated the declared adversarial vectors and recorded the observed outcomes at receipt-generation time.

---

## What the receipt does not prove

A JSON verification receipt does not prove:

- production runtime enforcement
- CI success
- deployment coverage
- path-universal enforcement
- that every consequence path is gated

---

## Safe claim

Local adversarial vector evaluation produced a durable receipt.

---

## Forbidden claim

Do not use a local verification receipt as evidence of production runtime enforcement or CI green proof.
