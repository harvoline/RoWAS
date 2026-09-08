# Level 4 — Multi-Client Allocation

> Feature spec. See `../robots.md` for shared robot rules and
> `level-3.md` for the standby activation this level builds on. Version 1.0.0 (2026-09-08).

## Purpose
Serve **several clients** from one active robot inventory in the same run. Level 3
handled a single client; Level 4 accepts many client work-hour values, prioritises
them by highest hours requested, and recommends standby robots for whatever the
active inventory cannot cover.

## What changes from Level 3
| | Level 3 | Level 4 |
|---|---|---|
| Clients per run | exactly 1 | 1..n, from one input line |
| Hours input | single integer | single value, comma-separated, or space-separated |
| Active inventory | whole capacity for the one client | **shared pool**, drawn down client by client |
| Ordering | n/a | highest hours requested first |
| Standby fill | unbounded, cost-optimised | unchanged, applied per client |

## Input rules
One prompt accepts all client hours. The **number of values is the number of clients**:

```
Client working hours:20
Client working hours:12,16,17,10,21
Client working hours:12 16 17 10 21
```

- Separators: commas, whitespace, or both (`12, 16 17` is accepted).
- Surrounding/repeated separators are ignored (`12,,16 ` -> two clients).
- Every value must be a positive integer, else
  `Error: Work hours must be a positive integer.`
- Empty input (no values at all) is the same error — a run needs at least one client.
- Clients keep their **input position** as their number (`Client 1` is the first value
  typed), regardless of the order they are served in.

## Priority rule
Clients are served in **descending requested hours**. Ties are served in input order.

## Allocation rules (per client, in priority order, against the *remaining* pool)
1. **Pool covers the client** (remaining active hours >= requested): allocate from the
   remaining inventory using the Level 2 objective — minimise cost, then excess, then
   robot count, preferring more Delta then Charlie. Those robots leave the pool.
   No standby section for this client.
2. **Pool cannot cover the client:** assign **all** remaining active robots (Level 3's
   "use full active capacity first"), leaving the pool empty, then fill
   `shortfall = requested - remaining active hours` with the Level 3 unbounded,
   cost-optimised standby recommendation.
3. Once the pool is empty, every later client is covered entirely by standby.

A robot assigned to a client is consumed for the day and cannot serve another client
(`robots.md`: each robot works once per day). Unused hours on an assigned robot are
excess, not carried over to the next client.

## Worked example
Inventory Bravo:2 Charlie:3 Delta:2 (37 active hours), input `12,16,17,10,21`.
Service order 21, 17, 16, 12, 10.

| Served | Client | Requested | From active pool | Pool after | Standby required | Standby cost |
|---|---|---:|---|---|---|---:|
| 1st | Client 5 | 21 | Charlie:1, Delta:2 (21h) | B2 C2 D0 (16h) | — | — |
| 2nd | Client 3 | 17 | Bravo:2, Charlie:2 (16h) | empty | Bravo:1 | $2 |
| 3rd | Client 2 | 16 | — | empty | Delta:2 | $8 |
| 4th | Client 1 | 12 | — | empty | Charlie:1, Delta:1 | $7 |
| 5th | Client 4 | 10 | — | empty | Charlie:2 | $6 |

Total standby cost: $23.

## CLI
Shared EOF/Ctrl+C handling: [Application Workflow](../app-workflow.md).

Menu gains **option 4**, with its own runner so Level 1–3 logic does not collide.
Prompts are the active inventory (Bravo/Charlie/Delta) then the multi-value client
hours line. No standby stock is ever requested.

```
Multi-Client Allocation

Active Robot Capacity: 37 hours
Clients: 5 (served highest hours first)

Client 5: 21 hours requested
  Active Robots Allocated: Charlie: 1, Delta: 2 (21 hours)

Client 3: 17 hours requested
  Active Robots Allocated: Bravo: 2, Charlie: 2 (16 hours)
  Additional Standby Robots Required:
    Bravo: 1 - cost $2

Client 2: 16 hours requested
  Additional Standby Robots Required:
    Delta: 2 - cost $8

Total Standby Cost: $23
```

Standby lines keep the Level 3 per-type colours (Bravo / Charlie / Delta) when colour
is enabled. Clients fully covered by the active pool have no standby section.

## Error handling (check order)
1. Robot counts not non-negative integers -> `Error: Robot counts must be non-negative integers.`
2. No client hours given, or any value not a positive integer ->
   `Error: Work hours must be a positive integer.`
3. Insufficient capacity cannot arise: standby is unbounded, so any shortfall is
   coverable. The shared `Error: Insufficient robot capacity to complete the requested work.`
   remains available for a future bounded-standby rule.

Zero active robots is valid — every client is then served entirely by standby.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-08 | Initial Level 4 multi-client allocation spec. |
| 1.0.0 (docs) | 2026-09-08 | Linked shared EOF/Ctrl+C handling; allocation rules unchanged. |
