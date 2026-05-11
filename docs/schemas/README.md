# Runtime Impossibility Receipt Schema

This folder contains a bounded schema and synthetic example for recording why a consequence-producing action could not validly proceed at runtime.

## Purpose

The Runtime Impossibility Receipt Schema captures the control conditions checked before an action is allowed to bind consequence.

The schema records:

- attempted action
- actor
- authority
- scope
- freshness
- replay protection
- current state
- verdict
- reason
- downstream effect prevented
- human review requirement
- claim boundary

## Plain line

The receipt does not merely say that an action was discouraged.

It records why the action could not validly proceed.

## Files

- `Runtime_Impossibility_Receipt_Schema_v0.1.json` — schema definition
- `examples/runtime_impossibility_receipt_email_refusal_v0.1.json` — synthetic refusal example

## Claim boundary

This is a bounded artefact and path-local demonstration.

It does not prove:

- adoption
- validation
- endorsement
- certification
- compliance
- production readiness
- medical safety
- field impact
- proven market demand
- path-universal coverage
- standardisation

## Status

Version: v0.1  
Status: synthetic example / inspection surface  
Use: research, demonstration, and artefact review only
