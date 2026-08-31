# commit-gate-core v0.2.0

> **Unreleased prepare object on this branch.** These notes describe the
> authorize-only kernel. They must not be published until a separate B2
> ticket tags `v0.2.0` on the successor SHA. GitHub **Latest** remains
> `v0.1.1`, whose `execute()` path can invoke `mutation_callback`.

Authorize-only successor. The gate hashes caller-supplied `payload_bytes`
inside `authorize`, checks the bound DecisionRecord, and returns
authorisation or refusal. It does not apply the payload.
`mutation_callback` is never invoked. `execute` is a deprecated wrapper
that only calls `authorize` and requires `payload_bytes`.

## Included

- promoted public path: `authorize(record, payload_bytes, ...)`
- payload hash bound inside the gate; hash-only calls refused
- `execute` no longer invokes `mutation_callback`
- package version and public `__version__` set to `0.2.0`
- Package and Release workflow version asserts set to `0.2.0`

## Not included

- no GitHub tag or release in this commit
- Ed25519 (specified, not implemented)
- durable nonce or audit storage
- production readiness, compliance, or path-universal enforcement

## Install (after B2 only)

Until `/releases/latest` is `v0.2.0`, install the historical Latest tag:

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.1.1"
```

That install is the mutation-callback object. Do not cite it as this kernel.

## Verify (this tree, unreleased)

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
python -c "from commit_gate_core import __version__; print(__version__)"
```

Expected version on this tree: `0.2.0`.

## Claim boundary

These notes describe authorize-only behaviour on this tree. They do not
establish that GitHub Latest is this tree until B2 verifies
`/releases/latest` is `v0.2.0` and this file is the published body.
