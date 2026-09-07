"""Allocation strategies — one class per behavior, named for what it does.

The exercise's "level" is just an entry in ``STRATEGY_BY_LEVEL``; strategy classes
are named for their behavior, not their level number.
"""

from everbot.strategies.base import AllocationStrategy
from everbot.strategies.category_distribution import CategoryDistributionStrategy

# Maps the exercise's level number to the strategy it uses.
STRATEGY_BY_LEVEL = {
    1: CategoryDistributionStrategy,
}


def strategy_for_level(level: int) -> AllocationStrategy:
    """Instantiate the strategy registered for ``level``."""
    try:
        return STRATEGY_BY_LEVEL[level]()
    except KeyError:
        raise ValueError(f"No strategy registered for level {level}.") from None


__all__ = [
    "AllocationStrategy",
    "CategoryDistributionStrategy",
    "STRATEGY_BY_LEVEL",
    "strategy_for_level",
]
