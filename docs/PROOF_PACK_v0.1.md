# Proof Pack v0.1 — historical mutation-facing artefact

**Status: SUPERSEDED / RETAINED FOR LINEAGE / NOT CURRENT RELEASE EVIDENCE**

This proof pack was created for the pre-Shape A executor. Its stored fixtures
and receipts describe a synthetic verifier, a mutation callback, and an ALLOW
path that applied in-process state. Those are not behaviours of the current
authorize-only kernel.

The historical fixtures use `signature == "sig_valid"`. That value is not a
signature, not the current HMAC-SHA256 lab MAC, and not evidence that Ed25519 is
implemented. The stored receipts are retained unchanged as historical objects;
they must not be quoted as current package results.

## Runner status

`scripts/run_proof_pack.py` is deliberately retired and exits without invoking
the gate or writing receipts. It remains only to fail closed for old commands
that still point at the v0.1 proof pack.

`scripts/verify_receipt.py` can still inspect the integrity of the historical
receipt files. Receipt integrity does not promote their retired execution model
into a current capability claim.

## Current inspection path

The authorize-only kernel introduced by PR #31 is bound to merge commit:

`c0fbc5fb425291a48bc2aed590dfbb66f0c77785`

At that commit, run:

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

Those regressions inspect authorisation without application, payload hashing
inside the gate, hash-only refusal, and audit-failure handling with the
in-memory test ledger.

## Current claim boundary

The current kernel may return `AUTHORIZED`; it does not apply the payload.
HMAC-SHA256 is a lab MAC. Ed25519 is specified but not implemented. This object
does not establish production readiness, certification, compliance, durable
replay protection, atomic world commit, external non-bypassability, or
path-universal governance.
