# GOVERNANCE CLASSES

Status: ACTIVE  
Class: CONTROLLED_TAXONOMY  
Scope: governance changelog trigger classes

This file defines the permitted governance classes for changelog trigger declarations.

No new class may be introduced without a `CHANGE_CONTROL.md` trigger and a `BUILD_RECEIPTS.md` entry.

---

## Mechanism change

A change to how enforcement, evaluation, verification, or receipt generation operates.

Examples:
- verifier behaviour changes
- adversarial vector evaluator changes
- CI enforcement scope changes
- receipt generation behaviour changes

---

## Claim-boundary change

A change to what the repository, primitive, verifier, receipt, or governance surface is allowed to assert.

Examples:
- safe-claim wording changes
- forbidden-claim wording changes
- configured surface promoted to evidenced surface
- claim limit widened, narrowed, or restated

---

## Receipt-semantics change

A change to what an evidence artefact is allowed to mean.

Examples:
- local receipt scope changes
- receipt proof limits change
- receipt admissibility changes
- receipt interpreted as evidence for a new surface

---

## Enforcement-scope change

A change to where enforcement applies or is claimed to apply.

Examples:
- path-local claim promoted to broader coverage
- CI trigger scope changes
- runtime/deployment coverage changes
- path-universal enforcement claim introduced or removed

---

## Standing boundary

These classes classify governance authority movement.

They do not, by themselves, upgrade any claim.

CI green proof remains unheld until evidenced.
