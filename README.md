# commit-gate-core

`REFERENCE KERNEL v1 — spec, contract, gate kernel, and initial tests live`

> **Core invariant:** No state mutation is permitted unless a signed, scoped, unexpired, and unreplayed `DecisionRecord` authorises the exact commit.

## Why this exists

Runtime governance only matters when it can block mutation at the commit boundary. Most AI and automation pipelines have no checkpoint between *the model decided* and *the action ran*. `commit-gate-core` is a small, deterministic, stdlib-only Python reference that closes that gap: a single, inspectable kernel that refuses to mutate state without a valid authorisation record.

Fail-closed by default. Minimal surface. Running code over commentary.

## What this exposes

| Component | Purpose |
|---|---|
| `DecisionRecord` contract | The authorisation unit every gate checks |
| `CommitGate` | Blocks mutation at the commit boundary |
| Nonce replay protection | One-use enforcement |
| Audit trail | Immutable log of every decision |
| Adversarial tests | Pre-registered failure modes |

## What this does NOT expose

- Full TrinityOS orchestration
- Multi-agent architecture
- Private calculus or system map

## Try it

```
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
pip install pytest
pytest -q
```

## Licence

TBD
