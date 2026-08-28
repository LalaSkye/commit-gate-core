# Historical mutation contract — NOT the supported API

These notes describe v1 `CommitGate.execute` when it invoked `mutation_callback`.
That behaviour is forbidden on the public kernel.

Do not collect this directory in pytest `testpaths`.
Do not treat files here as the supported contract.

Supported proofs live in `tests/test_beau_failure_classes.py`:
- execute cannot mutate
- commit_hash-only calls fail closed
- payload binding occurs inside authorize
- audit failure leaves the world unchanged
