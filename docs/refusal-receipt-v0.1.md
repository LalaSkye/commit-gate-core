# Refusal Receipt v0.1

A refusal receipt is what the gate writes when it returns `DENY` or `HOLD`.

It is not the `DecisionRecord`.

The `DecisionRecord` is the authority object presented before execution.

The refusal receipt is the output the gate produces when the `DecisionRecord` is absent, invalid, expired, replayed, out of scope, or otherwise insufficient for the requested mutation.

## Core distinction

A clean payload does not authorise an action.

```text
valid_payload ≠ authorised_action
```

`DENY` is a first-class outcome.

It is not the absence of `ALLOW`.

The refusal receipt is the inspectable proof that execution was stopped before state mutation.

## Minimal schema

```json
{
  "receipt_id": "rr_20260509_001",
  "attempted_action": "send_external_email",
  "actor_id": "agent_17",
  "object_id": "email_outbound_004",
  "environment": "prod",
  "decision_outcome": "DENY",
  "failed_condition": "missing_decision_record",
  "authority_presented": null,
  "scope_context": "outbound_email_scope_v1",
  "reason_code": "NO_VALID_AUTHORITY",
  "policy_reference": "policy_v2026-04-27.1",
  "timestamp": "2026-05-09T16:16:00Z",
  "mutation_result": "blocked",
  "state_changed": false,
  "replay_reference": "rr_20260509_001"
}
```

## Field intent

| Field | Purpose |
|---|---|
| `receipt_id` | Stable identifier for the refusal event. |
| `attempted_action` | The action that tried to cross the commit boundary. |
| `actor_id` | The actor or agent requesting the action. |
| `object_id` | The target object of the attempted mutation. |
| `environment` | The environment in which the attempt occurred. |
| `decision_outcome` | Gate outcome: `DENY` or `HOLD` for refusal receipts. |
| `failed_condition` | The specific gate condition that failed. |
| `authority_presented` | The authority supplied, or `null` if none was supplied. |
| `scope_context` | The scope against which the action was evaluated. |
| `reason_code` | Machine-readable reason for refusal. |
| `policy_reference` | Policy or rule reference used by the gate. |
| `timestamp` | Time of the refusal event. |
| `mutation_result` | Whether mutation was blocked or allowed. |
| `state_changed` | Boolean proof of whether state changed. |
| `replay_reference` | Reference used to replay or inspect the refusal event. |

## Required proof surface

A useful refusal receipt should show:

1. what action was attempted
2. which authority or scope condition was missing or invalid
3. why the gate refused execution
4. whether state changed
5. which policy or rule was applied
6. how the refusal can be replayed or inspected

## Claim boundary

This schema is a bounded proof surface. It does not claim production readiness, compliance certification, or equivalence with any other authorisation framework.
