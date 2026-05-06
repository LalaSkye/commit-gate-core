# CI GREEN PROOF REQUIREMENTS

Status: ACTIVE  
Trigger class: Claim-boundary change  
Scope: CI_GREEN_PROOF only

---

## Purpose

This file defines the evidence required to close the `CI_GREEN_PROOF` open claim.

---

## Required evidence

1. observable GitHub Actions workflow run
2. run linked to a commit SHA
3. workflow conclusion marked success
4. workflow name identified
5. job logs or workflow run URL referenced
6. BUILD_RECEIPTS entry created
7. OPEN_CLAIMS entry moved from Unheld to Closed
8. CHANGELOG entry records claim closure

---

## What does not close the claim

- local verifier receipt
- passing local tests
- workflow file existence
- trigger commit existence
- connector silence

---

## Standing boundary

CI green proof proves only scoped CI success.

It does not prove production runtime enforcement.
