# Level 3 — Standby Robot Activation

> Feature spec. See `../robots.md` for shared robot rules. Version 1.0.0 (2026-09-08).

## Purpose
When active robots cannot cover a client work request, recommend the cheapest set of
**additional standby robots to activate/buy**. There is **no** standby inventory input —
the search is unbounded by stock.

## Rules (locked)
1. **No standby inventory input.** "Additional required" is the recommended activate/buy
   set when active robots cannot cover hours (search unbounded by stock).
2. **If active capacity >= requested hours:** do **not** show the additional section.
3. **Always use full active capacity first.** Standby only covers the shortfall:
   `shortfall = requested - active_capacity`.
4. **Output only the winning** additional allocation (not alternatives), in colour.
5. **Colour by robot type** — three distinct ANSI colours for Bravo / Charlie / Delta.
6. **Insufficient / uncoverable shortfall:** same
   `Error: Insufficient robot capacity to complete the requested work.` message
   (should not arise with unbounded types unless hours are invalid).
7. **Top-level menu** currently chooses Level 1, 2, 3, or 4; each level has a separate runner so
   logics do not collide.

## Strategy for the shortfall
Cost-optimised standby fill uses the **same lexicographic objective as Level 2**,
applied to the **shortfall only**, with **no inventory caps**:

1. Minimise total charging cost among allocations with `provided >= shortfall`.
2. Minimise excess hours (`provided - shortfall`).
3. Fewest total robots.
4. Deterministic: prefer more Delta, then more Charlie.

Bound the search by enough robots of each type to cover the shortfall plus a small
margin (same bound style as Level 2).

## Worked example (owner)
Active Bravo:1 Charlie:1 Delta:1 (capacity 16), request 21 → shortfall 5 → winner
Charlie:1 cost $3.

```
Active Robot Capacity: 16 hours
Client Work Requested: 21 hours
Additional Standby Robots Required:
Charlie: 1 - cost $3
```

(Charlie line rendered in Charlie's colour when colour is enabled.)

When active capacity already covers the request (e.g. capacity 16, request 16), omit
the additional section entirely:

```
Active Robot Capacity: 16 hours
Client Work Requested: 16 hours
```

## CLI
Shared EOF/Ctrl+C handling: [Application Workflow](../app-workflow.md).

After the Level 1/2/3/4 menu, Level 3 prompts for **active** inventory (Bravo/Charlie/Delta)
and client work hours — the same prompts as Levels 1–2. It does **not** ask for standby
stock.

## Error handling
Shared validation for hours (positive integer) and active robot counts (non-negative
integers). Insufficient capacity uses the shared InsufficientCapacityError message when
applicable after the additional-require path.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-08 | Initial Level 3 standby activation + top-level menu. |
| 1.0.0 (docs) | 2026-09-08 | Refreshed menu context and linked shared termination handling. |
