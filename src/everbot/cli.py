"""Interactive command-line interface for the EverBot allocation system.

Input/output format matches ``features/level-1.md`` and ``features/level-2.md``.
The core functions take injectable ``input_fn`` / ``output_fn`` so the flow is
easy to unit-test.
"""

from collections.abc import Callable

from everbot.allocation import Allocation
from everbot.comparison import CostComparison, compare_levels
from everbot.errors import EverBotError, InvalidRobotCountError, InvalidWorkHoursError
from everbot.robots import ROBOT_TYPES


def read_inventory(
    input_fn: Callable[[str], str], output_fn: Callable[[str], None]
) -> dict[str, int]:
    """Prompt for the available count of each robot type."""
    output_fn("Enter number of robots available:")
    inventory: dict[str, int] = {}
    for rt in ROBOT_TYPES:
        raw = input_fn(f"{rt.name}: ").strip()
        try:
            inventory[rt.name] = int(raw)
        except ValueError:
            raise InvalidRobotCountError() from None
    return inventory


def read_hours(input_fn: Callable[[str], str], output_fn: Callable[[str], None]) -> int:
    """Prompt for the client's requested work hours."""
    output_fn("")
    output_fn("Enter client work hours:")
    raw = input_fn("").strip()
    try:
        return int(raw)
    except ValueError:
        raise InvalidWorkHoursError() from None


def format_allocation(allocation: Allocation) -> str:
    """Render a Level 1-style allocation (all categories, including zeros)."""
    lines = ["Robot Assignment", ""]
    for rt in ROBOT_TYPES:
        lines.append(f"{rt.name}: {allocation.counts[rt.name]}")
    lines.append("")
    lines.append(f"Total Work Hours Provided: {allocation.provided_hours}")
    lines.append(f"Client Work Hours Requested: {allocation.requested_hours}")
    return "\n".join(lines)


def format_cost_allocation(allocation: Allocation) -> str:
    """Render a Level 2 cost-optimised allocation (positive counts only).

    Header wording matches the owner examples (\"Cost Optimized Allocation\").
    """
    lines = ["Cost Optimized Allocation"]
    for rt in ROBOT_TYPES:
        count = allocation.counts.get(rt.name, 0)
        if count > 0:
            lines.append(f"{rt.name}: {count}")
    lines.append(f"Total Hours Provided: {allocation.provided_hours}")
    lines.append(f"Total Charging Cost: ${allocation.total_cost}")
    return "\n".join(lines)


def format_comparison(comparison: CostComparison) -> str:
    """Render the Level 1 vs Level 2 cost comparison block."""
    lines: list[str] = ["Level 1 vs Level 2 Cost Comparison", ""]
    if comparison.level1 is None:
        lines.append("Level 1: infeasible")
        if comparison.level1_error:
            lines.append(comparison.level1_error)
        lines.append(f"Level 2 Cost: ${comparison.level2_cost}")
        lines.append(
            "Insight: Level 1 could not allocate under its mandatory diversity "
            "rules; Level 2 succeeded by optimising for cost alone."
        )
        return "\n".join(lines)

    assert comparison.cost_difference is not None
    diff = comparison.cost_difference
    lines.append(f"Level 1 Cost: ${comparison.level1_cost}")
    lines.append(f"Level 2 Cost: ${comparison.level2_cost}")
    lines.append(f"Cost Difference: ${diff}")
    if diff > 0:
        lines.append(
            f"Insight: Level 1 strategy resulted in ${diff} additional cost "
            "due to mandatory usage of multiple robot categories"
        )
    elif diff == 0:
        lines.append(
            "Insight: Level 1 and Level 2 incurred the same charging cost "
            "for this request"
        )
    else:
        # Unexpected (L2 is min-cost without diversity), but stay honest.
        lines.append(
            f"Insight: Level 2 cost ${comparison.level2_cost} vs Level 1 "
            f"${comparison.level1_cost} (difference ${diff})"
        )
    return "\n".join(lines)


def run(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    """Run one interactive allocation showing Level 2 and L1/L2 comparison.

    Returns a process exit code (0 ok, 1 error).
    """
    try:
        inventory = read_inventory(input_fn, output_fn)
        hours = read_hours(input_fn, output_fn)
        comparison = compare_levels(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(str(err))
        return 1

    output_fn("")
    output_fn(format_cost_allocation(comparison.level2))
    output_fn("")
    output_fn(format_comparison(comparison))
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
