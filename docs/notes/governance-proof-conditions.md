# Governance proof conditions

A system is governed only if it can prove, at the point where an output can bind consequence:

1. Valid authority existed.
2. The action was within scope.
3. The payload was admissible under the conditions at that time.
4. The state transition was permitted.
5. If not permitted, refusal occurred before mutation.
6. A record proves that refusal occurred.

**No receipt, no proof.**

## Boundary

This note claims that a proof layer must exist at the consequence boundary.

It does not claim that the proof layer is tamper-proof.

Recursive proof integrity, receipt tamper-resistance, and proof-layer optimisation are separate design questions and are not resolved here.

## Inspection surface

This repository is an inspection surface for the execution-boundary model.

It does not evidence production deployment, regulatory approval, compliance certification, or third-party adoption.
