# commit-gate-core v0.1.0

First packaged release of the bounded, path-local commit-gate proof surface.

## Included

- standards-based Python packaging
- stable public imports from `commit_gate_core`
- bundled ESP-001 synthetic refusal fixture
- wheel and source-distribution build checks
- automated GitHub release assets for tagged versions
- explicit MIT licence file

## Install

```bash
python -m pip install "commit-gate-core @ git+https://github.com/LalaSkye/commit-gate-core.git@v0.1.0"
```

## Verify

```bash
python -c "from commit_gate_core import CommitGate, __version__; print(__version__)"
```

Expected output: `0.1.0`.

## Claim boundary

This release makes the existing bounded code easier to install and inspect.
It does not establish production readiness, enterprise deployment, compliance,
certification, path-universal governance, external validation, or a managed
commercial deliverable.
