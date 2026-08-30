# INVARIANTS

**Status:** ARCHITECTURE CANDIDATES / NOT ESTABLISHED BY THIS KERNEL

These statements are preserved as wider design candidates. The current
`0.2.0a1` public object establishes only payload-bound authorisation on its
tested in-process path. It does not apply payloads or enforce these invariants
against external execution routes.

## INVARIANT I — Scope Monotonicity

At every delegation hop, the delegate authority envelope must be a subset of or equal to the delegator authority envelope.

## INVARIANT II — Cross-Surface Admissibility

No action may proceed to execution if active interpretive surfaces produce mutually incompatible verdicts.

## INVARIANT III — Consequence Binding

No unresolved interpretive state may bind directly into execution.
