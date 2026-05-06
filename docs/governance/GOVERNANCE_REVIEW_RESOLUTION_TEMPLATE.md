# GOVERNANCE REVIEW RESOLUTION TEMPLATE

Status: ACTIVE  
Trigger class: Mechanism change  
Governed by: `CHANGE_CONTROL.md`

---

## Purpose

This template defines the minimum record required to close a governed review.

It applies to all permitted outcomes in `GOVERNANCE_REVIEW_OUTCOMES.md`.

---

## Required resolution record

```markdown
## Governance review resolution

Outcome: CONFIRMED | UNFOUNDED | INCOMPLETE | DUPLICATE | OUT_OF_SCOPE

Issue or report reference:

Classification:

Evidence considered:

Rule or surface reviewed:

Resolution reason:

Required follow-up:

BUILD_RECEIPTS reference:

CHANGELOG reference, if applicable:

Boundary:
This outcome records governance classification only.
It does not determine contributor intent, blame, personnel action, or access control.
```

---

## Required fields

Every closure must include:

- outcome
- issue or report reference
- classification
- evidence considered
- rule or surface reviewed
- resolution reason
- receipt reference
- boundary statement

---

## Forbidden closures

- closure without outcome
- closure without evidence considered
- closure without receipt reference
- closure without boundary statement
- closure by comment consensus alone

---

## Standing boundary

A resolution record closes a governed review.

It does not erase the review.
