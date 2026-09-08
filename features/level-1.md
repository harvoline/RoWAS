# Level 1 — Robot Category Distribution

> Feature spec. See `../robots.md` for shared robot rules. Version 1.0.0 (2026-09-06).

## Purpose
Evaluate performance across robot categories (for future purchasing decisions) by distributing
work across all robot categories whenever possible.

## Strategy (lexicographic priority)
1. **Diversity (mandatory):** include >=1 Bravo, >=1 Charlie, >=1 Delta.
2. **Minimise excess hours (global):** minimise `provided - requested`, with `provided >= requested`.
3. **Fewest robots (tiebreak):** on equal excess, choose the fewest total robots.

Base allocation is 1/1/1 = 16h.

## Worked examples
| Requested | Allocation B/C/D | Provided | Excess |
|----------:|------------------|---------:|-------:|
| 16 | 1/1/1 | 16 | 0 |
| 17 | 2/1/1 | 19 | 2 |
| 21 | 1/2/1 | 21 | 0 |
| 24 | 1/1/2 | 24 | 0 |
| 22 | 3/1/1 | 22 | 0 |
| 10 | 1/1/1 | 16 | 6 |

Excess is minimised globally, not just by filling the remainder with one robot.

## Error handling (check order)
1. Work hours not a positive integer -> `Error: Work hours must be a positive integer.`
2. All counts zero -> `Error: No robots available for assignment.`
3. Any category unavailable -> `Error: Unable to allocate at least one robot from each category with the available inventory.`
4. All robots still can't reach requested hours -> `Error: Insufficient robot capacity to complete the requested work.`

## CLI
Shared EOF/Ctrl+C handling: [Application Workflow](../app-workflow.md).

Input:
```
Enter number of robots available:
Bravo: 2
Charlie: 3
Delta: 2

Enter client work hours:
16
```
Output:
```
Robot Assignment

Bravo: 1
Charlie: 1
Delta: 1

Total Work Hours Provided: 16
Client Work Hours Requested: 16
```

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-06 | Initial Level 1 category-distribution strategy. |
| 1.0.0 (docs) | 2026-09-08 | Linked shared EOF/Ctrl+C handling; allocation rules unchanged. |
