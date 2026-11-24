This guide tests commit 610d155232fbc3f590ed40656e48403ef4d20dcf (authorise-only candidate). It does not apply to release v0.1.1.

# Reproduce the authorise-only tests

The **guide revision** is the commit that adds this file (the PR head SHA).
The **tested revision** is the pinned SHA above. Record both; do not substitute
the guide revision for the tested revision.

## Keep the guide open

Open `REPRODUCE.md` from the PR in a browser tab and leave it open. Use a
separate terminal and a fresh temporary directory for the tested checkout.
The checkout is detached at the tested SHA; it is not the PR branch.

## Prerequisites and sources

Use Python 3.11 or later. `pyproject.toml` at the pinned revision declares
`requires-python = ">=3.11"` and the `dev` extra `pytest>=8.0`
([Python and test dependency](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/pyproject.toml#L10),
[dev dependency](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/pyproject.toml#L29-L30)).
`requirements-dev.txt` also specifies `pytest>=8.0`
([lines 1-2](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/requirements-dev.txt#L1-L2)).

The pinned Package workflow uses Python 3.11, installs with
`python -m pip install --upgrade build pytest`, then runs
`python -m pytest -q`
([CI lines 18-27](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/.github/workflows/package.yml#L18-L27)).
This guide uses that install command and the narrower README authorise-only
test command
([README lines 65-75](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L65-L75)).

**Do not use the README's “Install-from-tag” line.** It installs `v0.1.1`,
which the README itself says is not evidence for this kernel
([README lines 77-85](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L77-L85)).

## macOS or Linux

In a new terminal, set up a disposable checkout and virtual environment outside
the PR worktree:

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

The first `git rev-parse HEAD` must print the pinned SHA. The status check must
be empty. Keep the temporary path so you can report the run environment and
versions.

## Windows PowerShell

Run in a new PowerShell terminal. The test checkout and virtual environment
are separate from the PR worktree:

```powershell
$target = "610d155232fbc3f590ed40656e48403ef4d20dcf"
$testRoot = Join-Path $env:TEMP ("commit-gate-repro-" + [guid]::NewGuid().ToString("N"))
$repo = Join-Path $testRoot "repo"
$venv = Join-Path $testRoot "venv"
New-Item -ItemType Directory -Path $testRoot | Out-Null
git clone --no-checkout https://github.com/LalaSkye/commit-gate-core.git $repo
git -C $repo fetch origin $target
git -C $repo checkout --detach $target
$actual = (git -C $repo rev-parse HEAD).Trim()
if ($actual -ne $target) { throw "Expected $target, got $actual" }
if ((git -C $repo status --porcelain) -ne "") { throw "Checkout is not clean" }
git -C $repo rev-parse HEAD
python -m venv $venv
$python = Join-Path $venv "Scripts\python.exe"
& $python --version
& $python -m pip install --upgrade build pytest
& $python -m pip show build pytest
Push-Location $repo
$env:PYTHONPATH = "src"
& $python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
$testExit = $LASTEXITCODE
Pop-Location
if ($testExit -ne 0) { exit $testExit }
```

The first `git rev-parse HEAD` must print the pinned SHA. The status check must
be empty. Keep the temporary path so you can report the run environment and
versions.

## Claim boundary

The README at the pinned revision states:

> This object does not claim production readiness, enterprise deployment,  
> compliance, certification, path-universal enforcement, crash-safe durable  
> nonces, atomic PREPARED+nonce persistence, or that consequence cannot occur  
> outside this process.
>
> It does not claim that Ed25519 is implemented.  
> It does not claim certificates or algorithm agility.  
> It does not claim that the lab MAC is a signature.  
> It does not claim that `start-here` is this kernel.  
> It does not claim that GitHub Latest is this tree.

Source: [README lines 87-99 at the tested revision](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/README.md#L87-L99).

## Return receipt

Copy and complete this from the actual run. Do not infer totals or expected
versions. Include the guide revision from the PR separately from the detached
tested SHA.

```text
Guide revision (PR head SHA):
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

The run in the repository owner's environment is an internal repeat, not an
independent reproduction. Independent reproduction requires an outside
reviewer to run the same pinned revision in their own environment and return
their own evidence.
