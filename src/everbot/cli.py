"""Interactive command-line interface for the EverBot allocation system.

Input/output format matches ``features/level-1.md`` and ``features/level-2.md``.
The core functions take injectable ``input_fn`` / ``output_fn`` so the flow is
easy to unit-test. Colour is optional (on for real terminals, off in tests).
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from everbot.allocation import Allocation
from everbot.comparison import CostComparison, compare_levels
from everbot.errors import EverBotError, InvalidRobotCountError, InvalidWorkHoursError
from everbot.robots import ROBOT_TYPES

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"


def _c(text: str, *codes: str, color: bool) -> str:
    if not color or not codes:
        return text
    return f"{''.join(codes)}{text}{_RESET}"


def _rule(*, color: bool) -> str:
    return _c("\u2500" * 42, _DIM, color=color)


def _heading(title: str, *, color: bool) -> list[str]:
    return [
        _rule(color=color),
        _c(f"  {title}", _BOLD, _CYAN, color=color),
        _rule(color=color),
    ]


def read_inventory(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    color: bool = False,
) -> dict[str, int]:
    """Prompt for the available count of each robot type."""
    output_fn(_c("Enter number of robots available:", _BOLD, color=color))
    inventory: dict[str, int] = {}
    for rt in ROBOT_TYPES:
        raw = input_fn(f"{rt.name}: ").strip()
        try:
            inventory[rt.name] = int(raw)
        except ValueError:
            raise InvalidRobotCountError() from None
    return inventory


def read_hours(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    color: bool = False,
) -> int:
    """Prompt for the client's requested work hours."""
    output_fn("")
    output_fn(_c("Enter client work hours:", _BOLD, color=color))
    raw = input_fn("").strip()
    try:
        return int(raw)
    except ValueError:
        raise InvalidWorkHoursError() from None


def format_allocation(allocation: Allocation, *, color: bool = False) -> str:
    """Render a Level 1-style allocation (all categories, including zeros)."""
    lines = _heading("Robot Assignment", color=color)
    lines.append("")
    for rt in ROBOT_TYPES:
        lines.append(f"  {rt.name}: {allocation.counts[rt.name]}")
    lines.append("")
    lines.append(f"  Total Work Hours Provided: {allocation.provided_hours}")
    lines.append(f"  Client Work Hours Requested: {allocation.requested_hours}")
    return "\n".join(lines)


def format_cost_allocation(allocation: Allocation, *, color: bool = False) -> str:
    """Render a Level 2 cost-optimised allocation (positive counts only).

    Header wording matches the owner examples ("Cost Optimized Allocation").
    """
    lines = _heading("Cost Optimized Allocation", color=color)
    lines.append("")
    for rt in ROBOT_TYPES:
        count = allocation.counts.get(rt.name, 0)
        if count > 0:
            lines.append(f"  {rt.name}: {count}")
    lines.append("")
    lines.append(f"  Total Hours Provided: {allocation.provided_hours}")
    cost = f"  Total Charging Cost: ${allocation.total_cost}"
    lines.append(_c(cost, _BOLD, _GREEN, color=color))
    return "\n".join(lines)


def format_comparison(comparison: CostComparison, *, color: bool = False) -> str:
    """Render the Level 1 vs Level 2 cost comparison block."""
    lines = _heading("Level 1 vs Level 2", color=color)
    lines.append("")

    if comparison.level1 is None:
        lines.append(_c("  Level 1: infeasible", _YELLOW, color=color))
        if comparison.level1_error:
            lines.append(f"  {comparison.level1_error}")
        lines.append(f"  Level 2 Cost: ${comparison.level2_cost}")
        lines.append("")
        lines.append(
            "  Insight: Level 1 could not allocate under its mandatory diversity "
            "rules; Level 2 succeeded by optimising for cost alone."
        )
        return "\n".join(lines)

    assert comparison.cost_difference is not None
    diff = comparison.cost_difference
    lines.append(f"  Level 1 Cost: ${comparison.level1_cost}")
    lines.append(f"  Level 2 Cost: ${comparison.level2_cost}")
    diff_line = f"  Cost Difference: ${diff}"
    if diff > 0:
        lines.append(_c(diff_line, _BOLD, _GREEN, color=color))
        lines.append("")
        lines.append(
            f"  Insight: Level 1 strategy resulted in ${diff} additional cost "
            "due to mandatory usage of multiple robot categories"
        )
    elif diff == 0:
        lines.append(diff_line)
        lines.append("")
        lines.append(
            "  Insight: Level 1 and Level 2 incurred the same charging cost "
            "for this request"
        )
    else:
        lines.append(_c(diff_line, _YELLOW, color=color))
        lines.append("")
        lines.append(
            f"  Insight: Level 2 cost ${comparison.level2_cost} vs Level 1 "
            f"${comparison.level1_cost} (difference ${diff})"
        )
    return "\n".join(lines)


def run(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run one interactive allocation showing Level 2 and L1/L2 comparison.

    Returns a process exit code (0 ok, 1 error).
    Colour defaults off so unit tests see plain text; ``main`` enables it on TTYs.
    """
    try:
        inventory = read_inventory(input_fn, output_fn, color=color)
        hours = read_hours(input_fn, output_fn, color=color)
        comparison = compare_levels(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1

    output_fn("")
    output_fn(format_cost_allocation(comparison.level2, color=color))
    output_fn("")
    output_fn(format_comparison(comparison, color=color))
    output_fn("")
    return 0


def main() -> int:
    return run(color=sys.stdout.isatty())


if __name__ == "__main__":
    raise SystemExit(main())
