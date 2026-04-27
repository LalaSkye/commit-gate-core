# DecisionRecord Contract

## Purpose

A `DecisionRecord` is the smallest authority artefact the commit gate will accept.

It does not describe intent in general. It authorises one exact commit attempt under one exact scope.

If the record is missing, malformed, expired, replayed, unsigned, incorrectly signed, or scoped to another commit, the gate returns `DENY` and no state mutation occurs.

---

## Required fields

| Field | Type | Required | Purpose |
|---|---:|---:|---|
| `decision_id` | string | yes | Unique identifier for the authority decision |
| `actor_id` | string | yes | Actor attempting the commit |
| `action` | string | yes | Operation being authorised |
| `object_id` | string | yes | Target object of the commit |
| `environment` | string | yes | Execution environment, e.g. `dev`, `staging`, `prod` |
| `commit_hash` | string | yes | Hash of the exact commit payload being authorised |
| `verdict` | string | yes | Must be `ALLOW` for execution to proceed |
| `policy_version` | string | yes | Policy version under which the decision was issued |
| `issued_at` | RFC3339 timestamp | yes | Time the decision was issued |
| `expires_at` | RFC3339 timestamp | yes | Time after which the decision is invalid |
| `nonce` | string | yes | One-use replay prevention value |
| `signature` | string | yes | Cryptographic signature over the canonical record payload |

---

## Canonical JSON shape

```json
{
  "decision_id": "dr_20260427_001",
  "actor_id": "agent_17",
  "action": "approve_invoice",
  "object_id": "invoice_778",
  "environment": "prod",
  "commit_hash": "sha256:9f4a...",
  "verdict": "ALLOW",
  "policy_version": "2026-04-27.1",
  "issued_at": "2026-04-27T05:00:00Z",
  "expires_at": "2026-04-27T05:05:00Z",
  "nonce": "n_7f3c9b2a",
  "signature": "hmac-sha256:..."
}
```

---

## Binding rule

A `DecisionRecord` is valid only for the exact tuple:

```text
actor_id + action + object_id + environment + commit_hash + policy_version + time_window + nonce
```

The gate must not generalise from one valid record to another attempted commit.

Examples:

| Scenario | Result |
|---|---|
| Same record, same commit hash, unused nonce, valid time window | `ALLOW` |
| Same record, altered commit payload | `DENY` |
| Same record, different object | `DENY` |
| Same record, expired time window | `DENY` |
| Same record, reused nonce | `DENY` |
| Same record, different environment | `DENY` |

---

## Signature payload

The signature is calculated over the canonical record payload excluding the `signature` field itself.

Canonicalisation rules:

1. Include every required field except `signature`.
2. Sort keys lexicographically.
3. Use compact JSON separators.
4. Do not infer missing fields.
5. Do not coerce types silently.

A missing field is a structural failure, not a defaultable value.

---

## Verdict rule

Only `ALLOW` can authorise mutation.

All other verdicts are non-authorising:

| Verdict | Gate result |
|---|---|
| `ALLOW` | Continue evaluation |
| `HOLD` | `DENY` |
| `DENY` | `DENY` |
| Unknown verdict | `DENY` |

The gate may expose `HOLD` or `DENY` as reason codes, but the execution outcome remains blocked.

---

## Time rule

The gate accepts a record only when:

```text
issued_at <= now <= expires_at
```

If `issued_at` is in the future, the record is invalid.

If `expires_at` has passed, the record is invalid.

Invalid timestamp format is a structural failure.

---

## Replay rule

The nonce is consumed only after all validation checks pass and immediately before mutation is attempted.

A consumed nonce cannot authorise another mutation.

If the mutation fails after nonce consumption, the caller must obtain a new `DecisionRecord`.

---

## Out of scope

This contract does not define:

- key issuance
- human approval workflow
- upstream policy reasoning
- multi-agent orchestration
- transport security

Those belong outside the core gate.

---

## Contract status

`LOCK CANDIDATE` — this document defines the first public contract shape for `commit-gate-core`.
