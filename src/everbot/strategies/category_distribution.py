"""Robot Category Distribution strategy (used by Level 1).

Objective (lexicographic priority):
    1. Diversity (mandatory): every allocation includes >=1 of each category.
    2. Minimise excess hours globally (provided - requested, provided >= requested).
    3. Fewest total robots as the tiebreak on equal excess.

See ``features/level-1.md`` for the full spec and worked examples.
"""

from math import ceil

from everbot.allocation import Allocation
from everbot.errors import InsufficientCapacityError, MissingCategoryError
from everbot.robots import ROBOT_NAMES, ROBOT_TYPES, Robot
from everbot.strategies.base import AllocationStrategy


class CategoryDistributionStrategy(AllocationStrategy):
    """Distribute work across all robot categories with the least excess."""

    name = "Robot Category Distribution"

    def allocate(self, available: dict[str, int], requested_hours: int) -> Allocation:
        # Diversity is mandatory: need at least one of each type.
        if any(available.get(name, 0) == 0 for name in ROBOT_NAMES):
            raise MissingCategoryError()

        # Even using every available robot cannot reach the requested hours.
        max_hours = sum(robot.hours * available[robot.name] for robot in ROBOT_TYPES)
        if max_hours < requested_hours:
            raise InsufficientCapacityError()

        return self._search(available, requested_hours)

    @staticmethod
    def _search(available: dict[str, int], requested_hours: int) -> Allocation:
        """Bounded search for the (min excess, then fewest robots) allocation.

        Each count is bounded by inventory and by the most of that type that
        could ever help (covering ``requested_hours`` alone, plus a margin),
        keeping the search small for realistic inventories.
        """
        bravo, charlie, delta = ROBOT_TYPES  # smallest -> largest capacity

        def cap(robot: Robot) -> int:
            return min(available[robot.name], ceil(requested_hours / robot.hours) + 1)

        best_key: tuple[int, int, int, int] | None = None
        best_counts: dict[str, int] | None = None
        for b in range(1, cap(bravo) + 1):
            for c in range(1, cap(charlie) + 1):
                for d in range(1, cap(delta) + 1):
                    provided = b * bravo.hours + c * charlie.hours + d * delta.hours
                    if provided < requested_hours:
                        continue
                    # Minimise excess, then robot count; deterministic on ties.
                    key = (provided - requested_hours, b + c + d, -d, -c)
                    if best_key is None or key < best_key:
                        best_key = key
                        best_counts = {bravo.name: b, charlie.name: c, delta.name: d}

        # Guaranteed to exist: base 1/1/1 is within caps and max_hours >= hours.
        assert best_counts is not None
        return Allocation(best_counts, requested_hours)
