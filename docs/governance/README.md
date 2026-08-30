# Governance Surface

## Current inheritance boundary

The root `README.md`, `CLAIM_BOUNDARY.md`, `RECEIPT.md`,
`docs/invariant.md`, and `SHAPE_A_AUTHORIZE.md` describe the current
authorize-only object. Older governance files are preserved records and may
contain architecture proposals or release-era language. They do not inherit
standing into `0.2.0a1` unless the current claim boundary explicitly admits
them.

This folder contains the governance control surface for `commit-gate-core`.

Each file has one job.

| File | Governs |
| --- | --- |
| `ADMISSIBLE_CLAIM_REGISTER_v1.md` | Superseded positioning record; not current claim authority. |
| `INVARIANTS.md` | Wider architecture candidates; not established by this kernel. |
| `BUILD_RECEIPTS.md` | What has changed and what claim boundary is held. |
| `CHANGE_CONTROL.md` | When a change requires a receipt or claim-boundary review. |
| `GOVERNANCE_CLASSES.md` | Which governance trigger classes are permitted. Changes without a Mechanism change trigger are governance violations. |
| `OPEN_CLAIMS.md` | Which governance claims are explicitly unheld. Closing a claim without a BUILD_RECEIPTS entry is a governance violation. |
| `OPEN_CLAIMS_CLOSURE_CHECKLIST.md` | Pre-flight checklist for moving a claim from UNHELD to CLOSED. |
| `CLAIM_CLOSURE_PROCEDURE.md` | The exact ordered procedure required to move a claim from UNHELD to CLOSED. |
| `REVIEW_RECORDS.md` | The durable register of completed governed review outcomes. |
| `GOVERNANCE_VIOLATION_REVIEW.md` | The staged procedure for reviewing, classifying, and resolving suspected governance violations. |
| `GOVERNANCE_REVIEW_OUTCOMES.md` | The permitted outcome states for governed review resolution. |
| `GOVERNANCE_REVIEW_RESOLUTION_TEMPLATE.md` | The minimum constitutional record required to close a governed review. |
| `CI_GREEN_PROOF_REQUIREMENTS.md` | Evidence required to close the CI_GREEN_PROOF open claim. |
| `VERIFICATION_RECEIPT_SCOPE.md` | What local verification receipts are allowed to prove. |
| `CI_TRIGGER_RECEIPT.md` | Why the first CI trigger commit exists and what it does not prove. |

---

## Standing boundary

Local verification is present and discoverable.

CI enforcement is configured but not yet evidenced green.

No claim is upgraded without evidence.
