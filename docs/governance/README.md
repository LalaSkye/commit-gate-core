# Governance Surface

This folder contains the governance control surface for `commit-gate-core`.

Each file has one job.

| File | Governs |
| --- | --- |
| `ADMISSIBLE_CLAIM_REGISTER_v1.md` | What may be claimed about the repo and its primitives. |
| `INVARIANTS.md` | What must remain true. |
| `BUILD_RECEIPTS.md` | What has changed and what claim boundary is held. |
| `CHANGE_CONTROL.md` | When a change requires a receipt or claim-boundary review. |
| `GOVERNANCE_CLASSES.md` | Which governance trigger classes are permitted. Changes without a Mechanism change trigger are governance violations. |
| `VERIFICATION_RECEIPT_SCOPE.md` | What local verification receipts are allowed to prove. |
| `CI_TRIGGER_RECEIPT.md` | Why the first CI trigger commit exists and what it does not prove. |

---

## Standing boundary

Local verification is present and discoverable.

CI enforcement is configured but not yet evidenced green.

No claim is upgraded without evidence.
