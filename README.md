# Commit Gate Core

**PR #31 (`feat/authorize-only`) is open and unmerged. Version `0.2.0a1` is
unreleased.** Default branch `main` is still `v0.1.1`. This README describes
the authorize-only kernel on that PR, not the published tag.

Research map: https://lalaskye.github.io/inspection-surface/

Canonical message format: [`docs/governance/CANONICAL_BYTES_AND_ED25519_V1.md`](docs/governance/CANONICAL_BYTES_AND_ED25519_V1.md)

## 1. What the authorize-only kernel is

A small Python gate that **authorises** a DecisionRecord against a payload.
It hashes the caller-supplied `payload_bytes` inside the gate, checks scope,
time window, policy version, and nonce, then returns `AUTHORIZED` or a
deny/error code.

It checks the configured verifier. The demonstrated tests use an HMAC-SHA256
lab MAC.

It does not apply the payload. `mutation_callback` is never invoked.
`execute` is a deprecated wrapper: it requires `payload_bytes` and only
calls `authorize`. A `commit_hash` with no payload is refused
(`DENY:COMMIT_HASH_ONLY_FORBIDDEN`).

Ed25519 is specified for a later extra. It is not implemented in this tree.

## 2. What it refuses

On the demonstrated path the gate refuses when:

- there is no record
- required fields are missing or empty
- verdict is not `ALLOW`
- policy version is not accepted
- the configured verifier does not accept the record
- the record is not yet valid or has expired
- actor, action, object, environment, or payload hash do not match
- the nonce was already consumed
- `payload_bytes` is omitted
- only a caller-supplied `commit_hash` is offered
- the authorised audit event cannot be written; authorisation is refused and
  nonce rollback is attempted. Rollback failure has a separate error code.

Two-phase apply lives under `experimental/` and is not a public export.

## 3. One local command

From a clone of `feat/authorize-only`:

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

Expected: those files pass. They prove authorise-without-mutate, hash-only
refusal, payload binding inside `authorize`, and audit-failure rollback with
the in-memory test ledger.

Do not use `pip install …@v0.1.1` as evidence of this kernel.

## 4. What it does not claim

This object does not claim production readiness, enterprise deployment,
compliance, certification, path-universal enforcement, crash-safe durable
nonces, atomic PREPARED+nonce persistence, or that consequence cannot occur
outside this process.

It does not claim that Ed25519 is implemented.
It does not claim certificates or algorithm agility.
It does not claim that the lab MAC is a signature.
It does not claim that `start-here` is this kernel.

Working paper (broader than this package):
https://doi.org/10.5281/zenodo.19980275

## License

MIT.
