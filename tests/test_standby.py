"""Tests for Level 3 standby robot activation."""

import pytest

from everbot.errors import (
    InvalidRobotCountError,
    InvalidWorkHoursError,
)
from everbot.standby import plan_standby


def _counts(alloc):
    return (alloc.count_of("Bravo"), alloc.count_of("Charlie"), alloc.count_of("Delta"))


def test_owner_example_shortfall_charlie():
    # Active 1/1/1 = 16h, request 21 → shortfall 5 → Charlie:1 @ $3
    plan = plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, 21)
    assert plan.active_capacity == 16
    assert plan.requested_hours == 21
    assert plan.shortfall == 5
    assert plan.additional is not None
    assert _counts(plan.additional) == (0, 1, 0)
    assert plan.additional.total_cost == 3
    assert plan.additional.provided_hours >= 5


def test_no_additional_when_capacity_covers():
    plan = plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, 16)
    assert plan.active_capacity == 16
    assert plan.requested_hours == 16
    assert plan.additional is None
    assert plan.shortfall == 0


def test_no_additional_when_capacity_exceeds_request():
    plan = plan_standby({"Bravo": 2, "Charlie": 2, "Delta": 2}, 10)
    assert plan.active_capacity == 32
    assert plan.additional is None


def test_uses_full_active_capacity_before_standby():
    # Capacity 16, request 24 → shortfall 8 → Delta:1 @ $4 (not allocating as if from zero)
    plan = plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, 24)
    assert plan.active_capacity == 16
    assert plan.shortfall == 8
    assert plan.additional is not None
    assert _counts(plan.additional) == (0, 0, 1)
    assert plan.additional.total_cost == 4


def test_unbounded_ignores_active_inventory_for_standby_search():
    # Only 1 Bravo active (3h); request 20 → shortfall 17; standby may use many Deltas.
    plan = plan_standby({"Bravo": 1, "Charlie": 0, "Delta": 0}, 20)
    assert plan.active_capacity == 3
    assert plan.shortfall == 17
    assert plan.additional is not None
    assert plan.additional.provided_hours >= 17


def test_zero_active_covered_entirely_by_standby():
    plan = plan_standby({"Bravo": 0, "Charlie": 0, "Delta": 0}, 8)
    assert plan.active_capacity == 0
    assert plan.additional is not None
    assert _counts(plan.additional) == (0, 0, 1)
    assert plan.additional.total_cost == 4


def test_min_cost_objective_on_shortfall():
    # Shortfall 6: 2 Bravo ($4, exact) beats 1 Delta ($4, excess 2) via min-excess.
    plan = plan_standby({"Bravo": 0, "Charlie": 0, "Delta": 0}, 6)
    assert plan.additional is not None
    assert _counts(plan.additional) == (2, 0, 0)
    assert plan.additional.total_cost == 4


@pytest.mark.parametrize("hours", [0, -1, 1.5, "16", None, True])
def test_invalid_hours(hours):
    with pytest.raises(InvalidWorkHoursError):
        plan_standby({"Bravo": 1, "Charlie": 1, "Delta": 1}, hours)


def test_invalid_robot_counts():
    with pytest.raises(InvalidRobotCountError):
        plan_standby({"Bravo": -1, "Charlie": 1, "Delta": 1}, 10)
