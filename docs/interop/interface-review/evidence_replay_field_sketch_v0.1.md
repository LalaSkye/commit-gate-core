# Evidence / Replay Field Sketch v0.1

## Status

Draft v0.1. Scope: Interop Lab interface review.

## Purpose

This file defines a minimal evidence and replay field sketch for Lab interface submissions.

The purpose is to preserve inspectable comparison. It is not to prove runtime governance unless the submitted system separately provides that mechanism.

## Minimal Evidence Fields

Each submission should provide:

- submission_id
- contributor
- artefact_name
- artefact_version
- submission_date
- interface_item
- claim_under_review
- evidence_type
- evidence_reference
- result_class
- reason_code
- limitation_statement
- replay_available
- replay_reference
- provenance_reference
- review_notes

## Field Definitions

### submission_id

A unique identifier for the submitted item.

### contributor

The person, team, organisation, or project submitting the artefact.

### artefact_name

The submitted artefact name.

### artefact_version

The declared version of the submitted artefact.

### submission_date

The date the artefact was submitted or reviewed.

### interface_item

The specific Lab interface item under review.

### claim_under_review

The narrow claim being tested or compared. This must stay smaller than the submitted evidence.

### evidence_type

The category of evidence supplied.

Examples include specification, test output, trace, log, screenshot, repository file, paper, runtime receipt, and demo recording.

### evidence_reference

A stable reference to the evidence artefact.

This may be a file path, commit link, DOI, archive link, or other inspectable reference.

### result_class

One of PASS, PARTIAL, FAIL, HOLD, or OUT_OF_SCOPE.

### reason_code

A structured reason code explaining the result.

### limitation_statement

A short statement describing what the evidence does not prove.

### replay_available

Use yes, no, or partial.

### replay_reference

A path or instruction showing how the evidence can be replayed or rechecked.

If replay is unavailable, this field must say why.

### provenance_reference

A reference showing contributor source, version, authorship, or submission custody.

### review_notes

Short review notes. Review notes must not expand the claim beyond the evidence.

## Replay Rule

Replay is an evidence function. Replay does not create authority.

A replayable artefact can support comparison, inspection, and review.

It does not prove that the submitted system has non-bypassable runtime control unless that control is separately evidenced.

## Observational-Signal Rule

Sequence-level signals, trajectory indicators, continuity markers, and interpretability features may be recorded as evidence.

They remain observational at the Lab interface. They do not become authority semantics.

## Example

submission_id: IL-IR-0001  
contributor: Example Contributor  
artefact_name: Example Adapter Output  
artefact_version: v0.1  
submission_date: 2026-05-02  
interface_item: result_class_reason_code_surface  
claim_under_review: Submitted artefact provides result class and reason code.  
evidence_type: repository_file  
evidence_reference: docs/example/example_adapter_output.md  
result_class: PARTIAL  
reason_code: PARTIAL:COMPARABILITY:RESULT_CLASS_PRESENT_REASON_CODE_MISSING  
limitation_statement: This shows partial interface compatibility only. It does not prove runtime governance.  
replay_available: partial  
replay_reference: Manual inspection of submitted repository file.  
provenance_reference: Contributor-declared repository path and version.  
review_notes: Result class was present. Reason code surface was missing.

## Clean Stop

The evidence and replay surface supports inspection. It does not authorise execution.
