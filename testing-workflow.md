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

- 1 smoke test (`tests/test_cli.py`) verifying the CLI entry point imports
  and runs successfully. This exists to validate the scaffolding
  (packaging, entry point, pytest wiring) — it is **not** a business logic
  test, because no business logic exists yet.
- No integration or end-to-end tests yet — not applicable until the
  application has real input/output flows to exercise.

This section must be updated as soon as the first business-logic tests are
added, including the normal/edge/invalid/failure breakdown for that feature.
