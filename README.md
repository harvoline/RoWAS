# EverBot Solutions - Robot Working Allocation System

A Python 3.10+ terminal application that assigns Bravo, Charlie, and Delta robots
to client work. Levels 1-4 are implemented; there is no server, GUI, or persistence.

## Setup and Run

Create and activate a virtual environment using your platform's standard commands:

```bash
python3 -m venv .venv
```

With that environment active:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m everbot
# Alternative entry point: everbot-allocate
```

Select a level, enter the three robot counts, then the requested hours. Level 4
accepts one value or several values separated by commas or whitespace, for example
`12,16,17,10,21`. With inventory Bravo:2, Charlie:3, Delta:2, that example produces
a total standby cost of $23.

Successful runs exit 0; invalid input or insufficient capacity exits 1. EOF exits
1 with an input-ended message; Ctrl+C exits 130 with a cancellation message.
Termination messages go to stderr without a traceback. Restart to enter a new
request; no allocation is persisted.

## Approach and Design Decisions

| Level | Approach |
|---|---|
| 1 | Require every robot category; minimise excess hours, then robot count |
| 2 | Minimise charging cost, then excess, robot count, and deterministic type preference; compare against Level 1 |
| 3 | Use full active capacity, then recommend cost-optimised standby for the shortfall |
| 4 | Serve clients highest-hours-first from a shared pool; apply Level 2 or standby per client |

`src/everbot/` separates terminal I/O (`cli.py`) from shared validation (`allocator.py`),
allocation strategies (`strategies/`), and workflow services (`standby.py`,
`multiclient.py`). Robot definitions and allocation results centralise derived hours
and costs. Strategies suit Levels 1-2; workflow composition suits Levels 3-4.

Python and standard-library domain code keep dependencies small. Setuptools provides
packaging; pytest, Ruff, and strict mypy cover behaviour, lint, and source types.
The src layout separates package code from repository files; current tests also
add `src` to the import path, so they do not prove packaging works.

## Assumptions and Trade-offs

- Counts are non-negative integers; requested hours are positive integers. Missing
  inventory categories default to zero; unknown inventory keys are ignored.
- Robots work once per day. Excess hours are allowed; assigned robots cannot be
  split across clients. Bravo/Charlie/Delta provide 3/5/8 hours for $2/$3/$4.
- Standby stock is unbounded. Costs represent charging, not purchase prices.
- Level 4 preserves input order for equal requests. Its prescribed greedy ordering
  does not guarantee the lowest total cost across all clients.
- Exhaustive bounded searches are easy to inspect and preserve exact objectives,
  but become slow as inventory or standby shortfall grows.
- CLI termination is handled once in `main()`; reusable runners propagate EOF and
  interruption to their caller. No retry loop or saved session is provided.

## Verification

```bash
python -m pytest --cov=everbot --cov-report=term-missing
python -m ruff check .
python -m mypy src
```

Tests cover allocation examples, validation, client ordering, inventory consumption,
formatting, and termination through the process entry point. See
[testing-workflow.md](testing-workflow.md) for coverage and remaining gaps.

## Technical Debt

With additional time, priorities are:

1. Reduce the cubic search space and add realistic scale benchmarks. A review probe
   of a 1,000-hour standby shortfall took about 3.5 seconds on one machine.
2. Replace floating-point search-bound division with integer ceiling division.
   Very large valid integers currently raise `OverflowError`; this alone would not
   solve the search-performance problem. See the explanation in [solutions.md](solutions.md).
3. Align the setuptools minimum with SPDX license metadata support (77+), and verify
   a built wheel and both installed entry points outside the source checkout.
4. Add independent optimality checks over small inventories and more failure-path
   coverage. Passing source tests is not installed-package verification.

CI/CD remains explicitly deferred by owner decision. PR review is enforced by
convention; branch protection is unavailable under the recorded repository setup.
Higher allocation levels require new owner requirements.

## Project Documentation

- [Robot rules](robots.md), [Level 1](features/level-1.md), [Level 2](features/level-2.md),
  [Level 3](features/level-3.md), [Level 4](features/level-4.md)
- [Application flow](app-workflow.md), [project context](CLAUDE.md), [decision records](solutions.md)
- [Coding workflow](coding-workflow.md), [testing workflow](testing-workflow.md),
  [documentation workflow](documentation-workflow.md), [project rules](rules.md)
- [Review/delegation workflow](orchestrator-workflow.md), [AI tool log](tools.md)

Repository: [harvoline/RoWAS](https://github.com/harvoline/RoWAS). Keep machine-specific
workarounds in a local, gitignored `user-setup.md`.
