# AI Tool Usage Log

Record of meaningful AI-assisted development activity on this project, kept
for transparency and auditability. Not every trivial interaction is logged —
only usage that materially shaped the codebase or a decision.

---

## 2026-09-05 — Foundation Setup

**Tool used:** Claude Code (Claude Sonnet 5), operating per the project's
`CLAUDE.md`-style instructions provided by the project owner.

**Purpose:** Establish the engineering foundation for an empty repository
before any business functionality is implemented — project structure, tech
stack selection, documentation system, testing/lint/type-check tooling, and
process rules.

**Input/context provided:** A detailed process specification (role,
documentation requirements, TDD mandate, git workflow rules, CI/CD deferral
instructions, and an explicit "do not implement business logic yet"
constraint). The repository itself was empty (one empty initial commit, no
files besides an ignored `.claude/settings.local.json`).

**What the tool did:**

1. Inspected the repository and discovered a DevSwarm-specific environment
   issue: the `.git` file is a worktree pointer to a WSL-only path
   (`/var/www/rows`), which native Windows git cannot resolve. Diagnosed by
   comparing against sibling DevSwarm repos (same pattern in all of them,
   ruling out corruption) and confirming via `wsl.exe` that the real git
   history is reachable from WSL. This finding is recorded in `solutions.md`
   and `CLAUDE.md`.
2. Asked the project owner to choose a language/runtime (a decision that
   could not be reasonably inferred and materially affects architecture,
   testing, and tooling). **Result:** Python was selected from a shortlist
   of TypeScript, Python, Java, and C#.
3. Scaffolded a src-layout Python package (`src/robot_allocation/`), a
   pytest test suite, and `pyproject.toml` covering packaging, pytest,
   ruff, and mypy(strict) configuration.
4. Followed TDD for the scaffolding itself: wrote `tests/test_cli.py`
   first, confirmed it could not pass (package did not exist yet), then
   added the minimal `cli.py` implementation.
5. Verified the environment for real: created a virtualenv inside WSL,
   installed the project in editable mode with dev dependencies, and ran
   `pytest`, `ruff check .`, and `mypy src` — all passed (1 test, 0 lint
   issues, 0 type errors). Commands and output were inspected directly, not
   assumed.
6. Wrote the full documentation set required by the project instructions:
   `CLAUDE.md`, `rules.md`, `testing-workflow.md`, `coding-workflow.md`,
   `documentation-workflow.md`, `app-workflow.md`, `solutions.md`, and
   `README.md`.

**Accepted / rejected / modified:** Pending project owner review (this is
the first deliverable of the session). No prior output existed to accept or
reject.

**Limitations / risks discovered:**

- `ensurepip` is not installed in the WSL Ubuntu-20.04 environment, so
  `python3 -m venv` cannot create a venv with pip pre-seeded. Worked around
  using `pip install --python <venv-python> ...` from the already-present
  user-level pip, rather than requesting `sudo apt install
  python3.10-venv` (which would have required a password and a
  system-level change outside this repository's scope). This workaround is
  reproducible but slightly non-standard — a developer setting this up
  fresh on a machine with a normal Python install (with `ensurepip`
  available) will not need it.
- No remote git repository is configured, and CI/CD is explicitly
  undecided — both are flagged as open items rather than resolved by the
  AI, per the project's instruction to defer CI/CD decisions to a later
  checkpoint.

---

## 2026-09-05 — Remote Configuration and PR Creation

**Tool used:** Claude Code, via `gh` CLI (GitHub) and `git`, both invoked
through WSL for the reasons recorded in `solutions.md` §2.

**Purpose:** Wire up the GitHub remote the project owner provided
(`harvoline/RoWAS`), push the foundation work, and open the first PR for
review — while resolving the CI/CD checkpoint along the way.

**What happened:** Verified the remote was reachable and empty before
touching it, confirmed the specific push/PR plan with the owner, then
pushed `main` and `initial-setup` and opened PR #1 via `gh pr create`.

**Limitation/risk discovered:** `gh pr create --body "$(cat <<'EOF' ... EOF)"`
run through a nested `bash -c` (this tool's shell -> `wsl.exe` -> WSL bash)
had its heredoc quoting broken — backtick-wrapped code spans in the PR body
(e.g. `` `pytest` ``) were evaluated as command substitution by an
intermediate shell and silently vanished from the body, and the shell also
tried to execute `pytest`/`ruff`/`mypy` as commands (all "not found", since
they only exist inside the project's venv). **Not accepted as-is** — caught
by reviewing the created PR's actual body via `gh pr view --json body`
rather than trusting the create command's apparent success. **Fixed** by
writing the body to a plain file with the `Write` tool (no shell escaping
involved) and applying it with `gh pr edit --body-file`. Lesson recorded in
`solutions.md`: any multi-line or backtick-containing text destined for a
shell command in this environment should go through a file, not inline
heredoc/quoting, when the command crosses the Windows-shell/WSL boundary.
