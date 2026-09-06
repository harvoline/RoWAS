"""Robot domain model for EverBot Solutions.

Each robot category is a subclass of the abstract :class:`Robot`, carrying its
daily working hours and charging cost. ``ROBOT_TYPES`` is the ordered registry
(smallest -> largest capacity) used throughout the system.
"""

from abc import ABC, abstractmethod


class Robot(ABC):
    """Abstract base class for a category of robot.

    Concrete categories (Bravo/Charlie/Delta) override ``name``, ``hours`` and
    ``cost``. The base class is abstract and cannot be instantiated directly.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable category name (e.g. ``"Bravo"``)."""

    @property
    @abstractmethod
    def hours(self) -> int:
        """Working hours delivered per day."""

    @property
    @abstractmethod
    def cost(self) -> int:
        """Charging cost per day, in dollars."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(hours={self.hours}, cost={self.cost})"


class Bravo(Robot):
    @property
    def name(self) -> str:
        return "Bravo"

    @property
    def hours(self) -> int:
        return 3

    @property
    def cost(self) -> int:
        return 2


class Charlie(Robot):
    @property
    def name(self) -> str:
        return "Charlie"

    @property
    def hours(self) -> int:
        return 5

    @property
    def cost(self) -> int:
        return 3


class Delta(Robot):
    @property
    def name(self) -> str:
        return "Delta"

    @property
    def hours(self) -> int:
        return 8

    @property
    def cost(self) -> int:
        return 4


# Ordered smallest -> largest capacity; output and iteration rely on this order.
ROBOT_TYPES: tuple[Robot, ...] = (Bravo(), Charlie(), Delta())
ROBOT_NAMES: tuple[str, ...] = tuple(robot.name for robot in ROBOT_TYPES)
ROBOT_BY_NAME: dict[str, Robot] = {robot.name: robot for robot in ROBOT_TYPES}
