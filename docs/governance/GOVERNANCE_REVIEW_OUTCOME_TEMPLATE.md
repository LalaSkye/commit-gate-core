# GOVERNANCE REVIEW OUTCOME TEMPLATE

Status: ACTIVE  
Trigger class: Mechanism change  
Governed by: `CHANGE_CONTROL.md`

---

## Purpose

This template standardises the record produced when a governance violation review is resolved.

It does not replace `GOVERNANCE_VIOLATION_REVIEW.md`.

It records the outcome of that procedure.

---

## Outcome record

```markdown
# Governance Review Outcome

Issue: <issue number or link>  
Outcome: <CONFIRMED | UNFOUNDED | INCOMPLETE | DUPLICATE | OUT_OF_SCOPE>  
Date: <YYYY-MM-DD>  
Reviewer: <name or handle>  
Trigger class: <class used for review routing>

## Finding

<short statement of what was found>

## Evidence considered

- <commit, diff, issue, receipt, or changelog reference>

## Rule or boundary assessed

<which governance rule, file, or boundary was assessed>

## Required record

<record required by GOVERNANCE_REVIEW_OUTCOMES.md>

## Resolution

<confirmed remediation, return-for-completion, duplicate reference, out-of-scope redirect, or unfounded closure reason>

## Receipt reference

<BUILD_RECEIPTS.md entry or commit reference>

## Boundary

This outcome classifies the governed review only.

It does not determine contributor intent, blame, personnel action, or access control.
```

---

## Forbidden omissions

A review outcome record must not omit:

- outcome state
- evidence considered
- rule or boundary assessed
- receipt reference
- standing boundary

---

## Standing boundary

Outcome records preserve review state.

They do not create enforcement authority outside the local governance surface.
