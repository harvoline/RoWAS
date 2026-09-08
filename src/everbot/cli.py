"""Interactive command-line interface for the EverBot allocation system.

Top-level menu selects Levels 1-4 or optional advanced features; separate runners ensure
logics do not collide. Colour is optional (on for real terminals, off in tests).
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from everbot.advanced import AdvancedPlan, plan_advanced
from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.comparison import CostComparison, compare_levels
from everbot.errors import EverBotError, InvalidRobotCountError, InvalidWorkHoursError
from everbot.multiclient import MultiClientPlan, parse_client_hours, plan_multi_client
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


def read_client_hours(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    color: bool = False,
) -> list[int]:
    """Prompt for one or more clients' work hours on a single line."""
    output_fn("")
    output_fn(
        _c(
            "Enter client working hours (single, comma, or space separated):",
            _BOLD,
            color=color,
        )
    )
    raw = input_fn("Client working hours: ")
    return parse_client_hours(raw)


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


def _standby_lines(allocation: Allocation, indent: str, *, color: bool) -> list[str]:
    """Render the winning standby robots, one coloured line per robot type."""
    lines: list[str] = []
    for rt in ROBOT_TYPES:
        count = allocation.count_of(rt.name)
        if count <= 0:
            continue
        line = f"{indent}{rt.name}: {count} - cost ${count * rt.cost}"
        robot_colour = _ROBOT_COLOURS.get(rt.name, "")
        lines.append(_c(line, robot_colour, color=color) if robot_colour else line)
    return lines


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
    lines.extend(_standby_lines(plan.additional, "  ", color=color))
    return "\n".join(lines)


def format_multi_client_plan(plan: MultiClientPlan, *, color: bool = False) -> str:
    """Render Level 4: shared active capacity, then each client in service order."""
    lines = _heading("Multi-Client Allocation", color=color)
    lines.append("")
    lines.append(f"  Active Robot Capacity: {plan.active_capacity} hours")
    lines.append(f"  Clients: {plan.client_count} (served highest hours first)")

    for client in plan.clients:
        lines.append("")
        lines.append(
            _c(
                f"  Client {client.number}: {client.requested_hours} hours requested",
                _BOLD,
                color=color,
            )
        )
        if client.allocated is not None:
            assigned = ", ".join(
                f"{rt.name}: {client.allocated.count_of(rt.name)}"
                for rt in ROBOT_TYPES
                if client.allocated.count_of(rt.name) > 0
            )
            lines.append(
                f"    Active Robots Allocated: {assigned} "
                f"({client.allocated.provided_hours} hours)"
            )
        if client.additional is not None:
            lines.append(_c("    Additional Standby Robots Required:", _BOLD, color=color))
            lines.extend(_standby_lines(client.additional, "      ", color=color))

    lines.append("")
    total = f"  Total Standby Cost: ${plan.total_standby_cost}"
    lines.append(_c(total, _BOLD, _GREEN, color=color))
    return "\n".join(lines)


def format_advanced_summary(summary: AdvancedPlan, *, color: bool = False) -> str:
    """Render planned totals and two distinct utilization measures."""
    lines = _heading("Allocation Summary", color=color)
    lines.extend([
        "  Planned totals include recommended standby robots.",
        f"  Total Robots Used: {summary.total_robots} "
        f"(active {summary.active.total_robots}, standby {summary.standby.total_robots})",
        f"  Total Charging Cost: ${summary.total_cost} "
        f"(active ${summary.active.total_cost}, standby ${summary.standby.total_cost})",
        f"  Requested Hours: {summary.plan.total_requested_hours}",
        f"  Assigned Capacity: {summary.provided_hours} hours",
        f"  Avg Robot Utilization: {float(summary.utilization):.2f}%",
        "", "  Efficiency Metrics", "  Useful work is estimated proportionally per client.",
    ])
    for metric in summary.metrics:
        usage = metric.inventory_usage
        utilization = metric.capacity_utilization
        usage_text = "N/A" if usage is None else f"{float(usage):.2f}%"
        capacity_text = "N/A" if utilization is None else f"{float(utilization):.2f}%"
        lines.append(
            f"  {metric.name} Active Inventory Usage: "
            f"{metric.active_used}/{metric.available} ({usage_text})"
        )
        lines.append(f"  {metric.name} Estimated Useful Working Capacity: {capacity_text}")
    return "\n".join(lines)


def read_level_choice(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    color: bool = False,
) -> int:
    """Prompt for Levels 1-4 or optional advanced features (option 5)."""
    output_fn(_c("Select allocation level:", _BOLD, color=color))
    output_fn("  1. Level 1 — Robot Category Distribution")
    output_fn("  2. Level 2 — Cost Optimised Allocation")
    output_fn("  3. Level 3 — Standby Robot Activation")
    output_fn("  4. Level 4 — Multi-Client Allocation")
    output_fn("  5. Optional Advanced Features")
    output_fn("")
    raw = input_fn("Choice (1/2/3/4/5): ").strip()
    if raw not in {"1", "2", "3", "4", "5"}:
        raise EverBotError("Error: Please choose option 1, 2, 3, 4, or 5.")
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


def run_level_4(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run Level 4 multi-client allocation over one shared active inventory."""
    try:
        inventory = read_inventory(input_fn, output_fn, color=color)
        hours = read_client_hours(input_fn, output_fn, color=color)
        plan = plan_multi_client(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1

    output_fn("")
    output_fn(format_multi_client_plan(plan, color=color))
    output_fn("")
    return 0


def run_advanced(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Run multi-client allocation with an optional advanced summary."""
    try:
        inventory = read_inventory(input_fn, output_fn, color=color)
        hours = read_client_hours(input_fn, output_fn, color=color)
        summary = plan_advanced(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(_c(str(err), _BOLD, _RED, color=color))
        return 1
    output_fn("")
    output_fn(format_multi_client_plan(summary.plan, color=color))
    output_fn("")
    output_fn(format_advanced_summary(summary, color=color))
    output_fn("")
    return 0


def run(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    *,
    color: bool = False,
) -> int:
    """Show Levels 1-4 and optional advanced features, then dispatch.

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
    if level == 3:
        return run_level_3(input_fn, output_fn, color=color)
    if level == 4:
        return run_level_4(input_fn, output_fn, color=color)
    return run_advanced(input_fn, output_fn, color=color)


def main() -> int:
    """Run the terminal session, handling EOF and user cancellation once."""
    try:
        return run(color=sys.stdout.isatty())
    except EOFError:
        print("\nError: Input ended before allocation completed.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAllocation cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
