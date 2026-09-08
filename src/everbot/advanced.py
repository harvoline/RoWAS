"""Optional advanced reporting over the unchanged multi-client allocation plan."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from fractions import Fraction

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.multiclient import MultiClientPlan, plan_multi_client
from everbot.robots import ROBOT_TYPES


@dataclass(frozen=True)
class RobotMetrics:
    name: str
    available: int
    active_used: int
    provided_hours: int
    useful_hours: Fraction

    @property
    def inventory_usage(self) -> Fraction | None:
        return Fraction(100 * self.active_used, self.available) if self.available else None

    @property
    def capacity_utilization(self) -> Fraction | None:
        return 100 * self.useful_hours / self.provided_hours if self.provided_hours else None


@dataclass(frozen=True)
class AdvancedPlan:
    plan: MultiClientPlan
    active: Allocation
    standby: Allocation
    metrics: tuple[RobotMetrics, ...]

    @property
    def total_robots(self) -> int:
        return self.active.total_robots + self.standby.total_robots

    @property
    def total_cost(self) -> int:
        return self.active.total_cost + self.standby.total_cost

    @property
    def provided_hours(self) -> int:
        return self.active.provided_hours + self.standby.provided_hours

    @property
    def utilization(self) -> Fraction:
        return Fraction(100 * self.plan.total_requested_hours, self.provided_hours)


def plan_advanced(
    inventory: Mapping[str, object], client_hours: Iterable[object]
) -> AdvancedPlan:
    """Plan clients and estimate useful hours proportionally within each client."""
    available = Allocator.validate_inventory(inventory)
    plan = plan_multi_client(available, client_hours)
    active = dict.fromkeys(available, 0)
    standby = dict.fromkeys(available, 0)
    useful = {name: Fraction(0) for name in available}
    for client in plan.clients:
        capacity = client.allocated_hours
        if client.additional is not None:
            capacity += client.additional.provided_hours
        for robot in ROBOT_TYPES:
            name = robot.name
            active_count = 0 if client.allocated is None else client.allocated.count_of(name)
            standby_count = 0 if client.additional is None else client.additional.count_of(name)
            active[name] += active_count
            standby[name] += standby_count
            # Attribute before aggregating, preserving each client's excess capacity.
            useful[name] += Fraction(
                client.requested_hours * (active_count + standby_count) * robot.hours,
                capacity,
            )
    metrics = tuple(
        RobotMetrics(
            robot.name, available[robot.name], active[robot.name],
            (active[robot.name] + standby[robot.name]) * robot.hours, useful[robot.name],
        )
        for robot in ROBOT_TYPES
    )
    shortfall = sum(client.shortfall for client in plan.clients)
    return AdvancedPlan(
        plan,
        Allocation(active, plan.total_requested_hours - shortfall),
        Allocation(standby, shortfall),
        metrics,
    )
