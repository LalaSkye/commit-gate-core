# experimental/

Not part of the installable `commit_gate_core` package.
Not exported. Not a durable ledger.

`two_phase.py` is the PR #30 lab executor. It still contains an arbitrary
`mutation_callback`. Do not import it from production code.
