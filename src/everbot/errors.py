"""Error types and the exact user-facing messages required by the spec.

Keeping the messages here as constants ensures the CLI and any future callers
emit identical wording (see ``robots.md`` and ``features/level-1.md``).
"""

# Exact messages — do not reword; tests and the spec depend on these.
MSG_INVALID_WORK_HOURS = "Error: Work hours must be a positive integer."
MSG_INVALID_ROBOT_COUNT = "Error: Robot counts must be non-negative integers."
MSG_NO_ROBOTS = "Error: No robots available for assignment."
MSG_MISSING_CATEGORY = (
    "Error: Unable to allocate at least one robot from each category "
    "with the available inventory."
)
MSG_INSUFFICIENT_CAPACITY = (
    "Error: Insufficient robot capacity to complete the requested work."
)


class EverBotError(Exception):
    """Base class for all allocation errors.

    ``str(err)`` yields the exact user-facing message.
    """


class InvalidWorkHoursError(EverBotError):
    def __init__(self, message: str = MSG_INVALID_WORK_HOURS) -> None:
        super().__init__(message)


class InvalidRobotCountError(EverBotError):
    def __init__(self, message: str = MSG_INVALID_ROBOT_COUNT) -> None:
        super().__init__(message)


class NoRobotsError(EverBotError):
    def __init__(self, message: str = MSG_NO_ROBOTS) -> None:
        super().__init__(message)


class MissingCategoryError(EverBotError):
    def __init__(self, message: str = MSG_MISSING_CATEGORY) -> None:
        super().__init__(message)


class InsufficientCapacityError(EverBotError):
    def __init__(self, message: str = MSG_INSUFFICIENT_CAPACITY) -> None:
        super().__init__(message)
