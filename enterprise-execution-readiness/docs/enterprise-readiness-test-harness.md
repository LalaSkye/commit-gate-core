# Enterprise-Readiness Test Harness

## Status

**Version:** v0.1  
**Scope:** Synthetic / mocked downstream systems / CI replay  
**Claim:** Test-harness evidence only  

This document defines what the enterprise-shaped scenario harness currently proves and what remains absent.

## Clean claim

This harness tests whether a bounded AI-assisted action can reach a mocked downstream system when required authority is missing.

For ESP-001, the answer is:

```text
missing authority_token
  -> DENY
  -> mock email adapter not called
  -> downstream_send=false
  -> receipt_written=true
```

## What this harness proves

On the synthetic path, the harness proves:

- the action class is named: `SEND_EXTERNAL_EMAIL`
- the required authority field is missing: `authority_token`
- the gate returns `DENY`
- the mocked downstream email adapter is not called
- the adapter records zero sent messages
- a receipt is generated
- the scenario can be replayed by pytest
- the test can run in GitHub Actions

## What this harness does not prove

This harness does not prove:

- live SMTP / API non-execution
- production runtime enforcement
- enterprise deployment
- certification
- compliance
- legal adequacy
- closure of all bypass paths
- no dispatch through queues, retries, alternate APIs, human handoff, or connector side channels
- real-world controlled application
- external review

## Required evidence for stronger claims

| Stronger claim | Required evidence |
|---|---|
| Live runtime enforcement | Gate integrated with a real execution layer or realistic service boundary |
| Downstream non-execution | External connector call logs or service-level event evidence |
| Path-universal control | Architecture showing every consequence path routes through the gate or is explicitly out of scope |
| Enterprise readiness | Multiple realistic enterprise workflows, CI replay, bypass tests, external review, and controlled organisational pilot evidence |
| Production readiness | Deployment architecture, operational monitoring, failure handling, persistence, security review, and live audit trail |
| Certification / compliance | Independent qualified assessment against a named framework or legal requirement |

## Current label

Safe:

```text
enterprise-readiness test harness
```

Unsafe:

```text
enterprise-ready system
enterprise deployment evidence
production enforcement proof
certified control
compliance-ready system
```

## Next hardening path

1. Add more mocked consequence classes:
   - payment instruction
   - access change
   - HR decision support
   - vendor risk escalation

2. Add bypass tests:
   - retry cannot dispatch after denial
   - queue cannot dispatch after denial
   - stale DecisionRecord rejected
   - alternate send path blocked
   - audit failure fails closed

3. Add evidence matrix:
   - claim
   - required evidence
   - current proof
   - missing proof
   - next test

4. Add external review route:
   - issue template for hostile review
   - reviewer checklist
   - reproducibility instructions

## Stop rule

Do not call this enterprise-ready until an external reviewer or bounded organisation can inspect, run, and challenge the harness against a realistic workflow.
