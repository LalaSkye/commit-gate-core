"""Commit gate kernel.

v1 `execute` is deprecated as an executor. It no longer invokes
mutation_callback. The promoted path is `authorize` in authorize.py.

Invariant:
    Authorisation does not mutate the world.
"""
