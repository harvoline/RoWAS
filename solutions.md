# Solutions Log

Detailed record of significant technical problems and the reasoning behind
their solutions. This file preserves *why*, not just *what*.

---

## 1. Establishing the Engineering Foundation for an Empty Repository

### Problem

The repository contained nothing but an empty initial commit. No language,
framework, structure, or tooling existed. A production-oriented CLI
application needs to be built incrementally on top of a foundation that
supports TDD, disciplined git workflow, and clear documentation — but that
foundation didn't exist yet.

### Context

The project owner's process specification explicitly forbids implementing
business functionality before the foundation is established and approved,
and explicitly forbids assuming a technology stack when it "cannot
reasonably be inferred."

### Requirements

- A working, verified project skeleton (not just files that look right —
  actually installable and runnable).
- Test, lint, and type-check tooling wired up and passing.
- A documentation system covering context, tool usage, technical decisions,
  application workflow, git workflow, testing strategy, rules, and
  documentation process itself.
- No business logic.
- CI/CD explicitly deferred, recorded as an open decision.

### Constraints

- Cannot infer the programming language — this materially affects
  architecture, testing framework, and tooling, so it required asking
  rather than assuming.
- The repository is empty, so there were no existing conventions to
  discover and follow; conventions had to be established from scratch and
  justified.

### Analysis

Considered stacks: TypeScript/Node.js, Python, Java, C#. Each is a
reasonable choice for a rules-heavy terminal application; none could be
confidently inferred from the (empty) repository. Presented as a choice
rather than picking one, per the instruction to ask when a decision
materially affects architecture. **Decision: Python**, made by the project
owner.

Within Python, considered:

- **Flat vs. src-layout package structure.** Src-layout was chosen: it
  prevents a common footgun (tests accidentally importing the local
  directory instead of the installed package), which matters for keeping
  test results trustworthy — directly serves the "correctness" and
  "testability" priorities in the project's stated assessment criteria.
- **Poetry/PDM/hatchling vs. setuptools for packaging.** setuptools was
  chosen: it is bundled with virtually every Python installation and pip,
  needs no extra tool to learn, and the project's own rules explicitly say
  to avoid unnecessary dependencies. Poetry/PDM would add a second
  dependency-resolution tool for no benefit at this stage (no complex
  dependency graph exists yet).
- **Whether to add lint/type-check tooling now versus later.** Added now:
  the project's stated assessment criteria include "code structure and
  maintainability" and "production readiness" from the start, and
  retrofitting `mypy --strict` onto untyped code later is materially more
  expensive than writing typed code from the first line. ruff was chosen
  over separate flake8+black+isort because it is one dependency instead of
  three, with equivalent coverage.

### Delegation

No sub-tasks were delegated to other agents — the foundation work is small
enough, and requires enough continuity of context (the language decision
affects every subsequent file), to do directly.

### Decision

- Language: **Python >= 3.10** (owner decision).
- Layout: **src-layout**, package name `robot_allocation`.
- Build backend: **setuptools**.
- Dev tooling: **pytest + pytest-cov, ruff, mypy(strict)**.
- CLI entry point exists (`cli.py`) but contains no business logic — only a
  placeholder banner — to respect the explicit "do not implement business
  logic yet" instruction while still proving the scaffolding is real and
  runnable.

### Reasoning

Every tool choice above is justified by a stated project priority
(maintainability, testability, avoiding unnecessary dependencies) rather
than by default/habit. The CLI placeholder was added specifically because a
*silent, untested* scaffold would violate "never claim a test/build
succeeded unless it was actually executed and verified" — there had to be
something real to run and test.

### Implementation Order

1. Write failing test for the CLI entry point (RED).
2. Add `pyproject.toml`, `.gitignore`, package skeleton (`cli.py`,
   `__init__.py`).
3. Implement minimal `cli.py` to pass the test (GREEN).
4. Verify for real: build a virtualenv, install in editable mode, run
   pytest/ruff/mypy, confirm all pass.
5. Write the documentation set, referencing the now-verified decisions.
6. Commit in logically separated commits (scaffolding, then docs).

### Trade-offs

- **Pro:** minimal dependency footprint, standard/boring tooling choices
  that any Python developer will recognise immediately, strict typing from
  day one avoids expensive retrofitting.
- **Con:** `mypy --strict` adds friction for every future contributor —
  every function needs full type annotations. Accepted because the
  project's stated priority order is "correctness -> maintainability ->
  testability -> clarity -> production readiness," and strict typing
  directly serves the first two.
