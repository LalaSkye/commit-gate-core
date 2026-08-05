"""Path setup for the enterprise-shaped scenario tests.

`adapters/commit_gate_bridge.py` imports `commit_gate_core.gate` from the
repository's `src/` directory. When these tests are run without an editable
install — which is what CI does — `src/` is not on `sys.path` and collection
fails with ModuleNotFoundError.

This mirrors the existing pattern in the repository root `tests/conftest.py`.
No package installation is assumed.

Recorded 2026-08-05.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = _REPO_ROOT / "src"

if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))
