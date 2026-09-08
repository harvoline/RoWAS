"""Level 3 — Standby Robot Activation workflow.

Uses full active capacity first. When requested hours exceed active capacity,
recommends a cost-optimised set of additional standby robots to activate/buy.
There is no standby inventory — the fill search is unbounded by stock.

See ``features/level-3.md``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import ceil

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.errors import InsufficientCapacityError
from everbot.robots import ROBOT_TYPES, Robot
from everbot.strategies.cost_optimised import CostOptimisedStrategy


@dataclass(frozen=True)
class StandbyPlan:
    """Result of a Level 3 standby planning pass."""

    active_capacity: int
    requested_hours: int
    additional: Allocation | None
    """Winning standby allocation for the shortfall, or None when capacity covers."""

    @property
    def shortfall(self) -> int:
        return max(0, self.requested_hours - self.active_capacity)


def active_capacity_hours(inventory: Mapping[str, int]) -> int:
    """Total working hours available from the active robot inventory."""
    return sum(robot.hours * inventory.get(robot.name, 0) for robot in ROBOT_TYPES)


def _unbounded_caps(shortfall: int) -> dict[str, int]:
    """Enough of each type to cover ``shortfall`` alone, plus a small margin."""

    def cap(robot: Robot) -> int:
        return ceil(shortfall / robot.hours) + 1

    return {robot.name: cap(robot) for robot in ROBOT_TYPES}


def _fill_shortfall(shortfall: int) -> Allocation:
    """Cost-optimised fill of ``shortfall`` hours with no inventory caps."""
    if shortfall <= 0:
        raise ValueError("shortfall must be positive")
    available = _unbounded_caps(shortfall)
    # Reuse Level 2 objective via CostOptimisedStrategy (no diversity mandate).
    try:
        return CostOptimisedStrategy().allocate(available, shortfall)
    except InsufficientCapacityError:
        # Should not arise with unbounded caps; re-raise for a clear CLI path.
        raise


def plan_standby(
    active_inventory: Mapping[str, object], requested_hours: object
) -> StandbyPlan:
    """Plan Level 3 standby activation for active inventory + requested hours.

    Validates hours and active counts via the shared Allocator rules (using a
    throwaway Level 2 strategy call only for validation when capacity is enough,
    or validating inventory/hours explicitly).

    Raises:
        EverBotError: invalid hours/counts; or insufficient capacity if the
            shortfall somehow cannot be covered.
    """
    # Validate hours + inventory without requiring robots present (zero active
    # is allowed — standby can cover the whole request).
    Allocator._validate_hours(requested_hours)
    assert isinstance(requested_hours, int)
    available = Allocator._validate_inventory(active_inventory)

    capacity = active_capacity_hours(available)
    if capacity >= requested_hours:
        return StandbyPlan(
            active_capacity=capacity,
            requested_hours=requested_hours,
            additional=None,
        )

    shortfall = requested_hours - capacity
    additional = _fill_shortfall(shortfall)
    return StandbyPlan(
        active_capacity=capacity,
        requested_hours=requested_hours,
        additional=additional,
    )
