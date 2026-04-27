# Pre-Registered Failures

These are the expected, intentional failure modes of `commit-gate-core`. Each maps to an adversarial test.

---

## F1 — No record → blocks

**Test:** `test_no_record_blocks.py`  
**Input:** Commit attempt with no `DecisionRecord`  
**Expected gate output:** `DENY`  
**Reason:** No authority presented

---

## F2 — Invalid signature → blocks

**Test:** `test_invalid_signature_blocks.py`  
**Input:** `DecisionRecord` with bad signature  
**Expected gate output:** `DENY`  
**Reason:** Structural integrity failure

---

## F3 — Replay → blocks

**Test:** `test_replay_blocks.py`  
**Input:** Previously used nonce re-submitted  
**Expected gate output:** `DENY`  
**Reason:** Nonce already consumed

---

## F4 — Scope mismatch → blocks

**Test:** `test_scope_mismatch_blocks.py`  
**Input:** `DecisionRecord` scoped to different commit hash  
**Expected gate output:** `DENY`  
**Reason:** Binding is exact — wrong target

---

## F5 — Parameter tampering → blocks

**Test:** `test_params_tamper_blocks.py`  
**Input:** Signed record, but commit params altered post-signing  
**Expected gate output:** `DENY`  
**Reason:** Signature no longer verifies

---

## Failure evaluation rule

All failures are `FIRST_FAIL`. The gate does not continue evaluating after the first violation. Reason codes are written to audit on every `DENY`.
