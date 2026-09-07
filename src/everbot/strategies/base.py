"""The strategy interface every level implements.

Adding a new level means adding a new ``AllocationStrategy`` subclass — no
existing code changes (Open/Closed principle). Shared input validation lives in
:class:`~everbot.allocator.Allocator`, so strategies focus purely on the
allocation algorithm and their own level-specific feasibility rules.
"""

from abc import ABC, abstractmethod

from everbot.allocation import Allocation


class AllocationStrategy(ABC):
    """Interface for a level's robot-allocation algorithm."""

    #: Human-readable name; override in subclasses.
    name: str = "base"

    @abstractmethod
    def allocate(self, available: dict[str, int], requested_hours: int) -> Allocation:
        """Return the best :class:`Allocation` for the given inventory and hours.

        Args:
            available: validated mapping of robot name -> non-negative int count,
                with every category present as a key.
            requested_hours: validated positive integer of requested work hours.

        Raises:
            everbot.errors.EverBotError: when the request cannot be satisfied
            under this strategy's rules.
        """
