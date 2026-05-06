# BUILD RECEIPTS

Status: ACTIVE  
Class: GOVERNANCE_RECEIPT_LEDGER  
Scope: commit-gate-core governance build sequence

This ledger records structural commits and the claim boundary attached to each step.

---

## Receipt ledger

| Commit | Layer | File / Surface | Held receipt |
| --- | --- | --- | --- |
| `68f2d266` | Claim boundary | `docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md` | Claim discipline co-located with the code. |
| `d96b7fc0` | Entry surface | `README.md` | README links to the claim register. |
| `8a3c39ba` | Invariants | `docs/governance/INVARIANTS.md` | Three machine-testable invariants formalised. |
| `901cef71` | Adversarial vectors | `tests/adversarial/INVARIANT_TEST_VECTORS_v1.json` | Failure shapes declared as proof obligations. |
| `2192cd77` | Executable proof obligations | `tests/adversarial/test_invariants.py` | Adversarial vectors bound to executable tests. |
| `ea6f58a6` | CI configuration | `.github/workflows/adversarial-invariants.yml` | CI workflow committed for push and pull request triggers. |
| `5bd99556` | Trigger receipt | `docs/governance/CI_TRIGGER_RECEIPT.md` | Post-workflow push recorded; CI success not proven. |
| `f56d9588` | Local verifier | `scripts/verify_adversarial_invariants.py` | Local adversarial invariant verification command added. |
| `a624c970` | Entry discoverability | `README.md` | Local adversarial verifier command exposed from README. |
| `dc4162c` | Change control | `docs/governance/CHANGE_CONTROL.md` | Receipt-update triggers and claim-boundary review triggers defined. |
| `e13a2eee` | Governance index | `docs/governance/README.md` | Governance folder made navigable as a controlled surface. |
| `3e3c7f43` | Governance map | `docs/governance/GOVERNANCE_MAP.md` | Governance loop mapped as a single-page control surface. |
| `90cccbcd` | Durable verification receipts | `scripts/verify_adversarial_invariants.py` | Local verifier can emit machine-readable JSON verification receipts. |
| `ebb59f64` | Receipt scope note | `docs/governance/VERIFICATION_RECEIPT_SCOPE.md` | Verification receipt proof limits formalised as a governance boundary. |
| `68ac94c3` | Receipt-scope governance pinning | `docs/governance/CHANGE_CONTROL.md` | Receipt scope changes now trigger receipt updates and claim-boundary review. |
| `5a2a8ca4` | Governance index update | `docs/governance/README.md` | Verification receipt scope note added to governance routing surface. |
| `fa0e7e76` | Governance changelog | `docs/governance/CHANGELOG.md` | Receipt-scope trigger class documented as a governance event. |
| `e84f7e9f` | Changelog trigger-class rule | `docs/governance/CHANGELOG.md` | Governance changelog entries must now declare the trigger class that fired. |
| `941a1521` | Governance class taxonomy | `docs/governance/GOVERNANCE_CLASSES.md` | Permitted governance trigger classes formally defined. |
| `20223ea9` | Governance index taxonomy route | `docs/governance/README.md` | Governance class taxonomy exposed from the governance routing surface. |
| `78e6a948` | Governance ontology amendment rule | `docs/governance/CHANGE_CONTROL.md` | Governance class ontology amendments must use the existing Mechanism change class. |
| `98f07f80` | Ontology self-amendment boundary | `docs/governance/GOVERNANCE_CLASSES.md` | Governance class ontology cannot define a class for its own amendment. |
| `de92d803` | Governance violation index note | `docs/governance/README.md` | Governance class amendments without a Mechanism change trigger are explicitly marked as violations. |
| `18205739` | Open claims register | `docs/governance/OPEN_CLAIMS.md` | Explicitly unheld governance claims now tracked as a first-class surface. |
| `7eddccc7` | Open claims routing | `docs/governance/README.md` | Open claims register exposed from the governance routing surface. |
| `b9d9734e` | Open claims violation warning | `docs/governance/README.md` | Closing an open claim without a BUILD_RECEIPTS entry is explicitly classified as a governance violation. |
| `c7764e8f` | Claim lifecycle state machine | `docs/governance/GOVERNANCE_CLASSES.md` | Claim lifecycle formally classified as open, correctly closed, or governance violation. |
| `c84dfb35` | Claim closure procedure | `docs/governance/CLAIM_CLOSURE_PROCEDURE.md` | Ordered constitutional procedure for closing governance claims formalised. |
| `d8ce5cfc` | Claim closure routing | `docs/governance/README.md` | Claim closure procedure exposed from governance routing surface. |
| `54236eae` | Governance violation intake | `.github/ISSUE_TEMPLATE/governance_violation.md` | Structured constitutional intake surface for suspected governance violations formalised. |
| `5457fb60` | Intake template governance controls | `docs/governance/CHANGE_CONTROL.md` | Governance violation intake amendments now require Mechanism change classification and receipt tracking. |
| `1b0a0d62` | Governance violation review | `docs/governance/GOVERNANCE_VIOLATION_REVIEW.md` | Ordered constitutional review and classification procedure for governance violations formalised. |
| `c2d5937c` | Review procedure routing | `docs/governance/README.md` | Governance violation review procedure exposed from governance routing surface. |
| `3a88ac71` | Review procedure governance controls | `docs/governance/CHANGE_CONTROL.md` | Governance violation review amendments now require Mechanism change classification and receipt tracking. |
| `a72dd1e8` | Governance review outcomes | `docs/governance/GOVERNANCE_REVIEW_OUTCOMES.md` | Permitted constitutional outcome states for governed review resolution formalised. |
| `a1e9dc4d` | Review outcomes routing | `docs/governance/README.md` | Governance review outcomes exposed from governance routing surface. |
| `7392f06b` | Review outcome governance controls | `docs/governance/CHANGE_CONTROL.md` | Governance review outcome amendments now require Mechanism change classification and receipt tracking. |
| `fe2e7117` | Review resolution template | `docs/governance/GOVERNANCE_REVIEW_RESOLUTION_TEMPLATE.md` | Minimum constitutional closure record for governed reviews formalised. |
| `d8e5bfb7` | Review resolution routing | `docs/governance/README.md` | Governance review resolution template exposed from governance routing surface. |
| `2b392257` | Review records register | `docs/governance/REVIEW_RECORDS.md` | Durable register for governed review outcomes formalised. |
| `9b0baf92` | Open claims closure checklist | `docs/governance/OPEN_CLAIMS_CLOSURE_CHECKLIST.md` | Pre-flight checklist for governed claim closure formalised. |
| `b4bb2127` | CI green proof requirements | `docs/governance/CI_GREEN_PROOF_REQUIREMENTS.md` | Explicit closure requirements for CI_GREEN_PROOF formalised without closing the claim. |
| `292a07de` | Governance routing expansion | `docs/governance/README.md` | Remaining governance surfaces exposed from governance routing surface. |
| `00585e1b` | Final governance controls | `docs/governance/CHANGE_CONTROL.md` | Remaining governance surfaces now pinned as operative governance surfaces. |

