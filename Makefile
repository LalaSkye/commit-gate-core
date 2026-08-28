# commit-gate-core — inspection entry points for the authorize-only kernel.
# Packaging only. These targets do not add capability claims.

PYTHON ?= python3

.PHONY: help install install-dev demo test adversarial verify clean

help:
	@echo "install      Install the package (editable)"
	@echo "install-dev  Install the package plus test dependencies"
	@echo "demo         Run the authorize-only refusal example (payload_bytes, no apply)"
	@echo "test         Run the collected test suite"
	@echo "adversarial  Run the adversarial invariant verifier"
	@echo "verify       demo + named authorize regressions + full suite + adversarial"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

demo:
	PYTHONPATH=src $(PYTHON) -m examples.authorize_only_refuse

test:
	$(PYTHON) -m pytest tests enterprise-execution-readiness/tests

adversarial:
	$(PYTHON) scripts/verify_adversarial_invariants.py

verify: demo
	PYTHONPATH=src $(PYTHON) -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
	$(PYTHON) -m pytest tests enterprise-execution-readiness/tests
	$(PYTHON) scripts/verify_adversarial_invariants.py

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
