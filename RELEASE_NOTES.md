# Release Notes

## Governance notes

- 2026-05-04 — Issue #6 opened: Condition Freshness Check v0.1, a bounded DecisionRecord validation surface that resolves to HOLD when the supporting condition is stale, unevidenced, out-of-scope, or freshness is unknown.

## Room state sketch

- Condition Freshness Check v0.1 is recorded as a bounded DecisionRecord validation surface (no code yet) that fail-closes to HOLD when its authorising condition is stale, unevidenced, out-of-scope, or freshness is unknown.

## Reusable tags

- Freshness HOLD — preferred future issue-title phrase for test cases.
- freshness-hold — primary internal slug / machine-findable key.

## Future work headings

- Freshness Test Cases v0.1
- Receipt Visibility (Read-Only) v0.1
- Condition Typing & Limits v0.1
- Operational Telemetry v0.1
- Human Override Patterns v0.1
