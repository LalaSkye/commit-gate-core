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
9. Adds, removes, or modifies the governance violation intake template in `.github/ISSUE_TEMPLATE/governance_violation.md`
10. Adds, removes, or modifies `GOVERNANCE_VIOLATION_REVIEW.md`
11. Adds, removes, or modifies `GOVERNANCE_REVIEW_OUTCOMES.md`

---

## Triggers requiring a claim-boundary review

The standing claim boundary **must** be re-stated (not silently widened) when a commit:

1. Promotes a configured surface to an evidenced one (e.g. CI green proof)
2. Adds a new proof surface visible from README or entry
3. Removes or weakens an existing proof surface
4. Changes what a verification receipt is allowed to prove
5. Changes the permitted ontology of governance trigger classes
6. Changes governance violation intake framing or evidence requirements
7. Changes governance violation review classification or resolution framing
8. Changes what governance review outcomes are allowed to determine

---

## Governance-class amendment rule

Any amendment to `GOVERNANCE_CLASSES.md` must be classified under the existing **Mechanism change** class.

The class ontology may not create an exception for its own amendment.

---

## Governance violation intake template

File: `.github/ISSUE_TEMPLATE/governance_violation.md`  
Trigger class: Mechanism change

The following amendments require a Mechanism change trigger and a `BUILD_RECEIPTS.md` entry:

- Adding a violation type
- Removing a violation type
- Changing evidence requirements
- Changing review language
- Changing the intake framing, including accusation versus review

These are not editorial changes.

The selectable types and evidence standard are operative governance surfaces.

Amendment by editorial discretion is a governance violation.

---

## Governance violation review procedure

File: `docs/governance/GOVERNANCE_VIOLATION_REVIEW.md`  
Trigger class: Mechanism change

The following amendments require a Mechanism change trigger and a `BUILD_RECEIPTS.md` entry:

- Adding or removing review stages
- Changing classification table rows
- Changing resolution requirements
- Changing unfounded-review handling
- Changing the framing that classification is routing rather than punishment

These are not editorial changes.

The stage structure, classification mapping, and review framing are operative governance surfaces.

Amendment by editorial discretion is a governance violation.

---

## Governance review outcomes

File: `docs/governance/GOVERNANCE_REVIEW_OUTCOMES.md`  
Trigger class: Mechanism change

The following amendments require a Mechanism change trigger and a `BUILD_RECEIPTS.md` entry:

- Adding an outcome state
- Removing an outcome state
- Renaming an outcome state
- Changing required records for an outcome
- Changing forbidden outcomes
- Changing what outcome classification is allowed to determine

These are not editorial changes.

The permitted outcome states and outcome boundaries are operative governance surfaces.

Amendment by editorial discretion is a governance violation.

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
