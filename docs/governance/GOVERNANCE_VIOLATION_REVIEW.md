# GOVERNANCE VIOLATION REVIEW

Status: ACTIVE  
Trigger class: Mechanism change  
Governed by: `CHANGE_CONTROL.md`

---

## Purpose

This procedure defines how a filed governance violation report is reviewed, classified, and resolved.

Filing a report opens review.

This procedure determines what happens next.

---

## Stage 1 — Intake validation

Confirm the report is complete:

- violation type selected
- location specified: file, commit, or pull request
- observation stated specifically
- applicable rule identified
- evidence attached or referenced

Incomplete reports are returned for completion.

They are not dismissed.

---

## Stage 2 — Classification

Assign the report to exactly one classification:

| Finding | Classification |
| --- | --- |
| Mechanism altered without Mechanism change trigger | Mechanism change violation |
| Claim scope widened without Claim-boundary change trigger | Claim-boundary violation |
| Receipt claimed to prove more than declared scope | Receipt-scope violation |
| Ontology amended without governed procedure | Ontology violation |
| Open claim silently removed | Claim-closure violation |
| No governed violation found | Unfounded — close with record |

Classification is not punishment.

It is routing.

---

## Stage 3 — Resolution

Each classification routes to a resolution path.

### Violation confirmed

- state which rule was breached
- identify the specific commit or action
- determine remediation: revert, correction commit, or record
- produce a `BUILD_RECEIPTS.md` entry
- update `CHANGELOG.md` under the applicable trigger class
- close the issue with receipt reference

### Unfounded

- state why no violation was found
- produce a `BUILD_RECEIPTS.md` entry
- close the issue with record preserved

---

## Forbidden resolution actions

- closing without classification
- closing without a `BUILD_RECEIPTS.md` entry
- closing by social consensus alone
- retroactive reclassification without a new governed review
- deletion of the issue record

---

## What this procedure does not determine

- whether a contributor acted in bad faith
- personnel or access decisions
- anything outside the local governance surface

This procedure governs evidence and classification only.
