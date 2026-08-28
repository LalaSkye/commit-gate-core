# DecisionRecord Contract (Shape A)

## Purpose

A `DecisionRecord` is the smallest authority artefact the commit gate will accept.

It does not describe intent in general. It authorises one exact payload under one exact scope.

The public kernel **authorises**. It does not apply the payload. Authorisation is not execution.

If the record is missing, malformed, expired, replayed, rejected by the configured verifier, or scoped to another payload, the gate refuses. The world is not applied-to by this kernel.

---

## Required fields

Field names are schema v1 (`SIGNED_FIELDS`). This document does not add or remove fields.

| Field | Type | Required | Purpose |
|---|---:|---:|---|
| `decision_id` | string | yes | Unique identifier for the authority decision |
| `actor_id` | string | yes | Actor requesting authorisation |
| `action` | string | yes | Operation being authorised |
| `object_id` | string | yes | Target object |
| `environment` | string | yes | Execution environment, e.g. `dev`, `staging`, `prod` |
| `commit_hash` | string | yes | Hash of the exact payload being authorised (bound inside the gate from `payload_bytes`) |
| `verdict` | string | yes | Must be `ALLOW` for authorisation to proceed |
| `policy_version` | string | yes | Policy version under which the decision was issued |
| `issued_at` | RFC3339 timestamp | yes | Time the decision was issued |
| `expires_at` | RFC3339 timestamp | yes | Time after which the decision is invalid |
| `nonce` | string | yes | One-use replay prevention value |
| `signature` | string | yes | Authenticator slot over the canonical record bytes. Schema v1 keeps this name. The demonstrated verifier is an HMAC-SHA256 lab MAC, not a public-key signature. Ed25519 is specified and not implemented. |

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

The `hmac-sha256:` example is a lab MAC encoding, not a signature algorithm claim.

---

## Binding rule

A `DecisionRecord` is valid only for the exact tuple:

```text
actor_id + action + object_id + environment + commit_hash + policy_version + time_window + nonce
```

`commit_hash` must equal the hash the gate computes from `payload_bytes`.
The gate must not generalise from one valid record to another attempted payload.

| Scenario | Result |
|---|---|
| Matching record, matching payload bytes, unused nonce, valid time window | `AUTHORIZED` |
| Matching record, different payload bytes | `DENY` |
| Matching record, different object | `DENY` |
| Matching record, expired time window | `DENY` |
| Matching record, reused nonce | `DENY` |
| Matching record, different environment | `DENY` |
| `commit_hash` without `payload_bytes` | `DENY:COMMIT_HASH_ONLY_FORBIDDEN` |

---

## Authenticator payload

The authenticator is calculated over `canonical_bytes(record)`: required fields except `signature`, keys sorted, compact JSON separators.

A missing field is a structural failure, not a defaultable value.

The configured verifier decides accept/refuse. Tests use HMAC-SHA256. That is a lab MAC. Ed25519 is not implemented.

---

## Verdict rule

Only record verdict `ALLOW` can continue evaluation toward `AUTHORIZED`.

All other verdicts are non-authorising. The kernel still does not apply a payload.

---

## Time rule

The gate accepts a record only when:

```text
issued_at <= now <= expires_at
```

relative to the **injected** clock. That does not protect against a compromised clock.

Invalid timestamp format is a structural failure.

---

## Replay rule

The nonce is consumed only after validation passes, on the authorise path.
Consumption is not permission to apply a payload.

If the authorised audit append fails, authorisation is refused and nonce rollback is attempted. Rollback failure has a separate error code.

A consumed nonce cannot authorise again on this in-memory ledger. The ledger is not durable.

---

## Out of scope

This contract does not define key issuance, human approval, upstream policy, orchestration, transport security, world application, or crash-safe persistence.

---

## Contract status

Shape A alignment of the public contract text. Schema field names remain v1.
