# Changelog

This changelog records human-readable evidence changes for `LalaSkye/commit-gate-core`.

Git history remains the source of commit-level truth. This file provides a court-readable / buyer-readable summary layer.

## 2026-08-05

- Added `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `Makefile` to give the repository an explicit, inspectable install path.
- Added an `Install` section to `README.md` covering editable install, test-dependency install, Makefile targets, and the import path.
- Added a stable public import surface, explicit MIT licence, and bundled synthetic scenario fixture.
- Added CI that builds and installs the wheel, then checks it outside the repository checkout.
- Added a tag-triggered workflow that publishes wheel and source archives as a GitHub release.
- Recorded the corrected root-suite result: 42 passed, 0 failed after PR #25 fixed test data without changing the gate and this patch added two package checks.

Evidence effect:

- The repository can now be installed from a tagged version or a local clone.
- The built wheel contains the public package and the bundled ESP-001 fixture.
- The current root-suite and package-check boundaries are disclosed.

Claim boundary:

- This records packaging and disclosure only.
- It does not claim new gate capability, adoption, validation, compliance, or production readiness.
- The separate `enterprise-execution-readiness/tests/` collection issue remains outside this package release check.

## 2026-05-11

- Added `RECEIPT.md` to state the repository object, evidence class, proof surface, and claim boundary.
- Added `CLAIM_BOUNDARY.md` to separate allowed mechanism claims from forbidden adoption / compliance / production claims.
- Established quiet evidence-custody pattern for future repo hardening.

Evidence effect:

- Improves inspectability.
- Makes claim limits explicit.
- Keeps the repository focused on bounded, path-local demonstration rather than inflated field claims.

Claim boundary:

- This records documentation hardening only.
- It does not claim new technical capability, adoption, validation, compliance, or production readiness.
