"""Cost-optimised allocation strategy (used by Level 2).

Objective (lexicographic priority):
    1. Minimise total charging cost.
    2. Minimise excess hours (provided - requested, provided >= requested).
    3. Fewest total robots.
    4. Deterministic: prefer more Delta, then more Charlie (stable on remaining ties).

Diversity is NOT required — any subset of categories may be used (including a
single type). See ``features/level-2.md`` for the full spec and worked examples.
"""

from math import ceil

from everbot.allocation import Allocation
from everbot.errors import InsufficientCapacityError
from everbot.robots import ROBOT_TYPES, Robot
from everbot.strategies.base import AllocationStrategy


class CostOptimisedStrategy(AllocationStrategy):
    """Allocate robots to fulfil requested hours at the lowest charging cost."""

    name = "Cost Optimised Allocation"

    def allocate(self, available: dict[str, int], requested_hours: int) -> Allocation:
        max_hours = sum(robot.hours * available[robot.name] for robot in ROBOT_TYPES)
        if max_hours < requested_hours:
            raise InsufficientCapacityError()

        return self._search(available, requested_hours)

    @staticmethod
    def _search(available: dict[str, int], requested_hours: int) -> Allocation:
        """Bounded search for the min-cost (then min-excess, fewest robots) allocation."""
        bravo, charlie, delta = ROBOT_TYPES

        def cap(robot: Robot) -> int:
            # +1 margin matches Level 1; zero counts are allowed here.
            return min(available[robot.name], ceil(requested_hours / robot.hours) + 1)

        best_key: tuple[int, int, int, int, int] | None = None
        best_counts: dict[str, int] | None = None
        for b in range(0, cap(bravo) + 1):
            for c in range(0, cap(charlie) + 1):
                for d in range(0, cap(delta) + 1):
                    if b == 0 and c == 0 and d == 0:
                        continue
                    provided = b * bravo.hours + c * charlie.hours + d * delta.hours
                    if provided < requested_hours:
                        continue
                    cost = b * bravo.cost + c * charlie.cost + d * delta.cost
                    # Min cost, then excess, then robot count; prefer more Delta/Charlie.
                    key = (cost, provided - requested_hours, b + c + d, -d, -c)
                    if best_key is None or key < best_key:
                        best_key = key
                        best_counts = {bravo.name: b, charlie.name: c, delta.name: d}

        assert best_counts is not None
        return Allocation(best_counts, requested_hours)
