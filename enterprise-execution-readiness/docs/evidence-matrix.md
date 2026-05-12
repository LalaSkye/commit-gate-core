# Evidence Matrix — Enterprise-Shaped Scenario Harness

## Status

**Version:** v0.1  
**Scope:** Synthetic / mocked downstream / CI replay  
**Rule:** Claims can widen only when evidence widens.

## Matrix

| Claim | Required evidence | Current proof | Missing proof | Next test |
|---|---|---|---|---|
| Missing authority blocks send | Gate returns `DENY` when `authority_token` is absent | ESP-001 synthetic harness and pytest assert `DENY` | Integration with real gate primitive | Wire ESP-001 to `commit_gate_core` gate object |
| Denied action does not reach downstream adapter | Mock downstream adapter has zero send calls after denial | `test_esp_001_email_no_send.py` asserts `send_call_count == 0` and `sent_messages == []` | Live SMTP/API connector evidence | Add realistic connector boundary mock with call log fixture |
| Receipt is written | Synthetic result records `receipt_written=true` and fixture exists | `ESP-001-refusal-receipt.json` + trace harness receipt | Persistent audit sink / append-only log | Add in-memory append-only receipt log with hash chain |
| State does not mutate | Before and after state hashes match in synthetic trace | `run_scenario_001.py` asserts `before_hash == after_hash` | External state store evidence | Add state store mock with committed-state snapshot |
| Scenario is replayable | Test runs under pytest and GitHub Actions workflow | `.github/workflows/enterprise-shaped-scenarios.yml` | Confirm passing CI run after merge/push | Inspect workflow result after trigger |
| Path-local boundary is clear | Claim boundary states synthetic, path-local, not runtime enforcement | README, scenario, receipt claim boundary | External reviewer confirmation | Add hostile review issue template |
| Enterprise readiness | Multiple realistic workflows, bypass tests, external review, controlled pilot | Not proven | Payment, access, HR, vendor risk, bypass suite, external review | Build ESP-002 payment expired-authority test |
| Production enforcement | Live execution layer, routing proof, monitoring, persistence, failure handling | Not proven | Real integration and operational evidence | HOLD until real integration exists |
| Compliance / certification | Independent qualified assessment against named standard | Not proven | Auditor/certifier review | HOLD until external authority exists |

## Current score posture

This is stronger than a documentation-only scenario because it now has:

- inspectable structure
- mocked downstream adapter
- pytest non-call proof
- synthetic trace harness
- receipt fixture
- CI replay surface

It is still not enterprise-ready evidence because it lacks:

- live execution layer
- external review
- real-world controlled application
- path-universal bypass analysis
- production or audit evidence

## Compression line

The harness proves a mocked downstream email adapter is not called when authority is missing. It does not prove live enterprise enforcement.
