# Repository Receipt

Date: 2026-08-31

Repository: `LalaSkye/commit-gate-core`

Object: unreleased `v0.2.0` prepare (authorize-only). GitHub Latest remains `v0.1.1`.

Evidence class: bounded in-process reference kernel

## Observed function

The current public kernel on this tree accepts a DecisionRecord, caller-supplied
`payload_bytes` and exact scope fields. It hashes the payload inside the gate,
evaluates the configured checks and returns an authorisation or refusal
result. It does not apply the payload.

## Runnable inspection

```bash
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

The inspected tests cover authorize-without-mutate, payload/hash binding,
hash-only refusal, typed failure paths and audit-failure nonce rollback using
in-memory test objects.

## Exact limits

- `v0.1.1` remains the latest tagged release and contains the historical
  mutation-callback object. It is not this successor.
- This prepare does not tag or publish. `/releases/latest` is unchanged.
- The demonstrated verifier is an HMAC-SHA256 lab MAC, not Ed25519.
- Nonce and audit durability are not established.
- An external caller can ignore the verdict and invoke another consequence
  path. This repository does not prevent that.
- The repository does not establish production readiness, deployment,
  compliance, certification, adoption, safety or path-universal enforcement.

## Related evidence

- Current object and command: `README.md`
- Claim ceiling: `CLAIM_BOUNDARY.md`
- Current invariant: `docs/invariant.md`
- Authorize-only cut: `docs/governance/SHAPE_A_AUTHORIZE.md`
- Prepare notes (not published as Latest): `RELEASE_NOTES.md`

## Receipt line

Payload-bound authorisation is evidenced on this tree. Payload application,
external enforcement, and GitHub Latest identity with this tree are not claimed.
