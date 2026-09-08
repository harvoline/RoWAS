"""Tests for Level 4 multi-client allocation.

Categories: normal (owner example, ordering), edge (ties, exact capacity, robot
consumption, zero inventory), invalid (parsing + validation failures).
"""

import pytest

from everbot.errors import InvalidRobotCountError, InvalidWorkHoursError
from everbot.multiclient import parse_client_hours, plan_multi_client

INVENTORY = {"Bravo": 2, "Charlie": 3, "Delta": 2}


def _counts(alloc):
    if alloc is None:
        return None
    return (alloc.count_of("Bravo"), alloc.count_of("Charlie"), alloc.count_of("Delta"))


# --- input parsing ----------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("20", [20]),
        ("12,16,17,10,21", [12, 16, 17, 10, 21]),
        ("12 16 17 10 21", [12, 16, 17, 10, 21]),
        ("12, 16 17,10 , 21", [12, 16, 17, 10, 21]),
        ("  8  ", [8]),
        ("12,,16", [12, 16]),
        (",12,16,", [12, 16]),
    ],
)
def test_parse_accepts_single_comma_and_space_separated(raw, expected):
    assert parse_client_hours(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", ",", " , , ", "abc", "12,abc", "12 -3", "0", "12,0", "1.5", "12;16"],
)
def test_parse_rejects_invalid_values(raw):
    with pytest.raises(InvalidWorkHoursError):
        parse_client_hours(raw)


# --- normal: owner example --------------------------------------------------


def test_owner_example_service_order_and_allocations():
    plan = plan_multi_client(INVENTORY, [12, 16, 17, 10, 21])

    assert plan.active_capacity == 37
    assert [c.number for c in plan.clients] == [5, 3, 2, 1, 4]
    assert [c.requested_hours for c in plan.clients] == [21, 17, 16, 12, 10]

    first, second, third, fourth, fifth = plan.clients

    # Pool covers 21h -> cost-optimised from the pool, no standby.
    assert _counts(first.allocated) == (0, 1, 2)
    assert first.allocated_hours == 21
    assert first.additional is None
    assert first.shortfall == 0

    # Pool has 16h left -> all of it, then standby covers the 1h shortfall.
    assert _counts(second.allocated) == (2, 2, 0)
    assert second.allocated_hours == 16
    assert second.shortfall == 1
    assert _counts(second.additional) == (1, 0, 0)
    assert second.standby_cost == 2

    # Pool is empty from here on.
    assert third.allocated is None
    assert third.shortfall == 16
    assert _counts(third.additional) == (0, 0, 2)
    assert third.standby_cost == 8

    assert _counts(fourth.additional) == (0, 1, 1)
    assert fourth.standby_cost == 7

    assert _counts(fifth.additional) == (0, 2, 0)
    assert fifth.standby_cost == 6

    assert plan.total_standby_cost == 23
    assert plan.client_count == 5


def test_single_client_matches_level_3_behaviour():
    plan = plan_multi_client({"Bravo": 1, "Charlie": 1, "Delta": 1}, [21])
    (client,) = plan.clients
    assert plan.active_capacity == 16
    assert client.number == 1
    assert client.allocated_hours == 16
    assert client.shortfall == 5
    assert _counts(client.additional) == (0, 1, 0)
    assert client.standby_cost == 3


def test_single_client_fully_covered_has_no_standby():
    plan = plan_multi_client({"Bravo": 1, "Charlie": 1, "Delta": 1}, [16])
    (client,) = plan.clients
    assert _counts(client.allocated) == (1, 1, 1)
    assert client.additional is None
    assert plan.total_standby_cost == 0


# --- edge cases -------------------------------------------------------------


def test_higher_hours_client_is_served_before_earlier_input():
    # Client 2 asks for more, so it draws from the pool first.
    plan = plan_multi_client({"Bravo": 0, "Charlie": 0, "Delta": 1}, [5, 8])
    assert [c.number for c in plan.clients] == [2, 1]
    assert _counts(plan.clients[0].allocated) == (0, 0, 1)
    assert plan.clients[1].allocated is None


def test_equal_hours_served_in_input_order():
    plan = plan_multi_client({"Bravo": 0, "Charlie": 0, "Delta": 1}, [16, 16])
    assert [c.number for c in plan.clients] == [1, 2]
    assert plan.clients[0].allocated_hours == 8
    assert plan.clients[1].allocated is None


def test_assigned_robot_is_consumed_not_split_across_clients():
    # One Delta (8h). First client needs 4h but consumes the whole robot.
    plan = plan_multi_client({"Bravo": 0, "Charlie": 0, "Delta": 1}, [4, 4])
    first, second = plan.clients
    assert _counts(first.allocated) == (0, 0, 1)
    assert first.allocated_hours == 8  # 4h of excess, not carried over
    assert first.additional is None
    assert second.allocated is None
    assert second.shortfall == 4
    assert _counts(second.additional) == (0, 1, 0)


def test_zero_active_inventory_is_all_standby():
    plan = plan_multi_client({"Bravo": 0, "Charlie": 0, "Delta": 0}, [8, 6])
    assert plan.active_capacity == 0
    assert all(c.allocated is None for c in plan.clients)
    assert _counts(plan.clients[0].additional) == (0, 0, 1)
    assert _counts(plan.clients[1].additional) == (2, 0, 0)
    assert plan.total_standby_cost == 8


def test_pool_is_drawn_down_across_clients():
    plan = plan_multi_client(INVENTORY, [21, 21])
    first, second = plan.clients
    assert first.allocated_hours == 21
    assert first.additional is None
    assert second.allocated_hours == 16  # whatever the pool had left
    assert second.shortfall == 5


# --- invalid cases ----------------------------------------------------------


def test_rejects_empty_client_list():
    with pytest.raises(InvalidWorkHoursError):
        plan_multi_client(INVENTORY, [])


@pytest.mark.parametrize("hours", [[0], [-1], [1.5], ["16"], [None], [True], [16, 0]])
def test_rejects_invalid_hours_values(hours):
    with pytest.raises(InvalidWorkHoursError):
        plan_multi_client(INVENTORY, hours)


def test_rejects_invalid_robot_counts():
    with pytest.raises(InvalidRobotCountError):
        plan_multi_client({"Bravo": -1, "Charlie": 1, "Delta": 1}, [10])
