# ALVIANTECH — Admissible Claim Register v1.0

**Status:** HISTORICAL / SUPERSEDED

**Class:** NON-CANONICAL POSITIONING RECORD

**Scope:** Preserved history only

**Purpose:** Record an earlier positioning proposal without granting it current claim authority.

## Successor boundary — 2026-08-30

This register does not govern the current public claim for
`commit-gate-core`. It contains architecture and market-positioning proposals
that are not established by the authorize-only kernel.

The active repository claim is narrower:

> The unreleased `0.2.0a1` kernel binds exact payload bytes to a
> DecisionRecord and returns authorisation or refusal. It does not apply the
> payload.

No sentence below may be used as evidence that this repository prevents
external execution, implements the wider AlvianTech architecture, is unique in
the field, or has production standing. See the root `CLAIM_BOUNDARY.md`.

---

## Field acknowledgement

The field is not empty.

Runtime governance, delegation, audit trails, deterministic gates, and admissibility language are active areas of work. ALVIANTECH public material must not claim that nobody is building runtime agent governance or execution gating.

Historical proposed comparison shape — **not currently admissible from this
repository**:

> No current product or public artefact appears to combine delegated authority, scope monotonicity, closed typed exits, cross-surface contradiction testing, sealed receipts, and a fail-closed execution boundary as one commit-boundary primitive.

This is a bounded comparison claim, not an exclusivity claim.

---

## Historical proposed core invariant

> **No unresolved interpretive state may bind directly into execution.**

This is the spine.

It is intended as an executable invariant, not a philosophical claim.

---

## Historical proposed positioning sentence

> ALVIANTECH builds runtime admissibility infrastructure for delegated AI systems, preventing unresolved interpretive states from binding into executable consequence.

---

## Distinct surface

The defensible ALVIANTECH surface is the combination of:

1. **Delegated authority** — authority is traceable from a root human authority through a bounded chain.
2. **Scope monotonicity** — delegated authority may narrow, but must not silently widen.
3. **Closed typed exits** — `ALLOW`, `HOLD`, `DENY`, `SILENCE` are controlled governance outcomes.
4. **Cross-surface contradiction testing** — active interpretive surfaces must remain structurally compatible before consequence is allowed.
5. **Sealed receipts** — decisions produce inspectable evidence of what was attempted, checked, and returned.
6. **Fail-closed execution boundary** — unresolved state blocks consequence.

The wedge is not generic agent governance.

The wedge is:

> **Cross-surface structural contradiction as a pre-execution admissibility gate.**

---

## Machine-testable invariants

### Invariant I — Scope Monotonicity

At every delegation hop, the authority envelope of the delegate must be a subset of or equal to the authority envelope of the delegator.

No delegation hop may expand scope.

### Invariant II — Cross-Surface Admissibility

No action may proceed to execution if active interpretive surfaces produce mutually incompatible verdicts.

Cross-surface contradiction produces `HOLD` unless a surface returns `DENY`, in which case the result is `DENY`.

### Invariant III — Consequence Binding

No unresolved interpretive state may bind directly into execution.

An unresolved state, where the contradiction engine cannot determine cross-surface compatibility, produces `SILENCE`.

`SILENCE` fails closed.

---

## Forbidden public claims

Do not claim:

- consciousness detection
- AGI
- emotional AI
- therapy or clinical application
- complete semantic understanding
- that nobody is building runtime governance
- that ALVIANTECH is the only governance primitive
- production readiness unless separately demonstrated
- certification, compliance, adoption, or standardisation unless independently evidenced

---

## Historical proposed claim territory — not active

The following phrases are admissible when used with appropriate scope boundaries:

- bounded detection-and-prevention architecture at the pre-execution boundary
- runtime admissibility infrastructure for delegated AI systems
- typed pre-execution contradiction engine
- cross-surface structural contradiction as a pre-execution admissibility gate
- no current product appears to combine the six properties as one commit-boundary primitive
- runtime constitutional layer, as metaphor only
- admissibility substrate, with prior-art acknowledgement where relevant
- consequence-binding control system

---

## Addendum A — Public Surface Rule v1.0

**Status:** HISTORICAL / SUPERSEDED
**Class:** POSITIONING_CONTROL  
**Purpose:** Prevent conceptual overload by assigning one primary mechanism to each public surface.

### Core risk

Conceptual overload collapses the spine.

### Spine

> No unresolved interpretive state may bind directly into execution.

### Rule

Do not explain the entire lattice on any single surface.

Each surface earns the next one.

### Surface assignment

| Surface | Primary mechanism | Keep off |
| --- | --- | --- |
| README | Delegated admissibility + typed exits | Full contradiction-engine theory; full receipt architecture; full delegation-chain formalism; standards positioning |
| Paper | Cross-surface contradiction engine | Product language; full receipt design; full delegation-chain implementation; marketing claims |
| Demo | Scope monotonicity + receipts | Coherence-surface theory; full positioning language; public-category claims; whole-system explanation |
| Standards submission | Formal invariants only | Product language; brand language; metaphor; narrative framing |

### Controlled observations

1. Boundaries became inspectable.
2. Frozen typed exits change category from application behaviour to governance primitive.
3. Neighbouring work must be described accurately, not territorially.

### Claim discipline

Everything in the lattice is evidence for the spine.

The spine is not evidence for the lattice.

### Forbidden move

Do not use one surface to prove the entire system.

---

## Controlled vocabulary

`ALLOW`, `HOLD`, `DENY`, `SILENCE`, `EXIT_ENUM`, `SCOPE_MONOTONICITY`, `DecisionRecord`, `receipt`, `admissibility`, `commit boundary`, `execution boundary`, and `cross-surface` are controlled terms.

No synonym substitution in public-facing governance material.

No runtime extension of `EXIT_ENUM`.

Frozen until formal human-authority revision.

---

## Governance note

Any public-facing document that departs from this register, including overclaim in marketing material or underclaim in standards submissions, must be flagged for governance review before publication.

Humour may decorate the control surface.

It may not mutate the governance rule.
