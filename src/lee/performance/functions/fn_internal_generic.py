"""Internal Generic Functions for Performance Domain

Shared utility functions used by multiple performance classes.
Zero external dependencies - uses only Python stdlib.
"""

import math
import statistics
from typing import Any, Optional


def _compute_stats(
    samples: list[float],
    cache: dict[str, Optional[Any]] = None,
    cache_valid: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Compute statistics for current window.

    Args:
        samples: List of sample values
        cache: Optional statistics cache dictionary
        cache_valid: Whether the cache is valid

    Returns:
        Tuple of (statistics dictionary, cache_valid flag)

    """
    if cache is not None and cache_valid:
        return cache, True

    if len(samples) == 0:
        stats = {
            "count": 0,
            "mean": 0.0,
            "stdev": 0.0,
            "median": 0.0,
            "q1": 0.0,
            "q3": 0.0,
            "iqr": 0.0,
        }
    elif len(samples) == 1:
        stats = {
            "count": 1,
            "mean": samples[0],
            "stdev": 0.0,
            "median": samples[0],
            "q1": samples[0],
            "q3": samples[0],
            "iqr": 0.0,
        }
    else:
        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        q1 = _percentile(sorted_samples, 0.25)
        q3 = _percentile(sorted_samples, 0.75)

        stats = {
            "count": n,
            "mean": statistics.mean(samples),
            "stdev": statistics.stdev(samples) if n > 1 else 0.0,
            "median": statistics.median(samples),
            "q1": q1,
            "q3": q3,
            "iqr": q3 - q1,
        }

    return stats, True


def _percentile(data: list[float], p: float) -> float:
    """Calculate percentile using linear interpolation.

    Matches numpy.percentile with interpolation='linear'.

    Args:
        data: Sorted list of values
        p: Percentile to calculate (0.0 to 1.0)

    Returns:
        Percentile value

    """
    if not data:
        return 0.0
    if len(data) == 1:
        return data[0]

    sorted_data = sorted(data)
    n = len(sorted_data)
    # Position is 1-indexed
    pos = (n - 1) * p
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))

    if lower == upper:
        return sorted_data[lower]

    # Linear interpolation
    weight = pos - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


__all__ = [
    "_compute_stats",
    "_percentile",
]
