This guide tests commit 610d155232fbc3f590ed40656e48403ef4d20dcf (authorise-only candidate). It does not apply to release v0.1.1.

## Preparation

Open this guide from the [PR](https://github.com/LalaSkye/commit-gate-core/pull/41/files) or its commit permalink and keep it open while testing. Record the full PR head SHA containing this guide as the **guide revision**; it is distinct from the **tested SHA** below. Do not copy the guide into the test checkout.

Use an existing checkout of this repository with Git, Python 3.11 or newer, pip, and internet access to install the test dependency. The commands below use a separate detached worktree and a virtual environment outside it, leaving the original checkout untouched. If the target object is not present, fetch it first; do not substitute a release tag.

The target's [`requirements.txt`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/requirements.txt#L1-L7) specifies no runtime dependencies; [`requirements-dev.txt`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/requirements-dev.txt#L1-L2) specifies `pytest>=8.0`, not a lockfile. Record the actual installed versions. The target's [`pyproject.toml`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/pyproject.toml#L5-L10) requires Python 3.11 or newer.

## Run

From the root of the existing repository checkout, in a POSIX shell:

```sh
TARGET=610d155232fbc3f590ed40656e48403ef4d20dcf
git cat-file -e "$TARGET^{commit}" || git fetch origin "$TARGET"
TEST_DIR=$(mktemp -d "${TMPDIR:-/tmp}/commit-gate-test.XXXXXX")
VENV_DIR=$(mktemp -d "${TMPDIR:-/tmp}/commit-gate-venv.XXXXXX")
git worktree add --detach "$TEST_DIR" "$TARGET"
cd "$TEST_DIR"
git rev-parse HEAD
test "$(git rev-parse HEAD)" = "$TARGET" || { echo "SHA mismatch"; exit 1; }
git status --porcelain --untracked-files=all
test -z "$(git status --porcelain --untracked-files=all)" || { echo "Checkout is not clean"; exit 1; }
python3 --version
python3 -m venv "$VENV_DIR"
. "$VENV_DIR/bin/activate"
python -m pip install -r requirements-dev.txt
python -m pip freeze --all
PYTHONPATH=src python -m pytest tests/test_authorize.py tests/test_beau_failure_classes.py -q
```

The full SHA printed by `git rev-parse HEAD` is the tested SHA; the status output must be empty before installing or testing. The focused command is the named authorise regression step in the target's [`Makefile`](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/Makefile#L31-L33). It selects two files, not the entire suite. The target's [package CI](https://github.com/LalaSkye/commit-gate-core/blob/610d155232fbc3f590ed40656e48403ef4d20dcf/.github/workflows/package.yml#L18-L27) uses Python 3.11, installs pytest and runs `python -m pytest -q` for the broader repository suite.

Record the PR URL and head SHA, guide revision, tested SHA, OS and version, Python version, `pip freeze --all` output, exact commands, test totals, and any mismatch or failure output. Also record who performed the work and which account GitHub shows; do not imply that another person or organisation performed the run. Leave tests unchanged on failure. An AlvianTech repeat and an outside reviewer's independent run are separate, pending evidence unless actually performed.
