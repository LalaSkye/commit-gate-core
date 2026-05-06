# GOVERNANCE CHANGELOG

Status: ACTIVE  
Class: GOVERNANCE_CHANGELOG  
Scope: governance-surface changes in `commit-gate-core`

---

## 2026-05-06 — Receipt-scope trigger class added

Commits:
- `68ac94c3` — `CHANGE_CONTROL.md`
- `5a2a8ca4` — `docs/governance/README.md`
- `70ba1e08` — `BUILD_RECEIPTS.md`

Change:
Receipt-scope changes are now a governed trigger class.

Effect:
A change that alters what a verification receipt is allowed to prove requires:

1. a `BUILD_RECEIPTS.md` update
2. a claim-boundary review
3. restatement of the standing boundary

Reason:
A local verification receipt must not be silently promoted into evidence of CI success, production runtime enforcement, deployment coverage, or path-universal enforcement.

Standing boundary:
Local adversarial vector evaluation can produce durable machine-readable receipts.

It does not prove production runtime enforcement or CI green proof.
