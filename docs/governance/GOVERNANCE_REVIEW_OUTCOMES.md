# GOVERNANCE REVIEW OUTCOMES

Status: ACTIVE  
Trigger class: Mechanism change  
Governed by: `CHANGE_CONTROL.md`

---

## Purpose

This file defines permitted outcome states for governance violation reviews.

A review outcome records what the review concluded.

It does not determine contributor intent, blame, personnel action, or access control.

---

## Permitted outcomes

| Outcome | Meaning | Required record |
| --- | --- | --- |
| `CONFIRMED` | A governed rule was breached. | Rule breached, evidence, remediation path, receipt reference. |
| `UNFOUNDED` | No governed violation was found. | Reason, evidence considered, receipt reference. |
| `INCOMPLETE` | The report lacks required intake information. | Missing fields, return-for-completion note. |
| `DUPLICATE` | The report duplicates an existing governed review. | Existing review reference. |
| `OUT_OF_SCOPE` | The report concerns a matter outside the local governance surface. | Scope reason and redirect if applicable. |

---

## Forbidden outcomes

- informal closure
- closed by consensus
- closed without classification
- closed without record
- deleted after review

---

## Standing boundary

Outcome classification is not punishment.

It is the final routing state of a governed review.
