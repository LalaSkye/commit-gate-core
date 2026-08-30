# Claim Boundary

Date: 2026-08-30

Repository: `LalaSkye/commit-gate-core`

Current object: unreleased `0.2.0a1` authorize-only successor on `main`

## One admissible sentence

> `commit-gate-core` binds caller-supplied payload bytes to a DecisionRecord,
> evaluates the configured checks, and returns authorisation or refusal. It
> does not apply the payload.

## What the demonstrated tests establish

On the tested in-process path:

- the payload hash is computed inside `authorize`;
- a caller-supplied hash without payload bytes is refused;
- scope, verdict, policy version, time window, verifier result and nonce state
  are checked;
- the demonstrated verifier is an HMAC-SHA256 lab MAC;
- an accepted record returns an authorisation ticket;
- neither `authorize` nor the deprecated `execute` wrapper invokes
  `mutation_callback`;
- the tested nonce and audit objects are in-memory implementations.

## Release inheritance

`v0.1.1` is the latest tagged release and is a different object: its
`CommitGate.execute` path can invoke a mutation callback. The authorize-only
successor is unreleased. Claims and test receipts from either object must not
be inherited by the other.

## Forbidden claims

Do not claim that this repository:

- applies payloads or physically prevents an external caller from bypassing it;
- is a production gate or a non-bypassable enforcement boundary;
- implements Ed25519, durable nonce storage or atomic cross-system commit;
- proves safety, deployment, adoption, compliance, certification or
  path-universal coverage;
- establishes category priority, copying or superiority over another project.

## Comparison boundary

Another project requires its own directly inspected artefact and dated
side-by-side evidence. Shared vocabulary or later publication dates do not
establish copying.

## Stop line

Authorisation is the end of this kernel's claim. Application and external
enforcement belong to a separately evidenced object.
