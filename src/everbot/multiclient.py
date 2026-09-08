"""Level 4 — Multi-Client Allocation.

Level 3 served one client from the full active inventory. Level 4 accepts many
client work-hour values in a single input, serves them highest-hours-first from
one shared pool of active robots, and recommends standby robots for whatever the
pool cannot cover — reusing the Level 3 shortfall fill unchanged.

A robot assigned to a client is consumed for the day (``robots.md``), so the pool
is drawn down by whole robots and unused hours are excess, not carried over.

See ``features/level-4.md``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from everbot.allocation import Allocation
from everbot.allocator import Allocator
from everbot.errors import InvalidWorkHoursError
from everbot.standby import active_capacity_hours, fill_shortfall
from everbot.strategies.cost_optimised import CostOptimisedStrategy

# Client hours may be separated by commas, whitespace, or both.
_SEPARATORS = re.compile(r"[,\s]+")


def parse_client_hours(raw: str) -> list[int]:
    """Parse a client-hours input line into one positive integer per client.

    Accepts ``"20"``, ``"12,16,17"``, ``"12 16 17"`` and mixtures; repeated or
    surrounding separators are ignored. The number of values is the number of
    clients, so an input with no values is rejected.

    Raises:
        InvalidWorkHoursError: no values, or any value that is not a positive
            integer.
    """
    tokens = [token for token in _SEPARATORS.split(raw.strip()) if token]
    if not tokens:
        raise InvalidWorkHoursError()

    hours: list[int] = []
    for token in tokens:
        try:
            value = int(token)
        except ValueError:
            raise InvalidWorkHoursError() from None
        Allocator.validate_hours(value)
        hours.append(value)
    return hours


@dataclass(frozen=True)
class ClientPlan:
    """What one client receives from the active pool, plus any standby needed."""

    number: int
    """1-based position in the input, kept even though service order differs."""

    requested_hours: int
    allocated: Allocation | None
    """Robots taken from the shared active pool, or None when it had none left."""

    additional: Allocation | None
    """Standby robots to activate for the shortfall, or None when covered."""

    @property
    def allocated_hours(self) -> int:
        return 0 if self.allocated is None else self.allocated.provided_hours

    @property
    def shortfall(self) -> int:
        return max(0, self.requested_hours - self.allocated_hours)

    @property
    def standby_cost(self) -> int:
        return 0 if self.additional is None else self.additional.total_cost


@dataclass(frozen=True)
class MultiClientPlan:
    """Result of a Level 4 planning pass over several clients."""

    active_capacity: int
    """Total active hours available before any client was served."""

    clients: tuple[ClientPlan, ...]
    """Clients in service order (highest hours first, ties in input order)."""

    @property
    def client_count(self) -> int:
        return len(self.clients)

    @property
    def total_requested_hours(self) -> int:
        return sum(client.requested_hours for client in self.clients)

    @property
    def total_standby_cost(self) -> int:
        return sum(client.standby_cost for client in self.clients)


def plan_multi_client(
    active_inventory: Mapping[str, object], client_hours: Iterable[object]
) -> MultiClientPlan:
    """Plan Level 4 allocation for several clients sharing one active inventory.

    Clients are served in descending requested hours (ties in input order). Each
    client takes a cost-optimised set of robots from the *remaining* pool when the
    pool can cover it; otherwise it takes every remaining robot and the shortfall
    becomes an unbounded, cost-optimised standby recommendation.

    Raises:
        EverBotError: invalid robot counts, no clients, or any client's hours not
            a positive integer.
    """
    available = Allocator.validate_inventory(active_inventory)

    requested: list[int] = []
    for value in client_hours:
        Allocator.validate_hours(value)
        assert isinstance(value, int)  # narrowed by validate_hours
        requested.append(value)
    if not requested:
        raise InvalidWorkHoursError()

    # Highest hours first; input position breaks ties and labels the client.
    service_order = sorted(enumerate(requested), key=lambda pair: (-pair[1], pair[0]))

    remaining = dict(available)
    plans: list[ClientPlan] = []
    for index, hours in service_order:
        capacity = active_capacity_hours(remaining)
        if capacity >= hours:
            # Pool covers this client: cost-optimised draw from what is left.
            allocated: Allocation | None = CostOptimisedStrategy().allocate(remaining, hours)
            assert allocated is not None
            for name, count in allocated.counts.items():
                remaining[name] -= count
            additional: Allocation | None = None
        else:
            # Use the full remaining pool first, then recommend standby robots.
            allocated = Allocation(dict(remaining), hours) if capacity > 0 else None
            remaining = dict.fromkeys(remaining, 0)
            additional = fill_shortfall(hours - capacity)
        plans.append(
            ClientPlan(
                number=index + 1,
                requested_hours=hours,
                allocated=allocated,
                additional=additional,
            )
        )

    return MultiClientPlan(
        active_capacity=active_capacity_hours(available), clients=tuple(plans)
    )
