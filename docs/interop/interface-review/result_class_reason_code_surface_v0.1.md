# Result Class / Reason Code Surface v0.1

## Status

Draft v0.1. Scope: Interop Lab interface review.

## Purpose

This file defines a minimal result and reason-code surface for neutral comparison across submitted systems.

The result surface supports Lab review. It does not create shared authority semantics.

## Result Classes

### PASS

The submitted artefact satisfied the declared interface requirement for the reviewed item.

PASS means the Lab surface received sufficient evidence for that specific check. It does not mean the system is generally safe, governed, compliant, or authoritative.

### PARTIAL

The submitted artefact satisfied part of the declared interface requirement. The missing portion must be named.

### FAIL

The submitted artefact did not satisfy the declared interface requirement.

### HOLD

The submitted artefact cannot be assessed without further boundary, evidence, scope, or provenance clarification.

### OUT_OF_SCOPE

The submitted artefact may be meaningful, but it does not belong to the declared interface review.

## Reason Code Pattern

Reason codes should follow this structure:

CLASS:SURFACE:REASON

Example:

PARTIAL:EVIDENCE:REPLAY_FIELD_MISSING

## Standard Reason Codes

Boundary:

- HOLD:BOUNDARY:INTERFACE_NOT_DECLARED
- HOLD:BOUNDARY:CONTROL_LAYER_UNCLEAR
- FAIL:BOUNDARY:ARCHITECTURE_MERGER_IMPLIED
- OUT_OF_SCOPE:BOUNDARY:NOT_INTERFACE_REVIEW

Evidence:

- PARTIAL:EVIDENCE:REPLAY_FIELD_MISSING
- PARTIAL:EVIDENCE:PROVENANCE_FIELD_MISSING
- FAIL:EVIDENCE:NO_INSPECTABLE_ARTEFACT
- HOLD:EVIDENCE:CLAIM_EXCEEDS_SUBMITTED_PROOF

Runtime authority:

- HOLD:AUTHORITY:RUNTIME_DEFINITION_MISSING
- FAIL:AUTHORITY:OBSERVATION_PRESENTED_AS_CONTROL
- FAIL:AUTHORITY:INTERPRETABILITY_PRESENTED_AS_PERMISSION

Comparability:

- PASS:COMPARABILITY:MINIMAL_FIELDS_PRESENT
- PARTIAL:COMPARABILITY:RESULT_CLASS_PRESENT_REASON_CODE_MISSING
- HOLD:COMPARABILITY:SUBMISSION_FORMAT_UNSTABLE

Provenance:

- PASS:PROVENANCE:CONTRIBUTOR_AND_VERSION_DECLARED
- PARTIAL:PROVENANCE:VERSION_DECLARED_SOURCE_MISSING
- FAIL:PROVENANCE:CONTRIBUTOR_NOT_IDENTIFIED
- HOLD:PROVENANCE:ATTRIBUTION_DISPUTE_UNRESOLVED

## Claim Limits

A result class must not be inflated.

PASS at the Lab interface does not mean governance compliance, runtime authority, safety guarantee, legal approval, architecture equivalence, or adoption by the Lab.

It means only that the declared interface item was satisfied.

## Clean Stop

The result surface reports the review state. It does not authorise execution.
