# commit-gate-core v0.1.1

> **Historical release object.** `v0.1.1` is still the latest tagged release
> and its `CommitGate.execute` path can invoke a caller-supplied mutation
> callback. Current `main` is the different, unreleased `0.2.0a1`
> authorize-only successor. These notes do not describe `main`.

Patch release widening default test discovery to the complete verified suite.

## Included

- bare `pytest` now discovers both the root and enterprise-shaped test surfaces
- complete-suite result: 49 passed, 0 failed
- package and tagged-release workflows run the same complete suite
- package version and public `__version__` advanced to `0.1.1`
- no change to `src/commit_gate_core/gate.py`

## Install

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.1.1"
```

## Verify

```bash
python -c "from commit_gate_core import CommitGate, __version__; print(__version__)"
```

Expected output: `0.1.1`.

## Claim boundary

This release makes the existing bounded code easier to install and inspect.
It does not establish production readiness, enterprise deployment, compliance,
certification, path-universal governance, external validation, or a managed
commercial deliverable.
