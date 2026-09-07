"""Level 1 vs Level 2 cost comparison helpers."""

from collections.abc import Mapping
from dataclasses import dataclass

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.errors import EverBotError
from everbot.strategies.category_distribution import CategoryDistributionStrategy
from everbot.strategies.cost_optimised import CostOptimisedStrategy


@dataclass(frozen=True)
class CostComparison:
    """Result of comparing Level 1 and Level 2 allocations for the same inputs."""

    level2: Allocation
    level1: Allocation | None
    level1_error: str | None

    @property
    def level2_cost(self) -> int:
        return self.level2.total_cost

    @property
    def level1_cost(self) -> int | None:
        return None if self.level1 is None else self.level1.total_cost

    @property
    def cost_difference(self) -> int | None:
        """Extra dollars Level 1 spends vs Level 2; None if Level 1 is infeasible."""
        if self.level1_cost is None:
            return None
        return self.level1_cost - self.level2_cost


def compare_levels(
    inventory: Mapping[str, object], requested_hours: object
) -> CostComparison:
    """Run Level 2 (required) and Level 1 (best-effort) for the same inputs.

    Level 2 must succeed or the underlying ``EverBotError`` propagates.
    If Level 1 fails (e.g. missing category), ``level1`` is None and
    ``level1_error`` holds the user-facing message.
    """
    level2 = Allocator(CostOptimisedStrategy()).allocate(inventory, requested_hours)
    try:
        level1 = Allocator(CategoryDistributionStrategy()).allocate(
            inventory, requested_hours
        )
    except EverBotError as err:
        return CostComparison(level2=level2, level1=None, level1_error=str(err))
    return CostComparison(level2=level2, level1=level1, level1_error=None)
