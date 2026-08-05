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

No install step is required for the demonstration. The gate kernel uses the
Python standard library only.

## Install

Requires Python 3.11 or later.

Install the tagged release from GitHub:

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.1.1"
```

Or install a local clone:

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m pip install .
```

With test dependencies:

```bash
python -m pip install -e ".[dev]"
```

Or using the Makefile:

```bash
make install-dev   # editable install plus pytest
make demo          # 30-second refusal demonstration
make test          # full test suite
make adversarial   # adversarial invariant verifier
```

Run `make help` to list all targets.

After installation, verify the public package surface:

```python
from commit_gate_core import CommitGate, __version__

print(__version__)
```

Packaging files:

- [`pyproject.toml`](pyproject.toml) — package metadata and build configuration
- [`requirements.txt`](requirements.txt) — runtime dependencies (none; standard library only)
- [`requirements-dev.txt`](requirements-dev.txt) — test dependencies
- [`Makefile`](Makefile) — inspection and verification entry points

Claim boundary: these files provide an install path. They do not add capability,
and they do not extend any claim made elsewhere in this repository.

## Known test status

Dated snapshot, 5 August 2026. Recorded here so the state is inspectable rather
than implied.

| Surface | Result |
|---|---|
| `make demo` | passes |
| `make adversarial` | passes — all three invariant vectors |
| Existing CI workflows (adversarial invariants and ESP-001) | passing |
| `python -m pytest` | **49 passed, 0 failed** |
| Package workflow | builds and installs the wheel, then checks it outside the checkout |

The four earlier changed-condition failures were corrected in PR #25 by fixing
malformed test data and one weaker expectation. `src/commit_gate_core/gate.py`
was not changed. This packaging patch adds two installed-package checks, taking
the root suite from 40 to 42 tests.

PR #26 repaired the enterprise test loaders without changing the gate. Those
seven tests now run under bare `pytest` alongside the 42 root tests. This is a
test-discovery and harness result; no enterprise-readiness claim is made.

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

`v0.1.1` — installable bounded public proof surface with complete default test
discovery.

Small surface. Clear failure mode. Receipts over reassurance.

## License

MIT.
