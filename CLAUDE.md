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

**Current state:** Levels 1–4 are implemented under `src/everbot/` (category
distribution, cost-optimised allocation with L1/L2 comparison, standby
activation, and multi-client allocation behind a Level 1/2/3/4 menu). Further
levels will be added progressively by the project owner.

## Domain Context

Shared robot rules: [`robots.md`](robots.md). Per-level strategies:
[`features/`](features/) (Level 1 category distribution; Level 2 cost-optimised;
Level 3 standby activation; Level 4 multi-client allocation). Do not invent new
domain rules ahead of requirements.

## Technology Stack

- **Language:** Python >= 3.10 (chosen by project owner from a shortlist of
  TypeScript/Python/Java/C# during foundation setup; verified available
  version in the dev environment is 3.10.12).
- **Packaging:** `pyproject.toml`, setuptools backend, **src-layout**
  (`src/everbot/`).
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
src/everbot/
    __init__.py / __main__.py
    robots.py       # Robot ABC + Bravo/Charlie/Delta
    errors.py       # EverBotError hierarchy
    allocation.py   # Allocation value object
    allocator.py    # shared validation + strategy delegation
    strategies/     # AllocationStrategy + CategoryDistribution + CostOptimised
    comparison.py   # Level 1 vs Level 2 cost comparison
    standby.py      # Level 3 standby plan (active capacity + shortfall fill)
    multiclient.py  # Level 4 multi-client plan (shared pool, hours parsing)
    cli.py          # interactive CLI (Level 1/2/3/4 menu + runners)
features/level-1.md ... features/level-4.md
robots.md
tests/              # allocation, cost, standby, multi-client, CLI, design tests
```

**Principle:** CLI/input-output concerns stay separate from domain/business
logic. Domain logic is testable without the terminal. Validation is separate
from processing. New levels add an `AllocationStrategy` subclass (Open/Closed).

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

## Multi-Agent Workflow

See [`orchestrator-workflow.md`](orchestrator-workflow.md) in full. Summary:
the project owner talks only to the Orchestrator (the main Claude Code
session). For every meaningful requirement, the Orchestrator runs a
coverage assessment across business/domain/architecture/testing/security/
performance/UX/documentation/ops/production-readiness, and delegates only
the dimensions that genuinely need specialist investigation to the
read-only specialist subagents in [`.claude/agents/`](.claude/agents/).
Coverage is mandatory; agent participation is optional — the Orchestrator
must be able to explain why any dimension wasn't delegated, not just that
it wasn't mentioned. The Orchestrator always owns synthesis, implementation,
and commits.

## Important Constraints

- This project must remain portable: no assumption about OS, shell, or
  sandbox/host environment belongs in this file. If your machine has a
  local quirk (e.g. a sandboxed dev environment that changes how a
  standard command must be invoked), document it in a local, gitignored
  `user-setup.md` at the repo root instead — see
  [`documentation-workflow.md`](documentation-workflow.md). Check for one
  before assuming a standard command will behave as documented here.
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
| Package name `everbot` (was `robot_allocation`) | Match product name; single package tree under `src/everbot/` | **Confirmed** |
| Level 1 strategy pattern (Allocator + AllocationStrategy) | Open/Closed for future levels; shared validation in Allocator | **Confirmed** |
| Level 2 CostOptimisedStrategy + L1/L2 comparison | Min cost (then excess, fewest robots); CLI compares strategies | **Confirmed** |
| Level 3 standby workflow + Level 1/2/3 menu | Active capacity first; unbounded shortfall fill; separate runners | **Confirmed** |
| Level 4 multi-client workflow (`multiclient.py`) | Shared active pool drawn down highest-hours-first; whole-robot consumption; reuses Level 3 shortfall fill | **Confirmed** |
| pytest + ruff + mypy(strict) | Minimal, standard, covers testing/lint/types | Confirmed |
| setuptools build backend | Ubiquitous, avoids extra tooling dependency | Confirmed |
| Repository hosting / PR platform | GitHub: `harvoline/RoWAS` | **Confirmed** |
| CI/CD strategy | Deferred entirely — revisit once there's more code | **Confirmed (deferred)** |
| PR review enforcement | Convention only (no branch protection) — private repo on GitHub Free blocks it; also currently a solo collaborator. Revisit if the plan is upgraded or a second collaborator joins | **Confirmed (interim)** |

## Things an AI/Developer Must Know Before Modifying This Project

1. **Do not invent new allocation levels or domain rules** until explicitly
   instructed. Levels 1–4 are implemented; further levels need owner requirements.
2. Check for a local, gitignored `user-setup.md` before assuming a standard
   command (e.g. `git`) will behave exactly as documented — some
   sandboxed/managed environments need a different invocation. Never add
   machine-specific workarounds to this file (`CLAUDE.md`) or other tracked
   docs; they belong in `user-setup.md`.
3. Every new business feature needs: a failing test first, an entry in
   `app-workflow.md` describing its flow, and (if a significant technical
   decision was involved) an entry in `solutions.md`.
4. Do not add CI/CD configuration without first triggering the CI/CD
   checkpoint conversation described in `rules.md`.
5. Keep `mypy --strict` and `ruff check .` passing at all times — treat
   failures as build breaks, not warnings to defer.
6. For any meaningful requirement, run the coverage assessment in
   `orchestrator-workflow.md` before jumping to implementation — even if it
   concludes most dimensions are "not relevant," that conclusion must be
   conscious, not silent.
