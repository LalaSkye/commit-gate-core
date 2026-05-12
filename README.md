# Commit Gate Core
New to this work? Start here:
[https://github.com/LalaSkye/start-here](https://github.com/LalaSkye/start-here)

**Reference kernel for execution-boundary governance.**

Commit Gate Core stops unauthorised consequences before execution.

Most governance systems review decisions after consequences happen.  
This repo demonstrates a smaller, harder control surface:

> **No state mutation is allowed unless a signed, scoped, unexpired, unreplayed `DecisionRecord` authorises the exact commit.**

If authority, scope, expiry, replay, or receipt checks fail, the action does not run.

The proof is the failed execution path.

Claim discipline for this repo is controlled in [`docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md`](docs/governance/ADMISSIBLE_CLAIM_REGISTER_v1.md).

Run the adversarial invariant verifier locally: `python scripts/verify_adversarial_invariants.py`

---

## 1. Definition

**Admissibility** is the pre-execution test that determines whether a requested action has a valid basis to enter an executable state.

A requested action is admissible only when the required authority, scope, evidence, state, and time conditions are present and valid before execution is made available.

If those conditions are missing, invalid, expired, or unresolved, the action is not admissible.

In that case, the system should not create an executable state for the action.

---

## Scope and limitations

This repository demonstrates a **path-local commit gate**.

It enforces a single v1 invariant at the boundary it sits on:

> No consequence at this commit boundary without a valid signed, scoped,
> unexpired, unreplayed DecisionRecord.

This is the **path-local invariant**. It is what the code in this
repository implements and tests.

### Current hardening gaps

The stronger properties below are tracked as hardening work, not claimed as
current v1 guarantees:

- payload binding: see issue #8
- atomic commit boundary: see issue #9

### Recently hardened

The following v1 hardening gaps have been addressed on the demonstrated path:

- audit-failure control: see PR #18 / issues #10 and #11
- frozen DecisionRecord snapshot for audit fidelity: see PR #18 / issues #10 and #11

These fixes do not create a path-universal guarantee, production-readiness claim,
compliance claim, or certification claim.

### What this gate does not, by itself, prove

The **path-universal invariant** is stronger:

> No consequence is reachable without passing a proof-bound, payload-bound,
> atomic commit boundary across all paths.

Achieving the path-universal invariant is an **architectural placement
question**, not a gate-implementation claim. It requires:

- routing every reachable path to a consequence through a gate of this kind
- exclusion or explicit out-of-scope marking of alternate routes, including:
  - human review handoffs
  - downstream agent execution
  - asynchronous side channels
  - bypass paths created by retries, rollbacks, or recovery flows
- system-level evidence that the routing holds

This repository does not make the path-universal claim.

### Reading guide

- If you want to inspect the gate primitive: read `src/commit_gate_core/gate.py`
  and the test suite.
- If you want to evaluate path-universal coverage in a real system: that
  is a deployment-architecture review, not a code review of this repo.

---

## Execution Boundary Test v1

Use the test to check whether a system can physically stop consequence at the point an action would become real.

See: [`docs/execution-boundary-test-v1.md`](docs/execution-boundary-test-v1.md)

Core question:

> Where does the system physically stop?

PASS:
The action cannot execute without valid proof.

FAIL:
The action still reaches consequence.

---

## Try it in 30 seconds

```bash
git clone https://github.com/LalaSkye/commit-gate-core.git
cd commit-gate-core
python -m examples.unsafe_email_send
```

Expected output:

```text
Result: HOLD
Email sent: false
Receipt written: true
```

If the email sends, the gate is broken.

---

## Enterprise execution readiness packet

A buyer-readable enterprise evidence packet has been added under:

[`enterprise-execution-readiness/`](enterprise-execution-readiness/)

It translates the execution-boundary primitive into an enterprise-readable chain:

```text
policy rule
  -> control requirement
  -> runtime gate
  -> refusal condition
  -> refusal receipt
  -> audit evidence
```

Current packet:

```text
ESP-001 — AI-generated external email attempted without authority_token
Expected result: DENY before send, downstream_send=false, receipt_written=true
Compression: No authority token. No external send. Receipt written.
```

This packet is **not** an enterprise-deployment, certification, compliance, production-readiness, legal-advice, adoption, or path-universal governance claim.

It is a bounded buyer-readable proof surface for one demonstrated scenario.

---

## Enterprise-shaped scenario pack

A bounded synthetic scenario pack has been added under:

[`docs/enterprise-shaped-scenarios/`](docs/enterprise-shaped-scenarios/)

Current scenario:

```text
ESP-001 — AI-generated external email attempted without authority_token
Expected result: DENY before send, downstream_send=false, receipt_written=true
Replay: same refusal class, same missing_field
```

Run it from the repository root:

```bash
python docs/enterprise-shaped-scenarios/run_scenario_001.py
```

This scenario is **not** an enterprise-readiness, deployment, compliance, certification, or production-enforcement claim. It is a bounded synthetic refusal path.

---

## The demo

```text
Attempt:        send external email
DecisionRecord: missing authority
Result:         HOLD
Email sent:     false
Receipt written: true
```

That is the shape.

The system refuses the unsafe state change before execution and writes a receipt proving why.

---

## What this repo proves

- Unsafe consequence can be refused before execution on the demonstrated path.
- Missing authority prevents mutation on the demonstrated path.
- Refusal can produce an auditable receipt when the audit sink accepts the event.
- Bypass failure can be tested directly.

This is not governance commentary.

It is a small enforcement primitive.

---

## Boundary

This repo does **not** claim to be a full AI governance system.

It proves one narrow invariant:

> This path cannot execute without a valid `DecisionRecord`.

The invariant is deliberately small so it can be inspected, tested, and broken under hostile reading.

This repository does not prove adoption, certification, standardisation, production readiness, payload binding, atomic commit, or path-universal deployment coverage.

It demonstrates a bounded execution-control surface that can be run, inspected, and tested.

---

## Core rule

A valid `DecisionRecord` must be:

- signed
- scoped to the exact commit
- within its validity window
- unreplayed
- sufficient for the requested mutation under the current v1 scope checks

Failure at any check produces `HOLD`.

No silent continuation.

---

## Evidence shape

A useful governance gate must show:

1. what action was attempted
2. what proof was required
3. which check failed
4. whether execution occurred
5. what receipt was written

For this demo, the answer is simple:

```text
Execution occurred: false
Receipt written:    true
Verdict:            HOLD
```

## Refusal receipt

When the gate returns `DENY` or `HOLD`, it writes a refusal receipt.

The receipt is not silence. It is a structured record of what was stopped, why, and whether state changed.

`DENY` is a first-class outcome. It is not the absence of `ALLOW`.

A valid payload does not authorise an action.

See: [`docs/refusal-receipt-v0.1.md`](docs/refusal-receipt-v0.1.md)

Example: [`examples/clean-payload-denied-action.json`](examples/clean-payload-denied-action.json)

---

## Status

`v0.1` — one narrow invariant, enforced on the demonstrated path.

Small surface. Clear failure mode. Receipts over reassurance.

---

## Working paper

**From Policy to Commit: Execution-Boundary Control for Governed AI Systems**

- DOI: https://doi.org/10.5281/zenodo.19980275
- Zenodo record: https://zenodo.org/records/19980275
- PDF (in this repo): [docs/papers/From_Policy_to_Commit_Ricky_Dean_Jones_AlvianTech_Working_Paper_v0.1.pdf](docs/papers/From_Policy_to_Commit_Ricky_Dean_Jones_AlvianTech_Working_Paper_v0.1.pdf)

### Citation

Jones, R. D. (2026). *From Policy to Commit: Execution-Boundary Control for Governed AI Systems* (v0.1). Zenodo. https://doi.org/10.5281/zenodo.19980275

---

## License

MIT. Use it. Break it. Tell me how.
