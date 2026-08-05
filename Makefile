# commit-gate-core — inspection and verification entry points.
# Packaging only. These targets do not add capability claims.

PYTHON ?= python3

.PHONY: help install install-dev demo test adversarial verify clean

help:
	@echo "install      Install the package (editable)"
	@echo "install-dev  Install the package plus test dependencies"
	@echo "demo         Run the 30-second refusal demonstration"
	@echo "test         Run the test suite"
	@echo "adversarial  Run the adversarial invariant verifier"
	@echo "verify       demo + test + adversarial, in order"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

demo:
	$(PYTHON) -m examples.unsafe_email_send

test:
	$(PYTHON) -m pytest

adversarial:
	$(PYTHON) scripts/verify_adversarial_invariants.py

verify: demo test adversarial

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
