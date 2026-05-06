# BUILD RECEIPTS

Ledger of verified commits and claim boundaries for commit-gate-core.

---

## a624c970

**Change:** README now exposes the local adversarial verifier command.

**Held:**
- Local proof path is discoverable from README
- Adversarial verifier is present and runnable
- Claim discipline is exposed from entry
- CI workflow is committed

**Not held:**
- CI green proof
- Connector-visible workflow success
- Verified enforcement on every push

**Safe claim:**
The repo now exposes both the execution demo and the adversarial verification path from its primary entry surface.

---

## f56d9588

**Change:** `scripts/verify_adversarial_invariants.py` added — local executable verifier for adversarial proof obligations.

**Held:**
- Local verification path exists
- ADV-I / ADV-II / ADV-III evaluation present
- PASS / FAIL receipts printed to stdout
- Exits non-zero on invariant divergence

**Not held:**
- CI green proof
- Connector-visible workflow success

**Safe claim:**
Local verification path exists. CI enforcement remains configured but not yet evidenced green.

---

## Claim boundary (standing)

Local verification is present and discoverable.
CI enforcement remains configured but not yet evidenced green.

---

*This ledger records verified state only. No claim is held until it is evidenced.*
