# Core Invariant (Shape A)

This text supersedes the v0.1 mutation-facing formulation.

## Statement

The public kernel authorises a DecisionRecord against caller-supplied `payload_bytes`. It does not apply the payload.

Authorisation requires a record that:

1. **Passes the configured verifier** — demonstrated tests use an HMAC-SHA256 lab MAC. That is not a public-key signature. Ed25519 is specified and not implemented.
2. **Is scoped** — binds actor, action, object, environment, and the payload hash computed inside the gate
3. **Has not expired** — evaluated against the injected clock
4. **Has not been replayed** — nonce unused on the in-memory ledger

If any condition fails, the gate refuses. The kernel does not apply the payload on success or on failure.

## Why this matters

A gate that applies the world and then reports refusal is a lie. Shape A separates authorisation from application. World-unchanged is the public kernel’s behaviour, including when a `mutation_callback` is supplied and ignored.

## Evaluation order

`STRUCTURE_FIRST` then `FIRST_FAIL`:
- Validate structure before evaluating claims
- Stop at the first violation

## Invariant status

Public-kernel statement for the authorize-only cut. It does not freeze production readiness or durable persistence.
