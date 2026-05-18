# Commit Gate Core

**Research Surface Map:** [lalaSkye.github.io/inspection-surface](https://lalaskye.github.io/inspection-surface/) — full index, provenance, and cross-links


New to this work? Start here: https://github.com/LalaSkye/start-here

## Public disclosure boundary

This repository is a public inspection surface, not full architecture disclosure.

It shows a bounded claim, a runnable evidence object, an inspection path, and the claim limit.

See [`PUBLIC_DISCLOSURE_BOUNDARY.md`](PUBLIC_DISCLOSURE_BOUNDARY.md).

## What this repo is

Commit Gate Core is a small public proof surface for one execution-boundary claim.

It demonstrates a path-local control condition:

> No state mutation on the demonstrated path without a valid, scoped, unexpired, unreplayed `DecisionRecord`.

If the required condition fails, the demonstrated action does not run.

## Scope and limitations

This repository demonstrates one bounded path-local commit-gate behaviour.

It does not claim:

- production readiness
- enterprise deployment
- compliance or certification
- path-universal governance
- payload binding across all systems
- atomic commit across all routes
- non-bypassability outside the demonstrated path

## Try it in 30 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

Expected output:

```text
Result: HOLD
Email sent: false
Receipt written: true
```

## Inspection path

Run the demo and adversarial invariant verifier:

```bash
python -m examples.unsafe_email_send
python scripts/verify_adversarial_invariants.py
```

The narrow question this repo answers is:

**Can the demonstrated action reach consequence without a valid DecisionRecord?**

Expected answer:

**No.**

## What this proves

On the demonstrated path:

- unsafe consequence can be refused before execution
- missing authority prevents mutation
- failed checks produce HOLD / DENY behaviour
- refusal can produce an auditable receipt when the audit sink accepts the event
- bypass failure can be tested directly

## What this does not prove

This repository does not prove adoption, certification, standardisation, production readiness, compliance, or path-universal deployment coverage.

It does not prove the wider governance architecture.

It proves only the bounded claim attached to this public proof object.

## Evidence shape

For the demonstrated scenario:

```text
Execution occurred: false
Receipt written:    true
Verdict:            HOLD
```

## Claim discipline

Claim discipline for this repo is controlled in:

[`docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md`](docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md)

## Related public artefact

Working paper:

**From Policy to Commit: Execution-Boundary Control for Governed AI Systems**

- DOI: https://doi.org/10.5281/zenodo.19980275
- Zenodo record: https://zenodo.org/records/19980275

## Status

`v0.1` — bounded public proof surface.

Small surface. Clear failure mode. Receipts over reassurance.

## License

MIT.
