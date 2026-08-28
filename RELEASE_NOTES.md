# commit-gate-core v0.2.0a1

Authorize-only Shape A prerelease.

## Included

- `authorize(record, payload_bytes, ...)` hashes the supplied payload inside
  the gate and returns an authorisation result without applying the payload
- the deprecated `execute(...)` wrapper delegates to `authorize(...)`; no
  application hook runs
- a caller-supplied `commit_hash` without `payload_bytes` is refused with
  `DENY:COMMIT_HASH_ONLY_FORBIDDEN`
- scope, time window, accepted policy version, configured verifier, payload
  binding, nonce use, and audit append are checked before `AUTHORIZED`
- the demonstrated authenticator is an HMAC-SHA256 lab MAC; it is not a
  signature and is not presented as production key management
- canonical bytes and PureEdDSA Ed25519 are specified for a later extra;
  Ed25519 is not implemented in this version
- two-phase application remains under `experimental/` and is not installed or
  exported by the package

## Install

After the `v0.2.0a1` tag exists:

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.2.0a1"
```

## Verify

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

The complete collected suite is:

```bash
python -m pytest tests enterprise-execution-readiness/tests
```

## Claim boundary

This prerelease demonstrates a bounded, in-process authorisation kernel. It
does not apply payloads and does not establish production readiness,
enterprise deployment, compliance, certification, durable replay protection,
atomic world commit, external non-bypassability, or path-universal governance.
