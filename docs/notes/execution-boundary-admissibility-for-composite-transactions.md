Technical Note — Execution-Boundary Admissibility for Composite Transactions
Ricky Jones / AlvianTech / TrinityOS — 14 May 2026

Distributed transaction protocols already handle important parts of the commit problem.

Two-phase commit asks whether participants can agree to commit or abort. Its prepare phase asks each node whether it can promise to carry out the update, and its commit phase carries the update out.

Paxos Commit improves the fault-tolerance of the commit decision. Gray and Lamport describe classic two-phase commit as the special case of Paxos Commit with zero coordinator faults tolerated; Paxos Commit generalises transaction commit by running consensus over commit or abort decisions.

Saga patterns solve a different problem: coordinating work across distributed services and compensating when one step fails. Microsoft describes Saga as a pattern for maintaining data consistency across services, with compensating transactions used to undo work when an eventually consistent operation fails.

Those mechanisms are useful.

But they do not, by themselves, produce an execution-boundary admissibility proof.

They can record that a transaction committed, aborted, retried, compensated, or reached agreement.

They do not necessarily prove that, at the moment of binding:

authority was fresh
canonical state was current
the proposed transition remained admissible
dependent sub-transitions still preserved the required invariant
refusal occurred before mutation where admissibility failed

That is the missing governance layer.

A composite proposal may decompose into several governed sub-transitions. Each sub-transition may appear locally valid. But the proposal as a whole may become inadmissible if the dependency structure no longer holds at bind time.

For example:

proposal:
  deploy billing update

sub-transitions:
  schema migration
  authorization model update
  reconciliation logic update
  API contract update

If the schema migration binds while the authorization update fails and the API contract partially changes, the system may reach a state that is transactionally recorded but governance-invalid.

The commit record says what happened.
The admissibility receipt must say why it was allowed to happen — or why it was refused before mutation.

This is the execution-boundary claim:

Governance for composite transactions requires a proof object generated at bind time, not merely a commit outcome, compensation path, or post-hoc audit record.

In TrinityOS terms, the control surface is not only:

prepare → commit / abort

It is:

proposal set
→ decomposition
→ authority check
→ canonical state check
→ dependency admissibility check
→ commit gate
→ allow / refuse / hold
→ receipt
→ audit trail

The receipt is the important object.

For weakly coupled proposals, the receipt may show that a subset was allowed to bind while another sub-transition was refused.

For strongly coupled proposals, the receipt may show that no partial bind was admissible because the dependency set failed as a whole.

Either way, governance is not satisfied by saying the transaction completed.

It must be able to show that the consequence-producing transition was authorised, admissible, and bounded at the moment it crossed into mutation.

Claim boundary

This note does not claim production deployment, standards authority, certification, external audit, or field ownership.

It defines a narrow architectural distinction:

Existing distributed commit and recovery patterns address agreement, consistency, and compensation.

Execution-boundary governance requires an additional admissibility proof layer: a receipt-bearing control surface that proves whether a transition or transition-set was allowed, refused, or held before mutation.

References

Martin Fowler, Two-Phase Commit: https://martinfowler.com/articles/patterns-of-distributed-systems/two-phase-commit.html

Jim Gray and Leslie Lamport, Consensus on Transaction Commit: https://arxiv.org/abs/cs/0408036

Microsoft Azure Architecture Center, Saga design pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga

Microsoft Azure Architecture Center, Compensating Transaction pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
