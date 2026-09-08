# EverBot Solutions — Robot Reference

> **Version:** 1.4.0 | **Last updated:** 2026-09-08
> Single source of truth for shared robot rules. Update the changelog on every change.
> Per-level strategies live in `features/`.

## Overview
EverBot Solutions assigns specialized robots (Bravo/Charlie/Delta) to fulfil client work
requests, measured in total hours, as efficiently as possible. Each level uses a different
allocation strategy.

## Robot Types
| Type    | Working hours / day | Charging cost / day |
|---------|--------------------:|--------------------:|
| Bravo   | 3 h                 | $2                  |
| Charlie | 5 h                 | $3                  |
| Delta   | 8 h                 | $4                  |

## General Rules
- Each robot works once per day for its max hours, then recharges.
- A robot cannot be used more than once per day / per allocation.
- Robot counts must be non-negative integers; client work hours must be positive integers.
- Combined robot hours need not match exactly but must be **>= requested** (overshoot allowed,
  undershoot not). E.g. request 16 -> 17 or 18 OK, 15 not.
- If work cannot be fulfilled, show a clear error message.

## Error Messages
| Situation | Message |
|-----------|---------|
| Insufficient capacity | `Error: Insufficient robot capacity to complete the requested work.` |
| Cannot allocate one per category | `Error: Unable to allocate at least one robot from each category with the available inventory.` |
| Zero robots available | `Error: No robots available for assignment.` |
| Invalid work hours | `Error: Work hours must be a positive integer.` |

## Levels

Optional menu option 5 adds reporting over Level 4 without changing robot rules:
see [Optional Advanced Features](features/optional-advanced.md).

All levels share the terminal exit behaviour in [Application Workflow](app-workflow.md):
EOF exits 1 and Ctrl+C exits 130, with stderr messages and no traceback.
- **Level 1 — Robot Category Distribution:** see `features/level-1.md`.
- **Level 2 — Cost Optimised Allocation:** see `features/level-2.md`.
- **Level 3 — Standby Robot Activation:** see `features/level-3.md`.
- **Level 4 — Multi-Client Allocation:** see `features/level-4.md`.

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-06 | Initial robot rules captured. |
| 1.1.0 | 2026-09-06 | Linked Level 1 spec; moved per-level detail to `features/`. |
| 1.2.0 | 2026-09-07 | Linked Level 2 cost-optimised spec. |
| 1.3.0 | 2026-09-08 | Linked Level 3 standby activation + top-level menu. |
| 1.4.0 | 2026-09-08 | Linked Level 4 multi-client allocation. |
| 1.4.0 (docs) | 2026-09-08 | Linked shared CLI termination behaviour; robot rules unchanged. |
