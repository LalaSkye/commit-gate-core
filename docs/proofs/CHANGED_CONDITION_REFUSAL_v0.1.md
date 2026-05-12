# CHANGED_CONDITION_REFUSAL_v0.1

**Artefact:** commit-gate-core — Changed-Condition Refusal Proof Surface  
**Status:** DRAFT — Synthetic proof surface only  
**Scope:** NON_EXEC / REVIEW_ONLY  
**Claim boundary:** Not production deployment. Not enterprise adoption. Not compliance certification.

---

## Claim

Yesterday's permission is not today's authority.

When conditions change after authority was granted, the gate must refuse the transition before mutation occurs and write a receipt recording what changed and why.

---

## Proof conditions

| Condition | Expected decision | Mutation committed |
|---|---|---|
| All conditions unchanged | ALLOW | false |
| Payload hash changed | REFUSE_PAYLOAD_HASH_MISMATCH | false |
| Recipient scope changed | REFUSE_SCOPE_MISMATCH | false |
| State version changed | REFUSE_STATE_VERSION_MISMATCH | false |
| Authority token expired | REFUSE_AUTHORITY_EXPIRED | false |

---

## Receipt fields (all refusal paths)

- `receipt_id`
- `scenario_id`
- `attempted_action`
- `actor`
- `authority_token_ref`
- `recipient_scope`
- `payload_hash`
- `state_version`
- `changed_condition` — which condition changed
- `expected_value` — what the gate expected
- `actual_value` — what was presented
- `decision`
- `refusal_reason`
- `mutation_committed: false`
- `timestamp`
- `previous_receipt_hash` — optional in this proof surface; full receipt-chain continuity is a separate proof concern

---

## Replay stability

Same changed-condition attempt run twice produces:
- same decision class
- same refusal reason
- `mutation_committed: false` on both runs

---

## What this proves

- Authority checked at consequence time, not grant time
- Changed condition stops the transition before mutation
- Receipt records the exact condition that changed
- No mutation occurred on any refusal path
- Refusal is deterministic and replayable

## What this does not prove

- Production enforcement
- Enterprise deployment
- Compliance certification
- Complete governance coverage
- Receipt-chain continuity (separate proof surface)
