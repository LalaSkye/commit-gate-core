# Changelog

This changelog records human-readable evidence changes for `LalaSkye/commit-gate-core`.

Git history remains the source of commit-level truth. This file provides a court-readable / buyer-readable summary layer.

## 2026-08-05

- Added `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `Makefile` to give the repository an explicit, inspectable install path.
- Added an `Install` section to `README.md` covering editable install, test-dependency install, Makefile targets, and the import path.
- Added a dated `Known test status` section to `README.md` recording that the full suite currently reports 36 passed and 4 failed, all four in `tests/test_changed_condition_refusal.py`, all four a refusal-code naming mismatch (expected code vs emitted code) where the gate still refuses.
- No release tagged. Versioning deferred until the four recorded test failures are resolved.

Evidence effect:

- The repository can now be installed by a third party without reading the source layout first.
- The current test state is disclosed rather than implied.

Claim boundary:

- This records packaging and disclosure only.
- It does not claim new technical capability, a fully green test suite, adoption, validation, compliance, or production readiness.
- The four failing tests are recorded, not resolved.
- No version tag is claimed by this entry.

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
