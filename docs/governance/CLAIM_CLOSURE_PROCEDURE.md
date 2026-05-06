# CLAIM CLOSURE PROCEDURE

Status: ACTIVE  
Creation trigger class: Claim-boundary change  
Amendment trigger class: Mechanism change  
Governed by: `CHANGE_CONTROL.md`

---

## Purpose

This procedure defines the exact steps required to move a claim from `UNHELD` to `CLOSED` in `OPEN_CLAIMS.md`.

Closure by deletion is a governance violation.

Closure by this procedure is a constitutional transition.

---

## Required steps

All steps are mandatory and must occur in order.

### 1. Evidence

State what changed that makes the claim closeable.

Evidence must be specific and externally verifiable.

"It feels resolved" is not evidence.

### 2. Receipt

A `BUILD_RECEIPTS.md` entry must be created before the claim moves.

Trigger class: Claim-boundary change.

The receipt must name the claim being closed.

### 3. Changelog entry

A `CHANGELOG.md` entry must declare:

- which claim is closing
- which trigger class fired
- what evidence was accepted

### 4. Section movement

In `OPEN_CLAIMS.md`:

- move the claim entry from `Unheld claims` to `Closed claims`
- do not delete it
- add closure date and receipt reference

### 5. Index update

The governance index must reflect the state change.

---

## Forbidden actions

- Deleting a claim entry is a governance violation.
- Closing without a receipt is a governance violation.
- Closing without a changelog entry is a governance violation.
- Closing by pull request merge alone is a governance violation.

---

## What does not close a claim

- A local verification receipt alone
- A passing local test run
- Social consensus in a pull request comment
- Silence

---

## Standing boundary

Correct closure is a governed transition.

Silent closure is a governance violation.