- **Con:** no CI/CD yet means these checks (`pytest`, `ruff`, `mypy`) are
  only enforced if a developer remembers to run them locally. This is a
  known, accepted gap until the CI/CD checkpoint (see `rules.md`) is
  resolved.

### Result

A verified, minimal Python project skeleton: `pyproject.toml` (setuptools,
src-layout, pytest/ruff/mypy config), `src/robot_allocation/{__init__.py,
cli.py}`, `tests/test_cli.py`. Confirmed working end-to-end: `pytest` (1
passed), `ruff check .` (all checks passed), `mypy src` (no issues, strict
mode). Full documentation set written alongside it.

### Future Considerations

- The `strict = true` mypy setting may need per-module relaxation if a
  future dependency lacks type stubs — deal with that when it happens
  rather than pre-emptively loosening it now.
- The CLI placeholder in `cli.py` must be replaced (not just extended) once
  real input/output requirements arrive — it is scaffolding, not a
  foundation to build features on top of untouched.
- Package name `robot_allocation` was chosen for clarity; if the project
  owner has a preferred naming convention (e.g. matching a future company
  monorepo), this is cheap to rename now and expensive later.

---

## 2. Diagnosing the DevSwarm Git/WSL Environment Mismatch

### Problem

Every native (Windows Git Bash) `git` command failed with `fatal: not a
git repository: /var/www/rows/.git/worktrees/initial-setup` — a Linux path
that does not exist on Windows. This blocked the very first step of the
process (inspecting existing git state).

### Context

This repository is managed by DevSwarm (`hivecontrol`), which — per its own
CLI output — expected a `claude-wsl` agent, i.e. it assumed git operations
would happen inside WSL, not a native Windows shell.

### Requirements

Confirm whether this indicated actual repository corruption (requiring
recovery) or an environment/tooling mismatch (requiring a different
invocation method).

### Constraints

Must not attempt destructive git recovery operations without being certain
of the root cause first (per safety rules).

### Analysis

1. Compared this repository's `.git` pointer file against four sibling
   DevSwarm repositories on the same machine — all four showed the
   identical pattern (`gitdir: /var/www/<project>/.git/worktrees/<branch>`),
   ruling out one-off corruption.
2. Confirmed a real WSL distribution (`Ubuntu-20.04`) is installed and
   running (`wsl.exe -l -v`).
3. Confirmed the referenced path exists inside WSL and contains real git
   worktree metadata (`HEAD`, `index`, `logs`, `refs`).
4. Confirmed the worktree's `gitdir` file points back to
   `/mnt/c/Users/Afif/.devswarm/repos/2/dfb88366/initial-setup/.git` — the
   same directory, reachable from WSL via its `/mnt/c/...` mount. This is a
   standard, correctly-formed git worktree cross-reference; the only issue
   is that Windows-native git cannot resolve the Linux-side half of it.
5. Verified the fix by running `git status`/`git log` from inside WSL
   against the `/mnt/c/...` path — worked immediately, showed the true
   repository state (one empty "Initial commit," no remote, current branch
   `initial-setup` off `main`).

### Delegation

Not applicable — single diagnostic thread.

### Decision

All git operations in this workspace must be issued via WSL
(`wsl.exe -d Ubuntu-20.04 -- bash -c "cd /mnt/c/... && git ..."`), never via
native Windows git. File edits (non-git) work fine from either side since
it's the same underlying filesystem.

### Reasoning

The repository is not corrupted; it is a correctly functioning git
worktree whose two halves live in different OS environments that only WSL
can bridge. Changing invocation method costs nothing and is fully
reversible; attempting to rewrite the `.git` pointer files would be a
destructive, unnecessary risk to working infrastructure.

### Implementation Order

Diagnose -> confirm via sibling repos -> confirm WSL bridges both paths ->
adopt WSL as the git invocation method -> document in `CLAUDE.md` and
`rules.md` so future sessions don't re-diagnose this from scratch.

### Trade-offs

**Con:** every git command in this project now requires wrapping in a
`wsl.exe` invocation, which is a small amount of friction and an
easy-to-forget detail for a future contributor unfamiliar with DevSwarm.
Mitigated by documenting it prominently in `CLAUDE.md`, `rules.md`, and
`README.md`.

### Result

Git operations work reliably for the remainder of this session and future
sessions, without any change to the repository itself.

### Future Considerations

If this workspace is ever migrated off DevSwarm or the WSL distribution
changes, this constraint should be re-verified and the documentation
updated or removed accordingly.
