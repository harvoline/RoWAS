"""EverBot Solutions — robot allocation system."""

from everbot.allocation import Allocation
from everbot.allocator import Allocator, allocate
from everbot.comparison import CostComparison, compare_levels
from everbot.errors import (
    EverBotError,
    InsufficientCapacityError,
    InvalidRobotCountError,
    InvalidWorkHoursError,
    MissingCategoryError,
    NoRobotsError,
)
from everbot.robots import ROBOT_TYPES, Bravo, Charlie, Delta, Robot
from everbot.strategies import (
    AllocationStrategy,
    CategoryDistributionStrategy,
    CostOptimisedStrategy,
    strategy_for_level,
)

__all__ = [
    "Allocation",
    "Allocator",
    "allocate",
    "AllocationStrategy",
    "CategoryDistributionStrategy",
    "CostOptimisedStrategy",
    "CostComparison",
    "compare_levels",
    "strategy_for_level",
    "Robot",
    "Bravo",
    "Charlie",
    "Delta",
    "ROBOT_TYPES",
    "EverBotError",
    "InsufficientCapacityError",
    "InvalidRobotCountError",
    "InvalidWorkHoursError",
    "MissingCategoryError",
    "NoRobotsError",
]
