"""The :class:`Allocation` result value object.

Produced by an allocation strategy; exposes derived figures (provided hours,
excess, robot count, cost) so callers never recompute them.
"""

from everbot.robots import ROBOT_TYPES


class Allocation:
    """How many of each robot type were assigned to fulfil a request."""

    def __init__(self, counts: dict[str, int], requested_hours: int) -> None:
        # counts: robot name -> int, expected in ROBOT_TYPES order.
        self._counts = dict(counts)
        self._requested_hours = requested_hours

    @property
    def counts(self) -> dict[str, int]:
        """A copy of the per-category counts (name -> int)."""
        return dict(self._counts)

    def count_of(self, name: str) -> int:
        return self._counts.get(name, 0)

    @property
    def requested_hours(self) -> int:
        return self._requested_hours

    @property
    def provided_hours(self) -> int:
        return sum(robot.hours * self._counts.get(robot.name, 0) for robot in ROBOT_TYPES)

    @property
    def excess_hours(self) -> int:
        return self.provided_hours - self._requested_hours

    @property
    def total_robots(self) -> int:
        return sum(self._counts.values())

    @property
    def total_cost(self) -> int:
        return sum(robot.cost * self._counts.get(robot.name, 0) for robot in ROBOT_TYPES)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Allocation)
            and self._counts == other._counts
            and self._requested_hours == other._requested_hours
        )

    def __repr__(self) -> str:
        inside = ", ".join(f"{name}={count}" for name, count in self._counts.items())
        return f"Allocation({inside}, requested={self._requested_hours})"
