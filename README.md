# commit-gate-core

> Runtime governance only matters when it can block mutation at the commit boundary.

`commit-gate-core` is a minimal Python reference implementation of execution-bound governance.

**Core invariant:** No state mutation is permitted unless a signed, scoped, unexpired, and unreplayed `DecisionRecord` authorises the exact commit.

---

## What this exposes

| Component | Purpose |
|---|---|
| `DecisionRecord` contract | The authorisation unit every gate checks |
| `CommitGate` | Blocks mutation at the commit boundary |
| Nonce replay protection | One-use enforcement |
| Audit trail | Immutable log of every decision |
| Adversarial tests | Pre-registered failure modes |
| Terminal demo | One-file walkthrough |

## What this does NOT expose

- Full TrinityOS orchestration
- Multi-agent architecture
- Private calculus or system map

## Status

`REFERENCE KERNEL v1 — spec, contract, gate kernel, and initial tests live`

## Structure

```
commit-gate-core/
├── README.md
├── docs/
│   ├── invariant.md
│   ├── decision-record.md
│   ├── threat-model.md
│   └── pre-registered-failures.md
├── src/
│   └── commit_gate_core/
│       ├── decision_record.py
│       ├── gate.py
│       ├── nonce_ledger.py
│       ├── audit.py
│       └── state_store.py
├── tests/
│   ├── test_no_record_blocks.py
│   ├── test_invalid_signature_blocks.py
│   ├── test_replay_blocks.py
│   ├── test_scope_mismatch_blocks.py
│   └── test_params_tamper_blocks.py
└── demo/
    └── terminal_demo.py
```

## Licence

TBD
