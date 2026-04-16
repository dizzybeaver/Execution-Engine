"""Request Record Data Class for LEE Lambda Performance

Record of a single request for load prediction pattern learning.
Zero external dependencies - uses only Python stdlib.
"""

import datetime
from dataclasses import dataclass


@dataclass
class RequestRecord:
    """Record of a single request for pattern learning.

    Attributes:
        timestamp: Request timestamp (Unix epoch)
        day_of_week: Day of week (0 = Monday, 6 = Sunday)
        hour: Hour of day (0-23)
        duration_ms: Request duration in milliseconds
        success: Whether the request succeeded

    """

    timestamp: float
    day_of_week: int  # 0 = Monday, 6 = Sunday
    hour: int  # 0-23
    duration_ms: float
    success: bool

    def to_dict(self) -> dict:
        """Convert record to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "day_of_week": self.day_of_week,
            "hour": self.hour,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "datetime": datetime.datetime.utcfromtimestamp(
                self.timestamp,
            ).isoformat(),
        }


__all__ = [
    "RequestRecord",
]
