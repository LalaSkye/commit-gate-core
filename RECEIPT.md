# Repository Receipt

Date: 2026-05-11
Repository: `LalaSkye/commit-gate-core`
Evidence class: path-local demonstration / bounded artefact / working paper support surface

## Object

`commit-gate-core` is a reference kernel for execution-boundary governance.

It demonstrates a path-local commit gate where a consequence-producing action must present a valid signed, scoped, unexpired, unreplayed `DecisionRecord` before mutation is allowed.

## What this repository does

- Enforces a fail-closed check at a demonstrated commit boundary.
- Blocks execution when authority, scope, expiry, replay, or admissibility checks fail.
- Emits refusal / denial evidence for blocked paths where the audit sink accepts the event.
- Provides a runnable inspection surface for the demonstrated path.
- Supports the working paper: *From Policy to Commit: Execution-Boundary Control for Governed AI Systems*.

## What this repository does not do

This repository does not claim:

- adoption
- certification
- compliance
- endorsement
- production readiness
- field validation
- standardisation
- path-universal coverage
- tamper-proof audit evidence
- that all possible downstream or side-channel routes are controlled

## Proof surface

Useful inspection questions:

1. Was an action attempted?
2. Was a valid `DecisionRecord` present?
3. Was the action within authorised scope?
4. Was the authority fresh and unreplayed?
5. Was the state transition permitted before mutation?
6. Was a refusal receipt produced when the action was blocked?

## Related evidence

- README: `README.md`
- Claim register: `docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md`
- Refusal receipt note: `docs/refusal-receipt-v0.1.md`
- Working paper DOI: https://doi.org/10.5281/zenodo.19980275

## Claim boundary

Allowed claim:

> This repository demonstrates a bounded, path-local execution-control surface that can refuse a consequence-producing action before mutation when required authority conditions are not met.

Not allowed:

> This repository proves adoption, compliance, certification, production readiness, or universal runtime governance coverage.

## Receipt line

No receipt, no proof. No scope, no build. No overclaim, no wobble.
