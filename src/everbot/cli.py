"""Interactive command-line interface for the EverBot allocation system.

Input/output format matches ``features/level-1.md``. The core functions take
injectable ``input_fn`` / ``output_fn`` so the flow is easy to unit-test.
"""

from collections.abc import Callable

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.errors import EverBotError, InvalidRobotCountError, InvalidWorkHoursError
from everbot.robots import ROBOT_TYPES
from everbot.strategies.base import AllocationStrategy
from everbot.strategies.category_distribution import CategoryDistributionStrategy


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
    """Render an allocation in the required output format."""
    lines = ["Robot Assignment", ""]
    for rt in ROBOT_TYPES:
        lines.append(f"{rt.name}: {allocation.counts[rt.name]}")
    lines.append("")
    lines.append(f"Total Work Hours Provided: {allocation.provided_hours}")
    lines.append(f"Client Work Hours Requested: {allocation.requested_hours}")
    return "\n".join(lines)


def run(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    strategy: AllocationStrategy | None = None,
) -> int:
    """Run one interactive allocation. Returns a process exit code (0 ok, 1 error)."""
    allocator = Allocator(strategy or CategoryDistributionStrategy())
    try:
        inventory = read_inventory(input_fn, output_fn)
        hours = read_hours(input_fn, output_fn)
        allocation = allocator.allocate(inventory, hours)
    except EverBotError as err:
        output_fn("")
        output_fn(str(err))
        return 1

    output_fn("")
    output_fn(format_allocation(allocation))
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
