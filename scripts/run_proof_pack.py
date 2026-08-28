"""Retired Proof Pack v0.1 entry point.

The original runner exercised the pre-Shape A mutation-facing executor with a
synthetic ``sig_valid`` verifier. That surface is not the authorize-only kernel
on ``main``. This retained entry point fails closed: it does not invoke the
gate, load fixtures, or write receipts.
"""

from __future__ import annotations


MESSAGE = """Proof Pack v0.1 is retired and was not run.

Current authorize-only inspection command:
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q

No gate call was made and no receipt was written.
"""


def main() -> int:
    print(MESSAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
