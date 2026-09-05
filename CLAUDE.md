# CLAUDE.md — Project Context

This file is the living context document for anyone (human or AI) working on
this repository. Read it before making changes. Update it whenever a
project-level decision or convention changes.

## Project Overview

**EverBot Solutions — Robot Working Allocation System.**

A terminal-based (CLI) application that allocates work to robots according to
business rules. The application reads input from the terminal, applies
allocation rules, and produces output. There is no GUI and no persistent
server component.

**Current state:** foundation only. No allocation business logic has been
implemented. Requirements will be provided progressively by the project owner.

## Domain Context

The business domain (robot allocation rules, constraints, priorities, robot
capabilities, work-item modelling, etc.) has **not yet been specified**. Do
not invent domain rules ahead of requirements — this repository intentionally
contains no assumptions about what "allocation" means beyond "assign work to
robots."

## Technology Stack

- **Language:** Python >= 3.10 (chosen by project owner from a shortlist of
  TypeScript/Python/Java/C# during foundation setup; verified available
  version in the dev environment is 3.10.12).
- **Packaging:** `pyproject.toml`, setuptools backend, **src-layout**
  (`src/robot_allocation/`).
- **Testing:** pytest + pytest-cov.
- **Linting/formatting:** ruff.
- **Type checking:** mypy, `strict = true`.

### Why these specific tools (not just "Python")

- **src-layout** over flat-layout: prevents accidentally importing the
  package from the working directory instead of the installed version —
  catches packaging mistakes early. Standard modern practice.
- **ruff** instead of separate flake8/black/isort: one fast dependency
  covers linting and import ordering; less tooling surface to maintain.
- **mypy strict** from day one: cheaper to keep strict typing discipline
  from the start of a business-rules-heavy system than to retrofit it later.
- **setuptools** (not Poetry/hatchling/PDM): ubiquitous, no extra build-tool
  dependency to learn — deliberate choice to avoid unnecessary tooling per
  project rules.

These are documented as **decisions**, not facts handed down by the project
owner — see [`solutions.md`](solutions.md) for the full reasoning, and
challenge them if requirements change.

## Architecture Overview

```
src/robot_allocation/
    __init__.py
    cli.py          # entry point ONLY — no business logic
tests/
    test_cli.py     # mirrors src/ structure
```

**Principle (not yet exercised, but binding once business logic exists):**
CLI/input-output concerns must stay separate from domain/business logic.
Domain logic must be testable without going through the terminal interface.
Validation is a separate concern from processing.

## Important Conventions

- One feature or fix per branch, branched from `main`. Never commit feature
  work directly to `main`.
- TDD is the default workflow: write a failing test, implement the minimum
  to pass it, refactor, commit. See [`testing-workflow.md`](testing-workflow.md).
- Small, coherent commits. No unrelated changes bundled together.
- Type hints are mandatory on all new code (`mypy --strict` must pass).
- `ruff check .` must pass with zero warnings before a commit is considered
  complete.

## Directory Structure

See the Architecture Overview above. As business modules are added, this
section must be updated to reflect the real structure (e.g. where domain
models, allocation strategies, and I/O adapters live).

## Development Workflow

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest && ruff check . && mypy src
```

See [`README.md`](README.md) for full setup instructions and
[`coding-workflow.md`](coding-workflow.md) for the Git process.

## Testing Strategy

See [`testing-workflow.md`](testing-workflow.md) in full. Summary: TDD by
default, pytest for unit/integration tests, meaningful coverage over 100%
coverage, explicit categorisation of normal/edge/invalid/failure cases for
every business-critical feature.

## Git Workflow

See [`coding-workflow.md`](coding-workflow.md) in full. Summary: feature
branches off `main`, small commits, PR review required before merge, `main`
always stable.

## Documentation Workflow

See [`documentation-workflow.md`](documentation-workflow.md). Summary:
documentation is updated in the same change as the code/decision it
describes, not as an afterthought.

## Important Constraints

- **Git must be operated from WSL, not native Windows shells, in this
  DevSwarm workspace.** The repository's actual git object database lives at
  `/var/www/rows` inside WSL (Ubuntu-20.04); the Windows-visible `.git` file
  is a worktree pointer into that Linux path and cannot be resolved by
  Windows-native git. From WSL, the same directory is reachable at
  `/mnt/c/Users/Afif/.devswarm/repos/2/dfb88366/initial-setup`. This is an
  environment fact discovered while establishing the foundation — see
  [`solutions.md`](solutions.md) for the diagnostic trail. Do not attempt to
  "fix" the `.git` pointer files; this is expected DevSwarm architecture,
  not corruption.
- Remote repository: `origin` is
  [github.com/harvoline/RoWAS](https://github.com/harvoline/RoWAS).
  PRs are opened and reviewed there (PR #1 was the foundation PR).
- CI/CD is explicitly **deferred by owner decision** (2026-09-05, at the
  "first PR" checkpoint — see [`rules.md`](rules.md) and
  [`solutions.md`](solutions.md)). No GitHub Actions workflow exists. Do not
  add one without raising it again first — this was a considered decision,
  not an oversight.

## Known Decisions

| Decision | Rationale | Status |
|---|---|---|
| Python >= 3.10 | Chosen by project owner from a language shortlist | **Confirmed** |
| src-layout package structure | Standard practice, avoids import footguns | Confirmed |
| pytest + ruff + mypy(strict) | Minimal, standard, covers testing/lint/types | Confirmed |
| setuptools build backend | Ubiquitous, avoids extra tooling dependency | Confirmed |
| Repository hosting / PR platform | GitHub: `harvoline/RoWAS` | **Confirmed** |
| CI/CD strategy | Deferred entirely — revisit once there's more code | **Confirmed (deferred)** |

## Things an AI/Developer Must Know Before Modifying This Project

1. **Do not implement robot allocation business logic** until explicitly
   instructed — this was an explicit constraint from the project owner during
   foundation setup, and may still apply until lifted.
2. Run git commands through WSL (see Important Constraints above), not
   native Windows git.
3. Every new business feature needs: a failing test first, an entry in
   `app-workflow.md` describing its flow, and (if a significant technical
   decision was involved) an entry in `solutions.md`.
4. Do not add CI/CD configuration without first triggering the CI/CD
   checkpoint conversation described in `rules.md`.
5. Keep `mypy --strict` and `ruff check .` passing at all times — treat
   failures as build breaks, not warnings to defer.
