"""Interactive command-line interface for the EverBot allocation system.

Top-level menu selects Level 1, 2, or 3; each level has a separate runner so
logics do not collide. Colour is optional (on for real terminals, off in tests).
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.comparison import CostComparison, compare_levels
from everbot.errors import EverBotError, InvalidRobotCountError, InvalidWorkHoursError
from everbot.robots import ROBOT_TYPES
from everbot.standby import StandbyPlan, plan_standby
from everbot.strategies.category_distribution import CategoryDistributionStrategy

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"

# Distinct colours per robot type (Level 3 additional lines).
_ROBOT_COLOURS: dict[str, str] = {
    "Bravo": _BLUE,
    "Charlie": _MAGENTA,
    "Delta": _YELLOW,
}


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


def format_standby_plan(plan: StandbyPlan, *, color: bool = False) -> str:
    """Render Level 3 capacity + optional winning additional standby block."""
    lines = _heading("Standby Robot Activation", color=color)
    lines.append("")
    lines.append(f"  Active Robot Capacity: {plan.active_capacity} hours")
    lines.append(f"  Client Work Requested: {plan.requested_hours} hours")
    if plan.additional is None:
        return "\n".join(lines)

    lines.append("")
    lines.append(_c("  Additional Standby Robots Required:", _BOLD, color=color))
    for rt in ROBOT_TYPES:
        count = plan.additional.count_of(rt.name)
        if count <= 0:
            continue
        line_cost = count * rt.cost
        line = f"  {rt.name}: {count} - cost ${line_cost}"
        robot_colour = _ROBOT_COLOURS.get(rt.name, "")
        if robot_colour:
            lines.append(_c(line, robot_colour, color=color))
        else:
            lines.append(line)
    return "\n".join(lines)


def read_level_choice(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    color: bool = False,
) -> int:
    """Prompt for Level 1, 2, or 3. Returns the chosen level number."""
    output_fn(_c("Select allocation level:", _BOLD, color=color))
    output_fn("  1. Level 1 — Robot Category Distribution")
    output_fn("  2. Level 2 — Cost Optimised Allocation")
    output_fn("  3. Level 3 — Standby Robot Activation")
    output_fn("")
    raw = input_fn("Choice (1/2/3): ").strip()
    if raw not in {"1", "2", "3"}:
        raise EverBotError("Error: Please choose level 1, 2, or 3.")
    return int(raw)


def run_level_1(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run Level 1 category-distribution assignment."""
    try:
        inventory = read_inventory(input_fn, output_fn, color=color)
        hours = read_hours(input_fn, output_fn, color=color)
        allocation = Allocator(CategoryDistributionStrategy()).allocate(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1

    output_fn("")
    output_fn(format_allocation(allocation, color=color))
    output_fn("")
    return 0


def run_level_2(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run Level 2 cost allocation and L1/L2 comparison."""
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


def run_level_3(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run Level 3 standby activation (active capacity + optional additional)."""
    try:
        inventory = read_inventory(input_fn, output_fn, color=color)
        hours = read_hours(input_fn, output_fn, color=color)
        plan = plan_standby(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1

    output_fn("")
    output_fn(format_standby_plan(plan, color=color))
    output_fn("")
    return 0


def run(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Show the Level 1/2/3 menu, then dispatch to the chosen runner.

    Returns a process exit code (0 ok, 1 error).
    Colour defaults off so unit tests see plain text; ``main`` enables it on TTYs.
    """
    try:
        level = read_level_choice(input_fn, output_fn, color=color)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1

    output_fn("")
    if level == 1:
        return run_level_1(input_fn, output_fn, color=color)
    if level == 2:
        return run_level_2(input_fn, output_fn, color=color)
    return run_level_3(input_fn, output_fn, color=color)


def main() -> int:
    return run(color=sys.stdout.isatty())


if __name__ == "__main__":
    raise SystemExit(main())
