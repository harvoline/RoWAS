# Optional Advanced Features

Version 1.0.0 (2026-09-08). Menu option **5**, separate from allocation Levels 1-4.

## Allocation

Reuse [Level 4](level-4.md) unchanged: multiple requests share active inventory,
highest-hours-first, ties in input order, whole robots consumed per client.
Choose lowest charging cost, then least excess, then fewest robots, retaining
the existing deterministic type preference. Standby covers any remaining shortfall.
Input accepts `16,10,22,7` or `16 10 22 7`, without literal brackets.

## Allocation Summary

After all per-client blocks, display:

- Total Robots Used: assigned active plus recommended standby, with subtotals.
- Total Charging Cost: full daily charging costs for both groups, with subtotals.
- Requested Hours and Assigned Capacity (including standby and excess).
- Avg Robot Utilization: `100 * total requested hours / assigned capacity`.

These are planned totals, not measured execution or purchased robots. Unused
active inventory contributes neither cost nor capacity to the summary.

## Efficiency Metrics

For each of Bravo, Charlie, Delta:

- Active Inventory Usage: active assigned count / initial inventory count, with
  a percentage. Standby is excluded. Zero initial stock displays `0/0 (N/A)`;
  available but unused stock displays `0/n (0.00%)`.
- Estimated Useful Working Capacity: useful hours attributed to that type /
  assigned capacity of that type, including active and standby. A type with no
  assigned robots displays `N/A`.

For each client, attribute useful hours proportionally:
`type useful hours = requested hours * type assigned capacity / client assigned capacity`.
Then sum useful hours and assigned capacity by type across clients before dividing.
Do not average client percentages. Fractions remain exact until display, rounded
to two decimal places. This estimate does not impose an execution order or change
the allocation objective or full charging cost.

Example: a 7-hour client assigned Bravo:1 and Charlie:1 has 8 hours capacity.
Bravo receives 2.625 useful hours; Charlie receives 4.375. Both are 87.50%
utilized for that client. Actual robot runtime is not tracked.

## Validation and Failure Behaviour

Reuse Level 4 parsing and validation, including zero active inventory. Invalid
input produces no summary. Shared EOF/Ctrl+C handling lives in
[Application Workflow](../app-workflow.md). Search scale/overflow limitations
remain as documented in README; reporting adds a linear pass over clients.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-09-08 | Separate advanced menu option, combined summary and both utilization measures |
