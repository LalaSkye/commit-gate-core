# Runtime Governance Evidence Packet v1

## Purpose

This packet gives a buyer-readable format for inspecting whether an AI-assisted action was permitted to bind consequence.

It does not inspect whether the AI output was high quality.

It inspects whether the action had permission to execute.

## Core question

> Can the organisation prove what happened when an AI-assisted action tried to bind consequence?

## Evidence fields

| Field | Purpose |
|---|---|
| `action_attempted` | Names the action that tried to execute |
| `consequence_boundary` | Identifies what real-world or system consequence would occur |
| `required_authority` | States what authority must exist before execution |
| `scope_condition` | Defines the permitted recipient, record, asset, workflow, or domain |
| `freshness_check` | Shows whether authority was current at gate time |
| `replay_check` | Shows whether stale or reused authority was blocked |
| `state_check` | Shows whether the current system / business state still permitted the action |
| `verdict` | `ALLOW`, `HOLD`, or `DENY` |
| `mutation_occurred` | `true` / `false` — whether the action changed state or triggered consequence |
| `receipt_written` | `true` / `false` — whether an inspectable receipt exists |
| `claim_boundary` | States what the packet does and does not prove |
| `unproven` | Lists the evidence still absent |

## Verdict classes

| Verdict | Meaning |
|---|---|
| `ALLOW` | Required authority, scope, freshness, replay, and state conditions were satisfied on the demonstrated path |
| `HOLD` | The system cannot safely decide; human or governance review is required before execution |
| `DENY` | A required condition failed; the action must not execute |

## Minimum packet example

```json
{
  "packet_id": "RGE-2026-0512-001",
  "scenario_id": "ESP-001",
  "action_attempted": "SEND_EXTERNAL_EMAIL",
  "consequence_boundary": "external email leaves system",
  "required_authority": "fresh scoped authority token for actor, action_type, recipient_scope, and payload_hash",
  "scope_condition": "recipient_scope must match approved external recipient domain",
  "freshness_check": "authority_token must be unexpired at gate time",
  "replay_check": "nonce must be unused",
  "state_check": "current workflow state must permit external send",
  "verdict": "DENY",
  "mutation_occurred": false,
  "receipt_written": true,
  "claim_boundary": "path-local refusal evidence only; no enterprise deployment claim",
  "unproven": [
    "production integration",
    "external review",
    "path-universal bypass closure",
    "real-world controlled application"
  ]
}
```

## Buyer-readable summary

The evidence packet should allow a buyer, auditor, risk lead, or technical reviewer to answer:

1. What action tried to happen?
2. What consequence would it have bound?
3. What authority was required?
4. Was the authority fresh and scoped?
5. Was replay blocked?
6. Was the current state checked?
7. Did the action execute?
8. Was a receipt written?
9. What remains unproven?

## Boundary

This packet is an inspection format.

It is not a certification, legal opinion, compliance guarantee, or production-readiness claim.
