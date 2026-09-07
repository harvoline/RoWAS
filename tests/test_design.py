"""Tests for the OOP structure: robot hierarchy and strategy interface."""

import pytest

from everbot.allocation import Allocation
from everbot.robots import ROBOT_TYPES, Bravo, Charlie, Delta, Robot
from everbot.strategies.base import AllocationStrategy
from everbot.strategies.category_distribution import CategoryDistributionStrategy


def test_robot_base_class_is_abstract():
    with pytest.raises(TypeError):
        Robot()  # cannot instantiate the abstract base


@pytest.mark.parametrize(
    "cls, name, hours, cost",
    [
        (Bravo, "Bravo", 3, 2),
        (Charlie, "Charlie", 5, 3),
        (Delta, "Delta", 8, 4),
    ],
)
def test_robot_subclasses_carry_correct_data(cls, name, hours, cost):
    robot = cls()
    assert isinstance(robot, Robot)
    assert (robot.name, robot.hours, robot.cost) == (name, hours, cost)


def test_registry_is_ordered_by_capacity():
    assert [r.name for r in ROBOT_TYPES] == ["Bravo", "Charlie", "Delta"]
    hours = [r.hours for r in ROBOT_TYPES]
    assert hours == sorted(hours)


def test_category_distribution_is_an_allocation_strategy():
    strategy = CategoryDistributionStrategy()
    assert isinstance(strategy, AllocationStrategy)
    assert strategy.name  # has a human-readable name


def test_strategy_returns_allocation():
    alloc = CategoryDistributionStrategy().allocate({"Bravo": 2, "Charlie": 2, "Delta": 2}, 16)
    assert isinstance(alloc, Allocation)


def test_allocation_equality_and_repr():
    a = Allocation({"Bravo": 1, "Charlie": 1, "Delta": 1}, 16)
    b = Allocation({"Bravo": 1, "Charlie": 1, "Delta": 1}, 16)
    c = Allocation({"Bravo": 2, "Charlie": 1, "Delta": 1}, 16)
    assert a == b
    assert a != c
    assert "Bravo=1" in repr(a)
