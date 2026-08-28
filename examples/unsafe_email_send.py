"""Removed. Use examples.authorize_only_refuse.

This module name is kept only so an old `python -m examples.unsafe_email_send`
command fails closed with an explicit message instead of implying HOLD+send.
"""

raise SystemExit(
    "examples.unsafe_email_send has been retired. "
    "Use: PYTHONPATH=src python -m examples.authorize_only_refuse"
)
