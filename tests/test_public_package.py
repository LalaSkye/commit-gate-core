from __future__ import annotations

from commit_gate_core import CommitGate, GateResult, __version__
from commit_gate_core.scenario_runner import run_scenario_001


def test_public_package_exports_core_types() -> None:
    assert CommitGate.__name__ == "CommitGate"
    assert GateResult.__name__ == "GateResult"
    assert __version__ == "0.1.0"


def test_installed_scenario_fixture_is_available() -> None:
    result = run_scenario_001()

    assert result["verdict"] == "DENY"
    assert result["downstream_send"] is False
