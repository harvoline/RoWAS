"""Tests for the Level 1 category-distribution allocation strategy."""

import pytest

from everbot import Allocator, CategoryDistributionStrategy, allocate
from everbot.errors import (
    InsufficientCapacityError,
    InvalidRobotCountError,
    InvalidWorkHoursError,
    MissingCategoryError,
    NoRobotsError,
)

GENEROUS = {"Bravo": 10, "Charlie": 10, "Delta": 10}


def _allocator():
    return Allocator(CategoryDistributionStrategy())


def _counts(alloc):
    return (alloc.count_of("Bravo"), alloc.count_of("Charlie"), alloc.count_of("Delta"))


@pytest.mark.parametrize(
    "hours, expected, provided, excess",
    [
        (16, (1, 1, 1), 16, 0),  # base case (CLI example)
        (17, (2, 1, 1), 19, 2),  # +Bravo minimises excess
        (21, (1, 2, 1), 21, 0),  # +Charlie exact
        (24, (1, 1, 2), 24, 0),  # +Delta exact; beats 2/2/1 on fewest robots
        (22, (3, 1, 1), 22, 0),  # global-min-excess beats 1/1/2 (excess 2)
        (10, (1, 1, 1), 16, 6),  # diversity mandatory below 16h
    ],
)
def test_worked_examples(hours, expected, provided, excess):
    alloc = _allocator().allocate(GENEROUS, hours)
    assert _counts(alloc) == expected
    assert alloc.provided_hours == provided
    assert alloc.excess_hours == excess
    assert alloc.requested_hours == hours


def test_convenience_function_matches_allocator():
    assert allocate(GENEROUS, 24) == _allocator().allocate(GENEROUS, 24)


def test_fewest_robots_tiebreak_at_24():
    # 1/1/2 (=24, 4 robots) must beat 2/2/1 (=24, 5 robots); both excess 0.
    alloc = _allocator().allocate(GENEROUS, 24)
    assert _counts(alloc) == (1, 1, 2)
    assert alloc.total_robots == 4


def test_global_min_excess_prefers_more_small_robots():
    # 22h: 3/1/1 (excess 0) is chosen over 1/1/2 (excess 2).
    alloc = _allocator().allocate(GENEROUS, 22)
    assert alloc.excess_hours == 0


def test_total_cost_is_exposed():
    # 24h -> 1 Bravo ($2) + 1 Charlie ($3) + 2 Delta ($8) = $13.
    alloc = _allocator().allocate(GENEROUS, 24)
    assert alloc.total_cost == 2 + 3 + 2 * 4


def test_respects_inventory_caps():
    alloc = _allocator().allocate({"Bravo": 1, "Charlie": 1, "Delta": 1}, 16)
    assert _counts(alloc) == (1, 1, 1)


def test_always_provides_at_least_requested():
    for hours in range(1, 60):
        alloc = _allocator().allocate(GENEROUS, hours)
        assert alloc.provided_hours >= hours
        assert all(alloc.count_of(n) >= 1 for n in ("Bravo", "Charlie", "Delta"))


# --- error paths -----------------------------------------------------------

@pytest.mark.parametrize("hours", [0, -1, -100])
def test_non_positive_hours(hours):
    with pytest.raises(InvalidWorkHoursError):
        _allocator().allocate(GENEROUS, hours)


@pytest.mark.parametrize("hours", [1.5, "16", None, True, False])
def test_non_integer_hours(hours):
    with pytest.raises(InvalidWorkHoursError):
        _allocator().allocate(GENEROUS, hours)


def test_zero_robots():
    with pytest.raises(NoRobotsError):
        _allocator().allocate({"Bravo": 0, "Charlie": 0, "Delta": 0}, 10)


def test_empty_inventory_is_zero_robots():
    with pytest.raises(NoRobotsError):
        _allocator().allocate({}, 10)


@pytest.mark.parametrize(
    "inventory",
    [
        {"Bravo": 0, "Charlie": 2, "Delta": 2},
        {"Bravo": 2, "Charlie": 0, "Delta": 2},
        {"Bravo": 2, "Charlie": 2, "Delta": 0},
    ],
)
def test_missing_category(inventory):
    with pytest.raises(MissingCategoryError):
        _allocator().allocate(inventory, 10)


def test_insufficient_capacity():
    # Max hours = 3 + 5 + 8 = 16 < 17.
    with pytest.raises(InsufficientCapacityError):
        _allocator().allocate({"Bravo": 1, "Charlie": 1, "Delta": 1}, 17)


@pytest.mark.parametrize(
    "inventory",
    [
        {"Bravo": -1, "Charlie": 1, "Delta": 1},
        {"Bravo": 1, "Charlie": 1.5, "Delta": 1},
        {"Bravo": 1, "Charlie": 1, "Delta": "2"},
    ],
)
def test_invalid_robot_counts(inventory):
    with pytest.raises(InvalidRobotCountError):
        _allocator().allocate(inventory, 10)


def test_missing_category_takes_priority_over_insufficient():
    # Bravo absent AND total capacity short -> missing-category wins (spec order).
    with pytest.raises(MissingCategoryError):
        _allocator().allocate({"Bravo": 0, "Charlie": 1, "Delta": 1}, 100)


def test_error_messages_are_exact():
    from everbot import errors

    assert str(NoRobotsError()) == errors.MSG_NO_ROBOTS
    assert str(MissingCategoryError()) == errors.MSG_MISSING_CATEGORY
    assert str(InsufficientCapacityError()) == errors.MSG_INSUFFICIENT_CAPACITY
    assert str(InvalidWorkHoursError()) == errors.MSG_INVALID_WORK_HOURS
