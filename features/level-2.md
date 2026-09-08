# Level 2 — Cost Optimised Allocation

> Feature spec. See `../robots.md` for shared robot rules. Version 1.0.0 (2026-09-07).

## Purpose
Maximise profits by minimising robot charging costs. Allocate robots purely on
cost efficiency — there is **no** mandatory diversity across categories.

## Strategy (lexicographic priority)
1. **Minimise total charging cost** among allocations with `provided >= requested`.
2. **Minimise excess hours** (`provided - requested`) on equal cost.
   - Needed so owner Example 2 uniquely selects 2 Bravo (exact 6h @ $4) over
     1 Delta (8h @ $4).
3. **Fewest total robots** on equal cost and excess.
4. **Deterministic:** prefer more Delta, then more Charlie (stable remaining ties).

Diversity is **not** required. Zero counts for a category are allowed (and omitted
from CLI output).

## Worked examples

### Example 1
Inventory Bravo:2 Charlie:3 Delta:2, hours 20:

```
Cost Optimized Allocation
Charlie: 1
Delta: 2
Total Hours Provided: 21
Total Charging Cost: $11
```

### Example 2
Inventory Bravo:2 Charlie:2 Delta:3, hours 6:

```
Cost Optimized Allocation
Bravo: 2
Total Hours Provided: 6
Total Charging Cost: $4
```

## Level 1 vs Level 2 comparison
The CLI always attempts both strategies for the same inputs.

For Example 1:
```
Level 1 Cost: $12
Level 2 Cost: $11
Cost Difference: $1
Insight: Level 1 strategy resulted in $1 additional cost due to mandatory usage of multiple robot categories
```

When Level 1 is infeasible (e.g. a category is missing) but Level 2 succeeds, the
CLI still shows the Level 2 allocation and reports Level 1 as infeasible with the
Level 1 error message — it does not fail the whole run.

## Error handling (check order)
Shared Allocator checks first (invalid hours, invalid counts, no robots).
Then Level 2 specific:
1. All robots still can't reach requested hours -> `Error: Insufficient robot capacity to complete the requested work.`

`MissingCategoryError` does **not** apply to Level 2.

## CLI
Shared EOF/Ctrl+C handling: [Application Workflow](../app-workflow.md).

After inventory + hours, the interactive flow prints the Level 2 block (header
wording matches owner examples: "Cost Optimized Allocation") then the comparison
block. See examples above.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-07 | Initial Level 2 cost-optimised strategy + L1/L2 comparison. |
| 1.0.0 (docs) | 2026-09-08 | Linked shared EOF/Ctrl+C handling; allocation rules unchanged. |
