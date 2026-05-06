---
name: Governance Violation Report
about: Report a suspected governance violation in commit-gate-core
title: "[VIOLATION] <brief description>"
labels: governance-violation
assignees: ''
---

## Suspected violation type

- [ ] Silent claim closure (open → removed without procedure)
- [ ] Ontology amendment without Mechanism change trigger
- [ ] Receipt-scope inflation (receipt claimed to prove more than declared)
- [ ] CI proof overclaim (CI green used as runtime enforcement proof)
- [ ] Claim-boundary drift (claim scope widened without Claim-boundary change trigger)
- [ ] Other (describe below)

## Location

<!-- File, commit, or PR where the suspected violation occurred. -->

## What you observed

<!-- Specific, externally verifiable description. Not "it felt wrong." -->

## What the procedure required

<!-- Which rule or file was not followed. -->

## Evidence attached

<!-- Commit hash, diff link, receipt reference, or changelog entry. -->

## What this is not

This report does not prove a violation occurred.

It opens a governed review.

The review determines classification.

---

_Filing this report is a constitutional act, not an accusation._

_Resolution requires the same evidence standard as claim closure._
