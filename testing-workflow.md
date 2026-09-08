# Testing Workflow

## Methodology: TDD by Default

```
RED       Write a failing test that expresses the desired behaviour
GREEN     Write the minimum implementation to make it pass
REFACTOR  Improve the implementation without changing behaviour
REPEAT
```

This cycle is not optional for business-logic changes. It is acceptable to
relax strict RED-GREEN-REFACTOR ceremony for pure scaffolding/config changes
that have no behaviour to test (e.g. adding a linter config) — but any code
with observable behaviour gets a test written first.

## Tooling

| Concern | Tool | Command |
|---|---|---|
| Test runner | pytest | `pytest` |
| Coverage | pytest-cov | `pytest --cov` |
| Lint | ruff | `ruff check .` |
| Type checking | mypy (strict) | `mypy src` |

All four must pass before a commit is considered complete.

## Test Categorisation

For every significant feature, identify and cover:

- **Normal cases** — the expected, common-path behaviour.
- **Edge cases** — unusual but valid situations (empty input, boundary
  values, maximum/minimum counts, ties, etc.).
- **Invalid cases** — input that must be explicitly rejected, with a clear
  error, not a crash.
- **Failure cases** — things that can fail unexpectedly (e.g. resource
  unavailable) and how the system should degrade or report that failure.

Document the **expected behaviour** for each case, not just "it should
work."

## Coverage Philosophy

Do not chase 100% line coverage as a goal in itself. Prioritise meaningful
coverage of business-critical behaviour — the allocation rules, validation
logic, and error handling matter far more than trivial getters or CLI
argument wiring.

## Current State

Tests under `tests/` cover domain behaviour, CLI behaviour, and entry-point exits:

| File | Covers |
|---|---|
| `test_design.py` | Robot hierarchy, strategy interface, `Allocation` value object |
| `test_allocation.py` | Level 1 category distribution + shared validation |
| `test_cost_optimised.py` | Level 2 cost objective and tie-breaks |
| `test_standby.py` | Level 3 active capacity + unbounded shortfall fill |
| `test_multiclient.py` | Level 4 hours parsing, priority order, shared-pool drawdown |
| `test_cli.py` | Menu dispatch, all four runners, formatters, error paths, EOF/Ctrl+C at `main`, subprocess EOF exits |

Level 4 case breakdown (the categorisation this document mandates):

- **Normal:** owner's five-client example (service order, per-client allocation,
  standby, total cost); single-client run; space- vs comma-separated equivalence.
- **Edge:** equal hours served in input order; a higher-hours later client served
  before an earlier one; an assigned robot consumed whole rather than split across
  clients; exact-capacity coverage; zero active inventory; pool drawn to empty
  mid-run.
- **Invalid:** empty/blank hours line, non-numeric token, zero or negative value,
  float, wrong type, semicolon separator, negative robot counts.
- **Failure:** insufficient capacity cannot occur while standby is unbounded — the
  shared error remains covered by the Level 1/2 tests that can still raise it.

Termination failure cases cover EOF and KeyboardInterrupt at the menu and each
level's hours prompt. Subprocess tests exercise `python -m everbot` with EOF at
the menu and inventory prompts, asserting exit 1 and stderr without a traceback.
Ctrl+C is injected as KeyboardInterrupt in process-boundary unit tests; real
terminal signal delivery is not exercised. The intended exit code is 130.

The suite has no persistence or network integration to exercise. It does have a
process boundary. Pytest adds `src` to the import path, and module subprocess tests
use the current environment; neither proves an independently installed wheel.
Remaining gaps: installed console-script smoke tests, build metadata validation,
scale benchmarks, very-large-integer bounds, and independent optimality oracles.
