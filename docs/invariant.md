# Core Invariant

## Statement

No state mutation is permitted unless a `DecisionRecord` exists that:

1. **Is signed** — carries a valid cryptographic signature from an authorised agent
2. **Is scoped** — binds exactly to the target commit hash and operation
3. **Has not expired** — timestamp is within the permitted execution window
4. **Has not been replayed** — nonce is unique and has not appeared in the ledger

If any condition fails, the gate returns `DENY`. No partial authorisation is possible.

## Why this matters

Runtime governance that cannot block at the boundary is advisory, not enforceable. This invariant ensures the gate is the single point of truth for mutation permission.

## Evaluation order

Gate evaluation follows `STRUCTURE_FIRST` then `FIRST_FAIL`:
- Validate structure before evaluating claims
- Stop at the first violation — do not accumulate partial passes

## Invariant status

`FROZEN` — this invariant is not subject to PROJECT-level override.
