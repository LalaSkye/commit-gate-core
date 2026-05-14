# Roadmap v0.2 — Proof Pack adversarial inspection targets

This document records the inspection result for Proof Pack v0.1 and the
candidate next proof-surface targets for v0.2. It is a custody artefact,
not a marketing document.

## 1. Current v0.1 boundary

Proof Pack v0.1 is bounded to:

- a path-local Python harness driving the existing CommitGate kernel
- a synthetic signature verifier (accepts records where
  `signature == "sig_valid"`)
- an in-memory nonce ledger
- a fixed clock pinned to `2026-04-27T05:01:00Z`
- a single mutation callback
- reproducible JSON fixtures and content-addressed receipts

## 2. What v0.1 proves

On the demonstrated path, with the harness above:

- a DENY decision prevents the `mutation_callback` from executing
- receipts record both ALLOW and DENY outcomes
- each DENY receipt emits a `no_execution_marker`
- the four fixture cases and their receipts are byte-for-byte replayable

## 3. What v0.1 does not prove

v0.1 does not prove:

- real cryptographic signature verification (the verifier is synthetic)
- persistent nonce custody across process restarts
- cross-process replay resistance
- concurrent safety under simultaneous `execute()` calls
- distributed side-effect control beyond the in-process callback
- production readiness

## 4. v0.2 candidate targets

The following are candidate proof surfaces, each scoped to remain
inspectable without expanding the public claim:

- Ed25519 or ECDSA signature verification against a fixed public key,
  with a malformed-signature fixture
- a persistent nonce ledger (file- or sqlite-backed) with a restart-
  replay fixture
- a cross-process replay test that consumes a nonce in one process and
  asserts refusal in a second
- a concurrent `execute()` test under a shared nonce ledger, asserting
  that at most one mutation occurs per nonce
- malformed-JSON and parser-boundary fixtures (truncated input, wrong
  types, extra fields) with matching DENY receipts
- clock skew and expiry edge tests covering `issued_at` in the future,
  just-past-expiry, and timestamps without timezone information

## 5. Claim boundary

- This roadmap does not claim production infrastructure, certification,
  adoption, or universal runtime governance.
- It records the next bounded proof surfaces for authority-before-
  mutation inspection.
- v0.2 targets remain candidate work until implemented, tested, and
  reviewed.
