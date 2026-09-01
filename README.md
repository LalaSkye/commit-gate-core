# Commit Gate Core

`commit-gate-core` on this branch is **unreleased v0.2.0 prepare**: an
authorize-only kernel. It hashes caller-supplied `payload_bytes` inside the
gate and checks the bound DecisionRecord for verdict, scope, policy version,
time window, verifier result and nonce freshness. It returns authorisation or
refusal; it does not apply the payload or invoke `mutation_callback`.

GitHub **Latest** is still `v0.1.1`. That tag can invoke `mutation_callback`.
This tree is not Latest until a separate B2 ticket tags `v0.2.0` and
`/releases/latest` resolves to that tag.

## Release boundary

| Object | Status | Behaviour |
| --- | --- | --- |
| `v0.1.1` | Latest tagged release | Historical predecessor. `CommitGate.execute` can invoke a caller-supplied mutation callback. It is not the authorize-only kernel described below. |
| `main` / this branch / `0.2.0` | Unreleased prepare | Binds exact payload bytes and returns authorisation or refusal. It never applies the payload. Not Latest. |

The authorize-only successor entered `main` in merge commit
[`c0fbc5f`](https://github.com/LalaSkye/commit-gate-core/commit/c0fbc5fb425291a48bc2aed590dfbb66f0c77785).
GitHub's **Latest** badge therefore identifies the latest release, not the
function currently present on this tree.

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

From a clone of this tree:

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

Expected: those files pass. They prove authorise-without-mutate, hash-only
refusal, payload binding inside `authorize`, and audit-failure rollback with
the in-memory test ledger.

Do not install or cite `v0.1.1` as evidence of the authorize-only kernel.

Install-from-tag until B2:

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.1.1"
```

That command installs the historical Latest object, not this kernel.

## 4. What it does not claim

This object does not claim production readiness, enterprise deployment,
compliance, certification, path-universal enforcement, crash-safe durable
nonces, atomic PREPARED+nonce persistence, or that consequence cannot occur
outside this process.

It does not claim that Ed25519 is implemented.
It does not claim certificates or algorithm agility.
It does not claim that the lab MAC is a signature.
It does not claim that `start-here` is this kernel.
It does not claim that GitHub Latest is this tree.

Working paper (broader than this package):
https://doi.org/10.5281/zenodo.19980275

## License

MIT.
