"""Tests for the Level 2 cost-optimised allocation strategy."""

import pytest

from everbot import Allocator, CostOptimisedStrategy, allocate, compare_levels
from everbot.errors import (
    InsufficientCapacityError,
    InvalidRobotCountError,
    InvalidWorkHoursError,
    NoRobotsError,
)
from everbot.strategies import STRATEGY_BY_LEVEL, strategy_for_level


def _allocator():
    return Allocator(CostOptimisedStrategy())


def _counts(alloc):
    return (alloc.count_of("Bravo"), alloc.count_of("Charlie"), alloc.count_of("Delta"))


def test_owner_example_1():
    # Inventory Bravo:2 Charlie:3 Delta:2, hours 20 -> Charlie:1 Delta:2, 21h, $11
    alloc = _allocator().allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 20)
    assert _counts(alloc) == (0, 1, 2)
    assert alloc.provided_hours == 21
    assert alloc.total_cost == 11


def test_owner_example_2():
    # Inventory Bravo:2 Charlie:2 Delta:3, hours 6 -> Bravo:2, 6h, $4
    # (beats same-cost 1 Delta @ 8h via min-excess tiebreak)
    alloc = _allocator().allocate({"Bravo": 2, "Charlie": 2, "Delta": 3}, 6)
    assert _counts(alloc) == (2, 0, 0)
    assert alloc.provided_hours == 6
    assert alloc.total_cost == 4


def test_prefers_cheaper_delta_over_diverse_mix():
    # 16h: 2 Delta ($8) beats L1-style 1/1/1 ($9)
    alloc = _allocator().allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 16)
    assert _counts(alloc) == (0, 0, 2)
    assert alloc.total_cost == 8


def test_allows_missing_category():
    # No Bravo available — Level 2 still allocates Charlie+Delta.
    alloc = _allocator().allocate({"Bravo": 0, "Charlie": 3, "Delta": 2}, 20)
    assert _counts(alloc) == (0, 1, 2)
    assert alloc.total_cost == 11


def test_single_type_when_sufficient():
    alloc = _allocator().allocate({"Bravo": 0, "Charlie": 0, "Delta": 3}, 16)
    assert _counts(alloc) == (0, 0, 2)
    assert alloc.provided_hours == 16
    assert alloc.total_cost == 8


def test_min_excess_before_fewest_robots():
    # Same min cost ($4): 2 Bravo (excess 0, 2 robots) beats 1 Delta (excess 2, 1 robot).
    alloc = _allocator().allocate({"Bravo": 2, "Charlie": 2, "Delta": 3}, 6)
    assert _counts(alloc) == (2, 0, 0)


def test_fewest_robots_after_cost_and_excess():
    # Exact 8h: 1 Delta (cost 4, 1 robot) beats 1B+1C (cost 5) and would beat
    # any same-cost multi-robot exact solution if one existed.
    alloc = _allocator().allocate({"Bravo": 5, "Charlie": 5, "Delta": 5}, 8)
    assert _counts(alloc) == (0, 0, 1)
    assert alloc.total_cost == 4


def test_strategy_registered_as_level_2():
    assert STRATEGY_BY_LEVEL[2] is CostOptimisedStrategy
    assert isinstance(strategy_for_level(2), CostOptimisedStrategy)


def test_convenience_allocate_with_strategy():
    expected = _allocator().allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 20)
    assert allocate({"Bravo": 2, "Charlie": 3, "Delta": 2}, 20, CostOptimisedStrategy()) == expected


def test_always_provides_at_least_requested():
    inv = {"Bravo": 10, "Charlie": 10, "Delta": 10}
    for hours in range(1, 60):
        alloc = _allocator().allocate(inv, hours)
        assert alloc.provided_hours >= hours


# --- comparison -------------------------------------------------------------


def test_comparison_owner_example_1():
    comparison = compare_levels({"Bravo": 2, "Charlie": 3, "Delta": 2}, 20)
    assert _counts(comparison.level2) == (0, 1, 2)
    assert comparison.level2_cost == 11
    assert comparison.level1 is not None
    assert comparison.level1_cost == 12
    assert comparison.cost_difference == 1


def test_comparison_when_level1_infeasible():
    # Missing Bravo: Level 1 fails, Level 2 succeeds.
    comparison = compare_levels({"Bravo": 0, "Charlie": 3, "Delta": 2}, 20)
    assert comparison.level1 is None
    assert comparison.level1_error is not None
    assert "each category" in comparison.level1_error
    assert comparison.level2_cost == 11
    assert comparison.cost_difference is None


# --- error paths ------------------------------------------------------------


@pytest.mark.parametrize("hours", [0, -1, 1.5, "16", None, True])
def test_invalid_hours(hours):
    with pytest.raises(InvalidWorkHoursError):
        _allocator().allocate({"Bravo": 2, "Charlie": 2, "Delta": 2}, hours)


def test_zero_robots():
    with pytest.raises(NoRobotsError):
        _allocator().allocate({"Bravo": 0, "Charlie": 0, "Delta": 0}, 10)


def test_insufficient_capacity():
    with pytest.raises(InsufficientCapacityError):
        _allocator().allocate({"Bravo": 1, "Charlie": 0, "Delta": 0}, 10)


def test_invalid_robot_counts():
    with pytest.raises(InvalidRobotCountError):
        _allocator().allocate({"Bravo": -1, "Charlie": 1, "Delta": 1}, 10)
