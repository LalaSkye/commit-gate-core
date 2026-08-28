from __future__ import annotations

from importlib.util import find_spec

import commit_gate_core


def test_two_phase_is_not_a_package_module() -> None:
    assert find_spec("commit_gate_core.two_phase") is None


def test_root_does_not_export_two_phase() -> None:
    assert not hasattr(commit_gate_core, "TwoPhaseCommit")
    assert "TwoPhaseCommit" not in getattr(commit_gate_core, "__all__", [])
