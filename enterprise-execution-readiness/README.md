# Enterprise-Shaped Scenario Evidence Pack

## Status

**Artefact class:** Buyer-readable execution-boundary scenario evidence packet  
**Version:** v0.1  
**Scope:** Synthetic / path-local / review-only  
**Claim rule:** Claims widen only when evidence widens.

> This is a synthetic, path-local demonstration. It does not prove runtime enforcement or downstream non-execution.

## What this is

This folder translates execution-boundary governance into a buyer-readable enterprise-shaped evidence packet.

It asks one practical question:

> Can an AI-assisted workflow bind consequence without valid authority, bounded scope, current state, freshness / replay protection, refusal route, and receipt evidence?

The first scenario is deliberately simple:

> An AI-generated external email may not be sent unless fresh, scoped authority exists for the actor, action type, recipient, and payload.

No authority token.  
No send in the synthetic trace.  
Receipt written.

## What this is not

This is not:

- certification
- compliance advice
- legal advice
- production assurance
- enterprise deployment proof
- adoption evidence
- path-universal governance
- proof that every bypass path is closed
- proof of runtime enforcement in a live execution layer
- proof of downstream non-execution outside the synthetic trace

It demonstrates a bounded evidence shape on the stated synthetic path only.

## Evidence chain

```text
policy rule
  -> control requirement
  -> runtime gate
  -> refusal condition
  -> refusal receipt
  -> synthetic execution trace
  -> audit evidence
```

## v0.1 contents

| Path | Purpose |
|---|---|
| `CLAIM_BOUNDARY.md` | States safe and forbidden claims |
| `docs/runtime-governance-evidence-packet-v1.md` | Buyer-readable evidence packet format |
| `scenarios/ESP-001-ai-generated-external-email.md` | First enterprise-shaped scenario |
| `receipts/ESP-001-refusal-receipt.json` | Example refusal receipt |
| `schemas/refusal-receipt.schema.json` | Minimal schema for receipt inspection |
| `run_scenario_001.py` | Synthetic trace harness for ESP-001 |

## Current proof surface

This package currently shows:

- a named action class
- a policy rule
- a required authority condition
- a missing-authority invalid condition
- a synthetic refusal before send
- an example receipt recording what stopped and why
- an execution trace shape: before_state, refusal_event, after_state, receipt
- a claim boundary

## Current hard limit

This package does not yet show:

- production integration
- external review
- real-world controlled application
- path-universal bypass analysis
- live enterprise deployment
- live execution-layer enforcement
- independent downstream-send verification
- certification or audit approval

## Clean line

We test the moment before the action.

Not the output.  
Not the policy.  
The permission.
