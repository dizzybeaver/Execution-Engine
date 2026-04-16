"""Anomaly Detection Gateway Integration for LEE Lambda Performance

Gateway integration functions for the anomaly detection system.
Provides SUGA-ISP compliant access through the SINGLETON interface.

Zero external dependencies - uses only Python stdlib.
"""

import threading
from typing import Optional

from lee.performance.classes.AnomalyDetector_class import (
    DEFAULT_IQR_MULTIPLIER,
    DEFAULT_MIN_SAMPLES,
    DEFAULT_SPIKE_THRESHOLD,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_Z_SCORE_THRESHOLD,
    AnomalyDetector,
)
from lee.performance.classes.AnomalyResult import AnomalyResult
from lee.performance.classes.BaselineStats import BaselineStats

# Singleton instance for Lambda performance monitoring
_performance_detector: Optional[AnomalyDetector] = None
_performance_detector_lock = threading.Lock()
_performance_detector_initialized = False


def get_performance_detector(
    window_size: int = DEFAULT_WINDOW_SIZE,
    reset: bool = False,
) -> AnomalyDetector:
    """Get or create thread-safe singleton anomaly detector."""
    # pylint: disable=global-statement
    # Required for singleton pattern with thread-safe lazy initialization
    global _performance_detector, _performance_detector_initialized

    if _performance_detector is None or reset:
        with _performance_detector_lock:
            if _performance_detector is None or reset:
                if reset and _performance_detector is not None:
                    _performance_detector.reset()
                else:
                    _performance_detector = AnomalyDetector(
                        window_size=window_size,
                        z_score_threshold=DEFAULT_Z_SCORE_THRESHOLD,
                        spike_threshold=DEFAULT_SPIKE_THRESHOLD,
                        iqr_multiplier=DEFAULT_IQR_MULTIPLIER,
                        min_samples=DEFAULT_MIN_SAMPLES,
                    )
                _performance_detector_initialized = True

    return _performance_detector


def reset_performance_detector() -> None:
    """Reset the performance detector singleton state."""
    # pylint: disable=global-statement
    # Required for singleton pattern reset
    global _performance_detector_initialized

    with _performance_detector_lock:
        if _performance_detector is not None:
            _performance_detector.reset()
        _performance_detector_initialized = False


# ===== GATEWAY INTEGRATION FUNCTIONS =====

def anomaly_detector_detect(
    value: float,
    algorithm: str = "z_score",
    auto_add: bool = True,
) -> AnomalyResult:
    """Detect anomalies using the performance detector singleton."""
    detector = get_performance_detector()
    return detector.detect(value, algorithm=algorithm, auto_add=auto_add)


def anomaly_detector_add_sample(value: float) -> None:
    """Add a sample to the performance detector."""
    detector = get_performance_detector()
    detector.add_sample(value)


def anomaly_detector_get_stats() -> dict[str, any]:
    """Get current statistics from the performance detector."""
    detector = get_performance_detector()
    return detector.get_stats()


def anomaly_detector_reset() -> None:
    """Reset the performance detector state."""
    reset_performance_detector()


def anomaly_detector_get_sample_count() -> int:
    """Get the current number of samples in the detector."""
    detector = get_performance_detector()
    return len(detector)


def anomaly_detector_add_time_aware_sample(
    value: float,
    timestamp: float,
) -> None:
    """Add a time-aware sample to the performance detector."""
    detector = get_performance_detector()
    detector.add_time_aware_sample(value, timestamp)


def anomaly_detector_learn_baselines(
) -> dict[tuple[int, int], BaselineStats]:
    """Learn baselines from time-aware samples."""
    detector = get_performance_detector()
    return detector.learn_baselines()


def anomaly_detector_is_deviation_from_baseline(
    value: float,
    timestamp: float,
    threshold_percentile: str = "p95",
) -> tuple[bool, BaselineStats | None, str]:
    """Check if value deviates from time-aware baseline."""
    detector = get_performance_detector()
    return detector.is_deviation_from_baseline(
        value, timestamp, threshold_percentile
    )


def anomaly_detector_get_baselines() -> dict[tuple[int, int], BaselineStats]:
    """Get all learned baselines."""
    detector = get_performance_detector()
    return detector.get_baselines()


def anomaly_detector_get_time_bin_sample_count(
    day_of_week: int,
    hour: int,
) -> int:
    """Get the number of samples for a specific time bin."""
    detector = get_performance_detector()
    return detector.get_time_bin_sample_count(day_of_week, hour)


def anomaly_detector_reset_time_aware_baselines() -> None:
    """Reset all time-aware baseline data."""
    detector = get_performance_detector()
    detector.reset_time_aware_baselines()


__all__ = [
    "get_performance_detector",
    "reset_performance_detector",
    "anomaly_detector_detect",
    "anomaly_detector_add_sample",
    "anomaly_detector_get_stats",
    "anomaly_detector_reset",
    "anomaly_detector_get_sample_count",
    "anomaly_detector_add_time_aware_sample",
    "anomaly_detector_learn_baselines",
    "anomaly_detector_is_deviation_from_baseline",
    "anomaly_detector_get_baselines",
    "anomaly_detector_get_time_bin_sample_count",
    "anomaly_detector_reset_time_aware_baselines",
]
