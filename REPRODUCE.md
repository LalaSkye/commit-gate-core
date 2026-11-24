# Reproduce the authorise-only tests

**Tested commit:** `610d155232fbc3f590ed40656e48403ef4d20dcf`<br>
**Scope:** Unreleased authorise-only candidate. Release `v0.1.1` is an earlier, callback-capable version and falls outside this guide.

Record two SHAs in your receipt:

- **Tested SHA:** the commit above.
- **Guide revision:** the commit SHA in the permalink of the guide you actually read.

Keep the guide permalink open while you test the pinned commit in a separate checkout.

## At a glance

| Step | What to do |
|---|---|
| 1 | Check the prerequisites. |
| 2 | Run the commands for your platform. |
| 3 | Fill in the receipt and send it back. |

| Platform | Evidence |
|---|---|
| Linux | Reported run: 12 passed at `610d155`. |
| macOS | Untested. |
| Windows PowerShell | Untested. |

## 1. Prerequisites

- **Python 3.11 or later**, as specified in [`pyproject.toml`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/pyproject.toml#L10).
- **Git** and network access to GitHub and the package index used by pip.
- The commands install the test dependencies. The project specifies **pytest 8.0 or later** in [`pyproject.toml`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/pyproject.toml#L29-L30) and [`requirements-dev.txt`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/requirements-dev.txt#L1-L2).

The install step follows the pinned [Package workflow](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/.github/workflows/package.yml#L18-L27). Dependency versions may vary between runs. Record the versions installed in your receipt.

Each block creates a fresh temporary checkout, verifies the full SHA and checks that the working tree is clean. It then runs the two authorise-only test files named in the [pinned README](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L65-L75).

Skip the README’s [install-from-tag command](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L77-L85). It installs `v0.1.1`.

## 2a. Linux or macOS

**Reported Linux run:** 12 passed at `610d155`. **macOS:** untested.

```bash
set -eu
target=610d155232fbc3f590ed40656e48403ef4d20dcf
test_root="$(mktemp -d)"
git clone --no-checkout https://github.com/LalaSkye/commit-gate-core.git "$test_root/repo"
git -C "$test_root/repo" fetch origin "$target"
git -C "$test_root/repo" checkout --detach "$target"
test "$(git -C "$test_root/repo" rev-parse HEAD)" = "$target"
test -z "$(git -C "$test_root/repo" status --porcelain)"
git -C "$test_root/repo" rev-parse HEAD
python3 -m venv "$test_root/venv"
. "$test_root/venv/bin/activate"
python --version
python -m pip install --upgrade build pytest
python -m pip show build pytest
cd "$test_root/repo"
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

If setup stops before pytest runs, record the step and its exact message.

## 2b. Windows PowerShell

**Windows:** untested.

If `python` resolves to the wrong version and you have both the Windows Python launcher and Python 3.11 installed, use `py -3.11 -m venv $venv` for the virtual environment creation step. Record the exact command you used.

```powershell
$ErrorActionPreference = "Stop"
$target = "610d155232fbc3f590ed40656e48403ef4d20dcf"
$testRoot = Join-Path $env:TEMP ("commit-gate-repro-" + [guid]::NewGuid().ToString("N"))
$repo = Join-Path $testRoot "repo"
$venv = Join-Path $testRoot "venv"
New-Item -ItemType Directory -Path $testRoot | Out-Null
git clone --no-checkout https://github.com/LalaSkye/commit-gate-core.git $repo
if ($LASTEXITCODE -ne 0) { throw "git clone failed with exit code $LASTEXITCODE" }
git -C $repo fetch origin $target
if ($LASTEXITCODE -ne 0) { throw "git fetch failed with exit code $LASTEXITCODE" }
git -C $repo checkout --detach $target
if ($LASTEXITCODE -ne 0) { throw "git checkout failed with exit code $LASTEXITCODE" }
$actual = (git -C $repo rev-parse HEAD)
if ($LASTEXITCODE -ne 0) { throw "git rev-parse failed with exit code $LASTEXITCODE" }
$actual = $actual.Trim()
if ($actual -ne $target) { throw "Expected $target, got $actual" }
$worktreeStatus = git -C $repo status --porcelain
if ($LASTEXITCODE -ne 0) { throw "git status failed with exit code $LASTEXITCODE" }
if ($worktreeStatus) { throw "Checkout is not clean" }
git -C $repo rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw "git rev-parse failed with exit code $LASTEXITCODE" }
python -m venv $venv
if ($LASTEXITCODE -ne 0) { throw "python -m venv failed with exit code $LASTEXITCODE" }
$python = Join-Path $venv "Scripts\python.exe"
& $python --version
if ($LASTEXITCODE -ne 0) { throw "python --version failed with exit code $LASTEXITCODE" }
& $python -m pip install --upgrade build pytest
if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit code $LASTEXITCODE" }
& $python -m pip show build pytest
if ($LASTEXITCODE -ne 0) { throw "pip show failed with exit code $LASTEXITCODE" }
Push-Location $repo
$env:PYTHONPATH = "src"
& $python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
$testExit = $LASTEXITCODE
Pop-Location
if ($testExit -ne 0) { exit $testExit }
```

If setup stops before pytest runs, record the step and its exact message.

## 3. Return receipt

Copy this receipt and record what actually happened. Use “unknown” for any field you cannot establish.

```text
Guide revision (commit SHA from the guide permalink):
Tested SHA:
OS and version:
Python version:
pip version:
build version:
pytest version:
Exact commands:
Tests passed:
Tests failed:
Other test totals / skipped:
Mismatch or failure (quote exactly, or “none”):
```

## What a pass shows

A pass records the outcome of the two documented test files at the pinned commit on your platform. The [pinned README’s claim boundary](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L87-L99) applies in full.

## Who ran it matters

- An **internal repeat** is a run by the repository owner or tools working for them.
- An **independent reproduction** is a run of the same pinned commit by an outside reviewer in their own environment, with their own receipt.

If that’s you, thank you. Your receipt is the evidence.
