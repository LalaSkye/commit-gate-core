# CHANGE CONTROL

Short rule file for when claim or invariant changes require a receipt update.

This file governs **when** documentation must be updated alongside a code or claim change. It is intentionally short. The PR template enforces the checklist; this file defines the triggers.

---

## Triggers requiring a BUILD_RECEIPTS.md update

A receipt entry **must** be added to `docs/governance/BUILD_RECEIPTS.md` when a commit:

1. Adds, removes, or modifies an invariant in `INVARIANTS.md`
2. Adds, removes, or modifies an adversarial vector in `INVARIANT_TEST_VECTORS_v1.json`
3. Changes the behaviour of `scripts/verify_adversarial_invariants.py`
4. Adds, removes, or modifies a claim in `ADMISSIBLE_CLAIM_REGISTER_v1.md`
5. Changes the CI workflow in a way that affects enforcement scope
6. Changes the PR template in a way that affects contributor obligations
7. Adds, removes, or modifies a receipt scope boundary in `VERIFICATION_RECEIPT_SCOPE.md`
8. Adds, removes, or modifies a governance trigger class in `GOVERNANCE_CLASSES.md`

---

## Triggers requiring a claim-boundary review

The standing claim boundary **must** be re-stated (not silently widened) when a commit:

1. Promotes a configured surface to an evidenced one (e.g. CI green proof)
2. Adds a new proof surface visible from README or entry
3. Removes or weakens an existing proof surface
4. Changes what a verification receipt is allowed to prove
5. Changes the permitted ontology of governance trigger classes

---

## Governance-class amendment rule

Any amendment to `GOVERNANCE_CLASSES.md` must be classified under the existing **Mechanism change** class.

The class ontology may not create an exception for its own amendment.

---

## Triggers NOT requiring a receipt update

To prevent ledger bloat, the following do **not** require a receipt entry:

- Typo fixes
- Formatting-only changes
- Internal comments and docstrings without behavioural change
- Dependency bumps that do not affect verifier output

---

## Receipt entry shape

Each receipt entry in `BUILD_RECEIPTS.md` should record:

- Commit SHA (short)
- File(s) affected
- Structural layer
- What is now held
- What is still not held
- Safe claim

---

## Standing rule

*No claim is upgraded without an evidenced trigger. No surface is widened without a receipt. The boundary is re-stated, never assumed.*
