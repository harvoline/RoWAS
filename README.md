# EverBot Solutions — Robot Working Allocation System

A terminal-based system for allocating work to robots, built for EverBot Solutions.

## Status

**Foundation stage.** No robot allocation business logic has been implemented yet.
This repository currently contains only the engineering scaffolding: project
structure, packaging, linting/type-checking configuration, test infrastructure,
and process documentation. Business functionality will be added incrementally,
one reviewed feature branch at a time.

## Business Problem

EverBot Solutions needs a way to allocate work to robots based on business rules
that will be specified progressively. The system is a terminal (CLI) application:
it reads input, applies allocation rules, and produces output — no GUI, no
persistent server.

## Architecture (current)

```
src/robot_allocation/   Application package (src-layout)
  __init__.py
  cli.py                Entry point only — no business logic yet
tests/                   pytest test suite, mirrors src/ package structure
```

As business logic is introduced, domain rules will live in their own modules,
separate from CLI/input-output concerns (see [`CLAUDE.md`](CLAUDE.md) and
[`coding-workflow.md`](coding-workflow.md) for the architectural principles this
project follows).

## Technology Stack

| Concern          | Choice                          |
|-------------------|----------------------------------|
| Language          | Python (>= 3.10)                |
| Packaging         | `pyproject.toml` + setuptools (src layout) |
| Testing           | pytest, pytest-cov              |
| Linting/formatting| ruff                             |
| Type checking     | mypy (`strict = true`)          |

**Decision record:** the language was chosen by the project owner from a
shortlist (TypeScript, Python, Java, C#) presented during foundation setup;
Python was selected. See [`solutions.md`](solutions.md) for the reasoning
behind the supporting tool choices (ruff, mypy, pytest, src-layout).

## Repository

Hosted on GitHub: [harvoline/RoWAS](https://github.com/harvoline/RoWAS).
`main` is the stable branch; feature/fix work happens on branches and merges
via reviewed pull requests (see `coding-workflow.md`).

## Installation

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

> **Environment note:** this repository is managed by DevSwarm, which stores the
> actual git object database inside a WSL (Ubuntu) filesystem path
> (`/var/www/rows`) and exposes this directory as a git *worktree* mirrored onto
> the Windows filesystem. Git commands run from a native Windows shell **will
> fail** because the `.git` worktree pointer references a Linux-only path. Run
> all git commands from inside WSL against this same path (via its `/mnt/c/...`
> mount). File edits work normally from either side. See
> [`rules.md`](rules.md) for details.

## Running the CLI

```bash
everbot-allocate
# or, without installing the console script:
python -m robot_allocation.cli
```

Currently this only prints a placeholder banner — there is no allocation
functionality yet.

## Running Tests

```bash
pytest              # run the test suite
pytest --cov        # with coverage
ruff check .        # lint
mypy src            # type-check
```

All three checks currently pass against the scaffolding (1 smoke test, no
lint/type errors).

## Development Workflow

See [`coding-workflow.md`](coding-workflow.md) for the full Git branching and
commit discipline, and [`testing-workflow.md`](testing-workflow.md) for the
TDD cycle this project follows. In short:

1. One feature/fix per branch, branched from `main`.
2. Write a failing test before writing implementation code.
3. Small, coherent commits with messages that explain *why*.
4. Pull request review before merging into `main`.

## Documentation Map

| File | Purpose |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Living project context for AI/developer onboarding |
| [`tools.md`](tools.md) | Log of AI tool usage and outcomes |
| [`solutions.md`](solutions.md) | Engineering reasoning behind significant decisions |
| [`app-workflow.md`](app-workflow.md) | Functional/business workflow (populated as features land) |
| [`coding-workflow.md`](coding-workflow.md) | Git branching, commit, and PR discipline |
| [`testing-workflow.md`](testing-workflow.md) | TDD cycle and test categorisation strategy |
| [`rules.md`](rules.md) | Non-negotiable project and safety rules |
| [`documentation-workflow.md`](documentation-workflow.md) | When/how documentation must be updated |

## Known Limitations / Open Decisions

- **No business logic yet.** This is intentional — see project instructions.
- **Repository hosting: decided.** GitHub, at
  [harvoline/RoWAS](https://github.com/harvoline/RoWAS) (`origin`). PRs are
  reviewed there.
- **CI/CD: explicitly deferred.** At the first-PR checkpoint (2026-09-05),
  the project owner chose to defer CI/CD entirely for now rather than add a
  GitHub Actions workflow. No CI config exists in this repo. The previously
  discussed 3-hour scheduled build was considered and declined in favour of
  event-driven checks — but even that was deferred, not adopted, pending
  more code to justify it. See `solutions.md` for the full reasoning; revisit
  when it's worth the setup cost.
- **Dependency management is intentionally minimal**: only pytest, pytest-cov,
  ruff, and mypy as dev dependencies. No runtime dependencies exist yet
  because there is no functionality requiring them.

## Technical Debt

None yet. This section will track deliberate shortcuts as they are introduced.
