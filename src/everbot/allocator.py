"""The :class:`Allocator` service: universal validation, then strategy delegation.

The Allocator enforces the rules that hold for *every* level (valid work hours,
valid robot counts, at least one robot present) and then hands off to a pluggable
:class:`~everbot.strategies.base.AllocationStrategy`. This keeps the shared rules
in one place and lets each level vary only its own algorithm.
"""

from collections.abc import Mapping

from everbot.allocation import Allocation
from everbot.errors import (
    InvalidRobotCountError,
    InvalidWorkHoursError,
    NoRobotsError,
)
from everbot.robots import ROBOT_NAMES
from everbot.strategies.base import AllocationStrategy
from everbot.strategies.category_distribution import CategoryDistributionStrategy


class Allocator:
    """Runs the universal rules, then delegates to the configured strategy."""

    def __init__(self, strategy: AllocationStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> AllocationStrategy:
        return self._strategy

    def allocate(self, inventory: Mapping[str, object], requested_hours: object) -> Allocation:
        self.validate_hours(requested_hours)
        assert isinstance(requested_hours, int)  # narrowed by validate_hours
        available = self.validate_inventory(inventory)

        if sum(available.values()) == 0:
            raise NoRobotsError()

        return self._strategy.allocate(available, requested_hours)

    @staticmethod
    def validate_hours(hours: object) -> None:
        # Strictly a positive integer (reject bools, floats, strings, None).
        if isinstance(hours, bool) or not isinstance(hours, int) or hours <= 0:
            raise InvalidWorkHoursError()

    @staticmethod
    def validate_inventory(inventory: Mapping[str, object]) -> dict[str, int]:
        # Non-negative integers only; unknown keys ignored, missing default to 0.
        available: dict[str, int] = {}
        for name in ROBOT_NAMES:
            count: object = inventory.get(name, 0)
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise InvalidRobotCountError()
            available[name] = count
        return available


def allocate(
    inventory: Mapping[str, object],
    requested_hours: object,
    strategy: AllocationStrategy | None = None,
) -> Allocation:
    """Convenience wrapper: allocate using ``strategy`` (defaults to category distribution)."""
    if strategy is None:
        strategy = CategoryDistributionStrategy()
    return Allocator(strategy).allocate(inventory, requested_hours)