---

## Current held claim

The repo exposes both the execution demo and the adversarial verification path from its primary entry surface.

`CHANGE_CONTROL.md` defines when future claim, invariant, proof-surface, CI, or PR-template changes require a receipt update.

`docs/governance/README.md` routes readers through the governance control surface.

`GOVERNANCE_MAP.md` maps the governance loop without widening the claim surface.

Local adversarial vector evaluation can now produce durable machine-readable receipts.

Verification receipt proof limits are now themselves governed by change-control triggers.

Receipt-scope trigger rules are now documented in the governance changelog.

Governance changelog entries must now declare the trigger class that fired.

Governance trigger classes are now formally defined and pinned.

Governance class ontology amendments must use the existing Mechanism change class.

Governance class ontology cannot define a class for its own amendment.

Governance class amendments without a Mechanism change trigger are explicitly classified as violations.

Explicitly unheld governance claims are now tracked as a first-class governance surface.

Closing an open claim without a BUILD_RECEIPTS entry is explicitly classified as a governance violation.

Claim lifecycle state transitions are now formally classified.

Claim closure procedure is now formally defined as an ordered constitutional transition.

Structured intake for suspected governance violations now exists.

Governance violation intake amendments are now controlled as operative governance surfaces.

Structured governance violation review and resolution procedure now exists.

Governance violation review amendments are now controlled as operative governance surfaces.

Governed review outcome states are now formally defined.

Governance review outcome amendments are now controlled as operative governance surfaces.

Governed review closure records are now formally standardised.

Governed review records now have a durable append-only register.

Governed claim closure now has a formal pre-flight checklist.

CI_GREEN_PROOF now has explicit closure requirements without closing the claim.

## Current unheld claim

CI green proof is not yet evidenced through the connector.

Do not claim verified enforcement on every push until a successful workflow run is observed.

Do not use local verification receipts as evidence of production runtime enforcement or CI success.

---

## Standing boundary

This ledger records verified state only.

No claim is held until it is evidenced.
