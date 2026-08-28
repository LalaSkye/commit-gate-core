# Shape A — authorise, do not mutate

PR #30 proved an honest exit for one audit-failure path.
It is not the replacement kernel because `apply` still holds an arbitrary callback.

Successor cut:

- Public path: `CommitGate.authorize(record, payload_bytes, ...)`
- The gate hashes `payload_bytes` itself. A caller-supplied hash that does not match is `DENY:PAYLOAD_HASH_MISMATCH`.
- `execute` no longer invokes `mutation_callback`.
- `TwoPhaseCommit.apply` is not exported.
- Version is `0.2.0a1`.
- Tickets are still in-memory. Do not persist them until mutation is gone from every public path.
- `COMMITTED` is reserved for an executor that can observe the world.
