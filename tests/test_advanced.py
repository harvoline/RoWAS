"""Advanced summary: totals, weighted estimates, empty categories, validation."""

from fractions import Fraction

import pytest

from everbot.advanced import plan_advanced
from everbot.errors import InvalidRobotCountError, InvalidWorkHoursError
from everbot.multiclient import plan_multi_client


def test_summary_includes_active_and_standby_without_changing_allocations():
    inventory = {"Bravo": 2, "Charlie": 3, "Delta": 2}
    hours = [12, 16, 17, 10, 21]
    result = plan_advanced(inventory, hours)
    assert result.plan == plan_multi_client(inventory, hours)
    assert result.active.total_robots == 7
    assert result.standby.total_robots == 7
    assert result.total_robots == 14
    assert result.active.total_cost == 21
    assert result.standby.total_cost == 23
    assert result.total_cost == 44
    # 37 active + (3 + 16 + 13 + 10) standby hours = 79.
    assert result.provided_hours == 79
    assert result.utilization == Fraction(7600, 79)
    assert sum(m.useful_hours for m in result.metrics) == 76
    assert inventory == {"Bravo": 2, "Charlie": 3, "Delta": 2}


def test_proportional_work_is_weighted_by_capacity_across_clients():
    # First client takes Delta (7/8), second takes Charlie (2/5).
    result = plan_advanced({"Bravo": 0, "Charlie": 2, "Delta": 1}, [2, 7])
    bravo, charlie, delta = result.metrics
    assert result.utilization == Fraction(900, 13)
    assert bravo.inventory_usage is None
    assert bravo.capacity_utilization is None
    assert charlie.inventory_usage == 50
    assert charlie.capacity_utilization == 40
    assert delta.inventory_usage == 100
    assert delta.capacity_utilization == Fraction(175, 2)
    assert result.standby.total_robots == 0


def test_available_but_unused_category_has_zero_inventory_usage():
    result = plan_advanced({"Bravo": 2, "Delta": 1}, [8])
    assert result.metrics[0].inventory_usage == 0
    assert result.metrics[0].capacity_utilization is None


def test_mixed_types_share_useful_work_proportionally():
    result = plan_advanced({"Bravo": 1, "Charlie": 1}, [7])
    bravo, charlie, delta = result.metrics
    assert bravo.useful_hours == Fraction(21, 8)
    assert charlie.useful_hours == Fraction(35, 8)
    assert bravo.capacity_utilization == charlie.capacity_utilization == Fraction(175, 2)
    assert delta.inventory_usage is None
    assert delta.capacity_utilization is None


def test_standby_does_not_count_as_active_inventory_usage():
    result = plan_advanced({}, [6, 8])
    assert result.active.total_robots == 0
    assert result.standby.total_robots == 3
    assert result.total_cost == 8
    assert result.utilization == 100
    assert all(m.inventory_usage is None for m in result.metrics)
    assert result.metrics[0].capacity_utilization == 100
    assert result.metrics[1].capacity_utilization is None


def test_mixed_active_and_standby_use_combined_client_capacity():
    # Bravo supplies 3 active hours; a standby Delta fills a 7-hour shortfall.
    result = plan_advanced({"Bravo": 1}, [10])
    bravo, _, delta = result.metrics
    assert bravo.useful_hours == Fraction(30, 11)
    assert delta.useful_hours == Fraction(80, 11)
    assert bravo.capacity_utilization == delta.capacity_utilization == Fraction(1000, 11)
    assert bravo.inventory_usage == 100
    assert delta.inventory_usage is None


def test_same_type_across_clients_is_capacity_weighted():
    # Two Charlies for 9h, one for 4h: 13/15, not mean(9/10, 4/5).
    result = plan_advanced({"Charlie": 3}, [4, 9])
    charlie = result.metrics[1]
    assert charlie.useful_hours == 13
    assert charlie.provided_hours == 15
    assert charlie.capacity_utilization == Fraction(260, 3)


@pytest.mark.parametrize("hours", [[], [0], [True], [1.5]])
def test_rejects_invalid_requests(hours):
    with pytest.raises(InvalidWorkHoursError):
        plan_advanced({}, hours)


def test_rejects_invalid_inventory():
    with pytest.raises(InvalidRobotCountError):
        plan_advanced({"Bravo": -1}, [7])
