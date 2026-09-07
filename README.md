# EverBot Solutions — Robot Working Allocation System

A terminal-based system for allocating work to robots, built for EverBot Solutions.

## Status

**Levels 1–2 implemented.** The CLI allocates Bravo/Charlie/Delta robots using
Level 2 Cost Optimised Allocation by default, and compares charging cost against
Level 1 (Robot Category Distribution). Foundation engineering scaffolding
(packaging, linting/type-checking, test infrastructure, process docs) remains
in place; further levels will land as reviewed feature branches.

## Business Problem

EverBot Solutions assigns specialized robots to fulfil client work requests
(measured in hours) as efficiently as possible. Each level uses a different
allocation strategy. Shared robot rules live in [`robots.md`](robots.md);
per-level specs live under [`features/`](features/).

## Architecture (current)

```
src/everbot/                 Application package (src-layout)
  __init__.py                Public API re-exports
  __main__.py                python -m everbot entry
  robots.py                  Robot ABC + Bravo/Charlie/Delta
  errors.py                  EverBotError hierarchy + exact messages
  allocation.py              Allocation result value object
  allocator.py               Shared validation + strategy delegation
  strategies/                AllocationStrategy + CategoryDistribution +
                             CostOptimised strategies
  comparison.py              Level 1 vs Level 2 cost comparison
  cli.py                     Interactive CLI (Level 2 + comparison)
features/                    Per-level specifications (level-1.md, level-2.md)
robots.md                    Shared robot reference
tests/                       pytest suite mirroring the package
```

Domain logic stays separate from CLI/I/O (see [`CLAUDE.md`](CLAUDE.md) and
[`coding-workflow.md`](coding-workflow.md)).

## Technology Stack

| Concern          | Choice                          |
|-------------------|----------------------------------|
| Language          | Python (>= 3.10)                |
| Packaging         | `pyproject.toml` + setuptools (src layout) |
| Testing           | pytest, pytest-cov              |
| Linting/formatting| ruff                             |
| Type checking     | mypy (`strict = true`)          |

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

> **Environment note:** if a standard command in this guide doesn't behave as
> documented on your machine, create a local gitignored `user-setup.md` — see
> [`documentation-workflow.md`](documentation-workflow.md).

## Running the CLI

```bash
everbot-allocate
# or:
python -m everbot
```

Example session (see [`features/level-2.md`](features/level-2.md)):

```
Enter number of robots available:
Bravo: 2
Charlie: 3
Delta: 2

Enter client work hours:
20

Cost Optimized Allocation
Charlie: 1
Delta: 2
Total Hours Provided: 21
Total Charging Cost: $11

Level 1 vs Level 2 Cost Comparison

Level 1 Cost: $12
Level 2 Cost: $11
Cost Difference: $1
Insight: Level 1 strategy resulted in $1 additional cost due to mandatory usage of multiple robot categories
```

## Level 1 — Robot Category Distribution

Assign robots so that (in priority order): every category is represented
(>=1 Bravo, Charlie, Delta), total hours >= requested with the **least excess**,
and ties are broken by the **fewest robots**. See
[`features/level-1.md`](features/level-1.md).

## Level 2 — Cost Optimised Allocation

Minimise total charging cost (no mandatory diversity). Tie-breaks: min excess,
then fewest robots, then deterministic Delta/Charlie preference. The CLI also
compares Level 1 vs Level 2 cost. See [`features/level-2.md`](features/level-2.md).

## Running Tests

```bash
pytest              # run the test suite
pytest --cov        # with coverage
ruff check .        # lint
mypy src            # type-check
```

## Development Workflow

See [`coding-workflow.md`](coding-workflow.md) and
[`testing-workflow.md`](testing-workflow.md). In short:

1. One feature/fix per branch, branched from `main`.
2. Write a failing test before writing implementation code.
3. Small, coherent commits with messages that explain *why*.
4. Pull request review before merging into `main`.

## Documentation Map

| File | Purpose |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Living project context for AI/developer onboarding |
| [`robots.md`](robots.md) | Shared robot rules (single source of truth) |
| [`features/level-1.md`](features/level-1.md) | Level 1 category-distribution spec |
| [`features/level-2.md`](features/level-2.md) | Level 2 cost-optimised allocation + comparison |
| [`tools.md`](tools.md) | Log of AI tool usage and outcomes |
| [`solutions.md`](solutions.md) | Engineering reasoning behind significant decisions |
| [`app-workflow.md`](app-workflow.md) | Functional/business workflow |
| [`coding-workflow.md`](coding-workflow.md) | Git branching, commit, and PR discipline |
| [`testing-workflow.md`](testing-workflow.md) | TDD cycle and test categorisation strategy |
| [`rules.md`](rules.md) | Non-negotiable project and safety rules |
| [`documentation-workflow.md`](documentation-workflow.md) | When/how documentation must be updated |
| [`orchestrator-workflow.md`](orchestrator-workflow.md) | Multi-agent delegation workflow |

## Known Limitations / Open Decisions

- **Higher levels beyond 2 not yet implemented.** Levels 1–2 land via strategy
  subclasses; Levels 3+ will add further strategies without changing Level 1/2.
- **Repository hosting: decided.** GitHub, at
  [harvoline/RoWAS](https://github.com/harvoline/RoWAS) (`origin`).
- **CI/CD: explicitly deferred.** See `solutions.md`; revisit when justified.
- **PR review is convention-enforced, not technically gated.** Private repo on
  GitHub Free; see `rules.md` "Pull Request Review".

## Technical Debt

None yet. This section will track deliberate shortcuts as they are introduced.
