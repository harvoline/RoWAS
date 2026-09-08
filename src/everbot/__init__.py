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
from everbot.multiclient import (
    ClientPlan,
    MultiClientPlan,
    parse_client_hours,
    plan_multi_client,
)
from everbot.robots import ROBOT_TYPES, Bravo, Charlie, Delta, Robot
from everbot.standby import StandbyPlan, plan_standby
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
    "StandbyPlan",
    "plan_standby",
    "ClientPlan",
    "MultiClientPlan",
    "plan_multi_client",
    "parse_client_hours",
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
