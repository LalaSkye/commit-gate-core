# Changelog

This changelog records human-readable evidence changes for `LalaSkye/commit-gate-core`.

Git history remains the source of commit-level truth. This file provides a court-readable / buyer-readable summary layer.

## 2026-08-31

### 0.2.0 — unreleased prepare (B1, no tag)

- Set package version and `__version__` to `0.2.0`.
- Pointed Package and Release workflow version asserts at `0.2.0`.
- Replaced `RELEASE_NOTES.md` with authorize-only v0.2.0 notes.
- Left GitHub Latest at `v0.1.1`. No tag in this change.
- Did not edit `release-v0.1.1.yml` or `bootstrap-v0.1.0.yml`.
- Did not edit the GitHub repository description.

Release boundary:

- `v0.1.1` remains the latest tagged release and contains the earlier
  mutation-callback object.
- `0.2.0` on this branch is unreleased prepare. Installing `v0.1.1` does not
  install this successor.

Claim boundary:

- This establishes version-pin alignment for a later B2 tag ticket.
- It does not establish that Latest is authorize-only.
- It does not establish production readiness, Ed25519, or external enforcement.

## 2026-08-28

### 0.2.0a1 — unreleased authorize-only successor on `main`

- Added `authorize(record, payload_bytes, ...)` as the promoted public path.
- Bound exact payload bytes by hashing them inside the authorisation call.
- Changed deprecated `execute` into an authorize-only wrapper.
- Stopped both public paths from invoking `mutation_callback`.
- Refused hash-only calls without the payload bytes.
- Kept the two-phase apply experiment outside the installable package and
  outside the public export surface.

Release boundary:

- `v0.1.1` remains the latest tagged release and contains the earlier
  mutation-callback object.
- `0.2.0a1` is unreleased. Installing `v0.1.1` does not install this successor.

Claim boundary:

- This establishes payload-bound authorisation on the tested in-process path.
- It does not establish payload application, downstream non-bypassability,
  durable persistence, Ed25519, production readiness or external enforcement.

## 2026-08-05

### v0.1.1 — complete-suite verification

- Widened bare `pytest` discovery to include both `tests/` and
  `enterprise-execution-readiness/tests/`.
- Verified the complete discovered suite on a fresh clone: 49 passed, 0 failed.
- Verified `pip install -e ".[dev]"` in a clean Python 3.12 environment.
- Verified the public package import and `make verify` path.
- Recorded all required CI checks green on `main` after the enterprise test
  loader fix.

Evidence effect:

- A bare `pytest` run now exercises all 49 tests rather than only the 42 root
  tests.
- The default local test command, package workflow, and tagged-release workflow
  now share the same complete discovery boundary.

Claim boundary:

- This is a test-discovery, verification, and patch-release change only.
- It does not add gate capability or establish production readiness,
  enterprise deployment, compliance, adoption, or independent validation.

### v0.1.0 — first packaged release

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
