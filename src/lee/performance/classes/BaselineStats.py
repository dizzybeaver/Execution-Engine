"""Baseline Statistics Data Class for LEE Lambda Performance

Statistical baseline for time-aware anomaly detection.
Zero external dependencies - uses only Python stdlib.
"""

from dataclasses import dataclass


@dataclass
class BaselineStats:
    """Statistical baseline for a specific time slot.

    Used for time-aware anomaly detection where different times of day
    and days of week have different performance characteristics.

    Attributes:
        avg: Average value for this time slot
        p95: 95th percentile value
        p99: 99th percentile value
        sample_count: Number of samples used to build baseline
        min_samples_required: Minimum samples needed for reliable baseline

    """

    avg: float
    p95: float
    p99: float
    sample_count: int
    min_samples_required: int = 5

    def is_reliable(self) -> bool:
        """Check if baseline has enough samples to be reliable."""
        return self.sample_count >= self.min_samples_required

    def to_dict(self) -> dict[str, any]:
        """Convert baseline to dictionary."""
        return {
            "avg": self.avg,
            "p95": self.p95,
            "p99": self.p99,
            "sample_count": self.sample_count,
            "reliable": self.is_reliable(),
        }


__all__ = [
    "BaselineStats",
]
