"""Statistical Anomaly Detection for LEE Lambda Performance

Implements multiple anomaly detection algorithms:
- Z-score detection: Identifies statistical outliers based on standard deviations
- Spike detection: Detects sudden changes between consecutive measurements
- IQR detection: Uses interquartile range to find outliers

Zero external dependencies - uses only Python stdlib.

Thread Safety:
    All public methods are thread-safe. Internal state is protected by locks.
    Uses separate locks for samples, previous_value, and cache to minimize contention.
"""

import datetime as dt
import math
import statistics
import threading
from collections import deque
from typing import Any, Optional

from lee.performance.classes.AnomalyResult import (
    AnomalyResult,
    AnomalySeverity,
    AnomalyType,
)
from lee.performance.classes.BaselineStats import BaselineStats
from lee.performance.functions.fn_internal_generic import _compute_stats

# ===== CONSTANTS =====

# Default configuration values
DEFAULT_WINDOW_SIZE: int = 100
DEFAULT_Z_SCORE_THRESHOLD: float = 3.0
DEFAULT_SPIKE_THRESHOLD: float = 2.5
DEFAULT_IQR_MULTIPLIER: float = 1.5
DEFAULT_MIN_SAMPLES: int = 10

# Severity thresholds for z-score
Z_SCORE_CRITICAL_THRESHOLD: float = 5.0
Z_SCORE_HIGH_THRESHOLD: float = 4.0

# Severity thresholds for spike detection (relative change)
SPIKE_CRITICAL_THRESHOLD: float = 3.0
SPIKE_HIGH_THRESHOLD: float = 2.0
SPIKE_MEDIUM_THRESHOLD: float = 1.0
SPIKE_RELATIVE_CHANGE_THRESHOLD: float = 0.5

# Severity thresholds for IQR distance
IQR_CRITICAL_DISTANCE: float = 3.0
IQR_HIGH_DISTANCE: float = 2.0
IQR_MEDIUM_DISTANCE: float = 1.0

# Confidence scaling
MAX_CONFIDENCE_Z_SCORE: float = 5.0
MAX_CONFIDENCE_IQR_DISTANCE: float = 3.0

# Time-aware baseline learning
MAX_SAMPLES_PER_TIME_BIN: int = 100
MIN_SAMPLES_PER_TIME_BIN: int = 5


class AnomalyDetector:  # pylint: disable=too-many-instance-attributes
    """Statistical anomaly detection using sliding window.

    Features:
    - Multiple detection algorithms (z_score, spike, iqr)
    - Configurable window size and thresholds
    - Minimal memory footprint (deque with maxlen)
    - Thread-safe singleton initialization with double-check pattern
    - Input validation for all numeric parameters
    - Type checking for sample values (rejects NaN, infinity, bool)
    - Thread-safe operations with fine-grained locking

    Thread Safety:
        All public methods are thread-safe. Uses separate locks for:
        - _samples_lock: Protects sample deque
        - _previous_value_lock: Protects previous value
        - _cache_lock: Protects statistics cache

    Example:
        >>> detector = AnomalyDetector(window_size=50)
        >>> result = detector.detect(1500.0, algorithm='z_score')
        >>> if result.is_anomaly:
        ...     print(f"Anomaly detected: {result.message}")

    Raises:
        ValueError: If initialization parameters are invalid
        ValueError: If sample value is not a finite number (excludes bool)

    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        z_score_threshold: float = DEFAULT_Z_SCORE_THRESHOLD,
        spike_threshold: float = DEFAULT_SPIKE_THRESHOLD,
        iqr_multiplier: float = DEFAULT_IQR_MULTIPLIER,
        min_samples: int = DEFAULT_MIN_SAMPLES,
    ):
        """Initialize anomaly detector with input validation.

        Args:
            window_size: Maximum number of historical samples to keep (must be > 0)
            z_score_threshold: Standard deviations for z-score detection (must be > 0)
            spike_threshold: Multiplier for spike detection (must be > 0)
            iqr_multiplier: IQR multiplier for outlier detection (must be > 0)
            min_samples: Minimum samples required before detection (must be > 0 and <= window_size)

        Raises:
            ValueError: If any parameter fails validation

        """
        # Validate parameters
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError(f"AnomalyDetector: window_size must be positive integer, got {window_size}")
        if not isinstance(z_score_threshold, (int, float)) or z_score_threshold <= 0:
            raise ValueError(f"AnomalyDetector: z_score_threshold must be positive, got {z_score_threshold}")
        if not isinstance(spike_threshold, (int, float)) or spike_threshold <= 0:
            raise ValueError(f"AnomalyDetector: spike_threshold must be positive, got {spike_threshold}")
        if not isinstance(iqr_multiplier, (int, float)) or iqr_multiplier <= 0:
            raise ValueError(f"AnomalyDetector: iqr_multiplier must be positive, got {iqr_multiplier}")
        if not isinstance(min_samples, int) or min_samples <= 0 or min_samples > window_size:
            raise ValueError(f"AnomalyDetector: min_samples must be positive integer <= window_size, got {min_samples}")

        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.spike_threshold = spike_threshold
        self.iqr_multiplier = iqr_multiplier
        self.min_samples = min_samples

        # Sliding window for historical data
        self._samples: deque[float] = deque(maxlen=window_size)
        self._samples_lock = threading.Lock()

        # Track previous value for spike detection
        self._previous_value: Optional[float] = None
        self._previous_value_lock = threading.Lock()

        # Statistics cache
        self._stats_cache: dict[str, Optional[Any]] = None
        self._cache_lock = threading.Lock()
        self._cache_valid: bool = False
        self._samples_discarded: bool = False

        # Time-aware baseline learning
        self._time_bins: dict[tuple[int, int], deque[float]] = {}
        self._time_bins_lock = threading.Lock()
        self._baselines: dict[tuple[int, int], BaselineStats] = {}
        self._baselines_lock = threading.Lock()
        self._min_samples_per_bin: int = MIN_SAMPLES_PER_TIME_BIN

    def add_sample(self, value: float) -> None:
        """Add a sample to the historical window with type validation.

        Thread-safe: Uses lock to protect samples deque and cache invalidation.

        Args:
            value: Sample value to add (must be a finite number, excludes bool)

        Raises:
            ValueError: If value is not a finite number (NaN, infinity, or bool)

        """
        # Type validation
        if not isinstance(value, (int, float)):
            raise ValueError(f"AnomalyDetector.add_sample: value must be numeric, got {type(value).__name__}")
        if isinstance(value, bool):
            raise ValueError("AnomalyDetector.add_sample: value cannot be boolean")
        if not math.isfinite(value):
            raise ValueError(f"AnomalyDetector.add_sample: value must be finite, got {value}")

        with self._samples_lock:
            was_full = len(self._samples) == self.window_size
            self._samples.append(value)
            if was_full:
                self._samples_discarded = True

        with self._cache_lock:
            self._cache_valid = False

    def detect(
        self,
        value: float,
        algorithm: str = "z_score",
        auto_add: bool = True,
    ) -> AnomalyResult:
        """Detect if value is anomalous using specified algorithm.

        Args:
            value: Value to check for anomaly
            algorithm: Detection algorithm ('z_score', 'spike', 'iqr', 'all')
            auto_add: Automatically add value to window after detection

        Returns:
            AnomalyResult with detection details

        Raises:
            ValueError: If algorithm is unknown

        """
        if algorithm == "all":
            results = [
                self._detect_z_score(value),
                self._detect_spike(value),
                self._detect_iqr(value),
            ]
            return max(results, key=lambda r: (r.is_anomaly, r.severity.value if r.severity else ""))

        # Dictionary dispatch for O(1) algorithm lookup
        ALGORITHM_DETECTORS = {
            "z_score": self._detect_z_score,
            "spike": self._detect_spike,
            "iqr": self._detect_iqr,
        }

        detector = ALGORITHM_DETECTORS.get(algorithm)
        if detector is None:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        result = detector(value)

        if auto_add:
            self.add_sample(value)

        return result

    def _compute_stats(self) -> dict[str, Any]:
        """Compute statistics for current window.

        Thread-safe: Uses lock to protect cache access.

        Returns:
            Dictionary with statistical measures

        """
        with self._cache_lock:
            if self._samples_discarded:
                self._cache_valid = False
                self._samples_discarded = False

            if self._cache_valid and self._stats_cache is not None:
                return self._stats_cache

        with self._samples_lock:
            samples = list(self._samples)

        stats, valid = _compute_stats(samples, self._stats_cache, self._cache_valid)

        with self._cache_lock:
            self._stats_cache = stats
            self._cache_valid = valid

        return stats

    def _detect_z_score(self, value: float) -> AnomalyResult:
        """Detect anomalies using z-score method."""
        with self._samples_lock:
            sample_count = len(self._samples)

        if sample_count < self.min_samples:
            return AnomalyResult(
                is_anomaly=False,
                severity=None,
                anomaly_type=AnomalyType.Z_SCORE,
                value=value,
                threshold=0.0,
                message=f"Insufficient data ({sample_count} < {self.min_samples})",
                confidence=0.0,
                context={"sample_count": sample_count},
            )

        stats = self._compute_stats()

        if stats["stdev"] == 0:
            return AnomalyResult(
                is_anomaly=False,
                severity=None,
                anomaly_type=AnomalyType.Z_SCORE,
                value=value,
                threshold=0.0,
                message="Standard deviation is zero, cannot compute z-score",
                confidence=0.0,
                context=stats,
            )

        z_score = abs((value - stats["mean"]) / stats["stdev"])
        is_anomaly = z_score > self.z_score_threshold

        if z_score > Z_SCORE_CRITICAL_THRESHOLD:
            severity = AnomalySeverity.CRITICAL
        elif z_score > Z_SCORE_HIGH_THRESHOLD:
            severity = AnomalySeverity.HIGH
        elif z_score > self.z_score_threshold:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = None

        confidence = min(z_score / MAX_CONFIDENCE_Z_SCORE, 1.0) if is_anomaly else 0.0

        return AnomalyResult(
            is_anomaly=is_anomaly,
            severity=severity,
            anomaly_type=AnomalyType.Z_SCORE,
            value=value,
            threshold=self.z_score_threshold,
            message=f"Z-score: {z_score:.2f} (threshold: {self.z_score_threshold})",
            confidence=confidence,
            context={
                "z_score": z_score,
                "mean": stats["mean"],
                "stdev": stats["stdev"],
                "sample_count": stats["count"],
            },
        )

    def _detect_spike(self, value: float) -> AnomalyResult:
        """Detect sudden performance spikes."""
        with self._previous_value_lock:
            if self._previous_value is None:
                self._previous_value = value
                return AnomalyResult(
                    is_anomaly=False,
                    severity=None,
                    anomaly_type=AnomalyType.SPIKE,
                    value=value,
                    threshold=0.0,
                    message="No previous value for spike detection",
                    confidence=0.0,
                    context={"first_value": True},
                )
            previous_value = self._previous_value

        with self._samples_lock:
            sample_count = len(self._samples)

        if sample_count < self.min_samples:
            return AnomalyResult(
                is_anomaly=False,
                severity=None,
                anomaly_type=AnomalyType.SPIKE,
                value=value,
                threshold=0.0,
                message=f"Insufficient data ({sample_count} < {self.min_samples})",
                confidence=0.0,
                context={"sample_count": sample_count},
            )

        stats = self._compute_stats()
        absolute_change = abs(value - previous_value)
        relative_change = absolute_change / max(abs(previous_value), 1.0)
        baseline_volatility = stats["stdev"]

        is_anomaly = (absolute_change > (self.spike_threshold * baseline_volatility)
                      and relative_change > SPIKE_RELATIVE_CHANGE_THRESHOLD)

        if relative_change > SPIKE_CRITICAL_THRESHOLD:
            severity = AnomalySeverity.CRITICAL
        elif relative_change > SPIKE_HIGH_THRESHOLD:
            severity = AnomalySeverity.HIGH
        elif relative_change > SPIKE_MEDIUM_THRESHOLD:
            severity = AnomalySeverity.MEDIUM
        elif is_anomaly:
            severity = AnomalySeverity.LOW
        else:
            severity = None

        # Calculate confidence based on volatility and change magnitude
        if baseline_volatility > 0:
            confidence = min(absolute_change / (self.spike_threshold * baseline_volatility), 1.0)
        else:
            confidence = 1.0 if is_anomaly else 0.0

        with self._previous_value_lock:
            self._previous_value = value

        return AnomalyResult(
            is_anomaly=is_anomaly,
            severity=severity,
            anomaly_type=AnomalyType.SPIKE,
            value=value,
            threshold=self.spike_threshold,
            message=f"Spike detected: {absolute_change:.2f} change ({relative_change * 100:.1f}%)",
            confidence=confidence,
            context={
                "previous_value": previous_value,
                "absolute_change": absolute_change,
                "relative_change": relative_change,
                "baseline_volatility": baseline_volatility,
                "sample_count": stats["count"],
            },
        )

    def _detect_iqr(self, value: float) -> AnomalyResult:
        """Detect anomalies using Interquartile Range (IQR) method."""
        with self._samples_lock:
            sample_count = len(self._samples)

        if sample_count < self.min_samples:
            return AnomalyResult(
                is_anomaly=False,
                severity=None,
                anomaly_type=AnomalyType.IQR,
                value=value,
                threshold=0.0,
                message=f"Insufficient data ({sample_count} < {self.min_samples})",
                confidence=0.0,
                context={"sample_count": sample_count},
            )

        stats = self._compute_stats()

        if stats["iqr"] == 0:
            return AnomalyResult(
                is_anomaly=False,
                severity=None,
                anomaly_type=AnomalyType.IQR,
                value=value,
                threshold=0.0,
                message="IQR is zero, cannot detect outliers",
                confidence=0.0,
                context=stats,
            )

        lower_bound = stats["q1"] - (self.iqr_multiplier * stats["iqr"])
        upper_bound = stats["q3"] + (self.iqr_multiplier * stats["iqr"])
        is_anomaly = value < lower_bound or value > upper_bound

        if is_anomaly:
            distance = max(abs(lower_bound - value), abs(upper_bound - value)) / stats["iqr"]
            if distance > IQR_CRITICAL_DISTANCE:
                severity = AnomalySeverity.CRITICAL
            elif distance > IQR_HIGH_DISTANCE:
                severity = AnomalySeverity.HIGH
            elif distance > IQR_MEDIUM_DISTANCE:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            confidence = min(distance / MAX_CONFIDENCE_IQR_DISTANCE, 1.0)
        else:
            severity = None
            confidence = 0.0

        return AnomalyResult(
            is_anomaly=is_anomaly,
            severity=severity,
            anomaly_type=AnomalyType.IQR,
            value=value,
            threshold=self.iqr_multiplier,
            message=f"Value {value} outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]",
            confidence=confidence,
            context={
                "q1": stats["q1"],
                "q3": stats["q3"],
                "iqr": stats["iqr"],
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "sample_count": stats["count"],
            },
        )

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics for the sliding window."""
        return self._compute_stats()

    def reset(self) -> None:
        """Reset detector state, clearing all samples."""
        with self._samples_lock:
            self._samples.clear()

        with self._previous_value_lock:
            self._previous_value = None

        with self._cache_lock:
            self._stats_cache = None
            self._cache_valid = False
            self._samples_discarded = False

        self.reset_time_aware_baselines()

    def __len__(self) -> int:
        """Return current number of samples in window."""
        with self._samples_lock:
            return len(self._samples)

    # ===== TIME-AWARE BASELINE LEARNING =====

    def add_time_aware_sample(self, value: float, timestamp: float) -> None:
        """Add a sample to time-binned historical data for baseline learning."""
        # Type validation
        if not isinstance(value, (int, float)):
            raise ValueError("add_time_aware_sample: value must be numeric")
        if isinstance(value, bool):
            raise ValueError("add_time_aware_sample: value cannot be boolean")
        if not math.isfinite(value):
            raise ValueError("add_time_aware_sample: value must be finite")
        if not isinstance(timestamp, (int, float)) or timestamp < 0:
            raise ValueError("add_time_aware_sample: timestamp must be non-negative numeric")

        datetime_utc = dt.datetime.utcfromtimestamp(timestamp)
        day_of_week = datetime_utc.weekday()
        hour = datetime_utc.hour
        time_bin_key = (day_of_week, hour)

        with self._time_bins_lock:
            if time_bin_key not in self._time_bins:
                self._time_bins[time_bin_key] = deque(maxlen=MAX_SAMPLES_PER_TIME_BIN)
            self._time_bins[time_bin_key].append(value)

    def learn_baselines(self) -> dict[tuple[int, int], BaselineStats]:
        """Calculate baseline statistics for each time bin."""
        new_baselines = {}

        with self._time_bins_lock:
            time_bins_copy = dict(self._time_bins)

        for time_bin_key, samples in time_bins_copy.items():
            if len(samples) < self._min_samples_per_bin:
                continue

            sorted_samples = sorted(samples)
            n = len(sorted_samples)
            avg = statistics.mean(samples)
            p95_index = int(n * 0.95)
            p95 = sorted_samples[min(p95_index, n - 1)]
            p99_index = int(n * 0.99)
            p99 = sorted_samples[min(p99_index, n - 1)]

            new_baselines[time_bin_key] = BaselineStats(
                avg=avg,
                p95=p95,
                p99=p99,
                sample_count=n,
                min_samples_required=self._min_samples_per_bin,
            )

        with self._baselines_lock:
            self._baselines = new_baselines

        return new_baselines

    def is_deviation_from_baseline(
        self,
        value: float,
        timestamp: float,
        threshold_percentile: str = "p95",
    ) -> tuple[bool, Optional[BaselineStats], str]:
        """Check if value deviates from time-aware baseline."""
        if threshold_percentile not in ("p95", "p99"):
            raise ValueError("threshold_percentile must be 'p95' or 'p99'")

        datetime_utc = dt.datetime.utcfromtimestamp(timestamp)
        day_of_week = datetime_utc.weekday()
        hour = datetime_utc.hour
        time_bin_key = (day_of_week, hour)

        with self._baselines_lock:
            baseline = self._baselines.get(time_bin_key)

        if baseline is None:
            return (False, None, f"No baseline learned for time slot (day={day_of_week}, hour={hour})")

        if not baseline.is_reliable():
            return (False, baseline, f"Baseline not reliable: {baseline.sample_count} < {baseline.min_samples_required} samples")

        threshold = baseline.p95 if threshold_percentile == "p95" else baseline.p99
        is_deviation = value > threshold

        if is_deviation:
            percent_over = ((value - threshold) / threshold) * 100
            message = f"Value {value:.2f}ms exceeds {threshold_percentile} baseline {threshold:.2f}ms for time slot (day={day_of_week}, hour={hour}) by {percent_over:.1f}%"
        else:
            message = f"Value {value:.2f}ms within normal range for time slot (day={day_of_week}, hour={hour}): {threshold_percentile}={threshold:.2f}ms"

        return (is_deviation, baseline, message)

    def get_baselines(self) -> dict[tuple[int, int], BaselineStats]:
        """Get all learned baselines."""
        with self._baselines_lock:
            return dict(self._baselines)

    def get_time_bin_sample_count(self, day_of_week: int, hour: int) -> int:
        """Get the number of samples for a specific time bin."""
        time_bin_key = (day_of_week, hour)
        with self._time_bins_lock:
            samples = self._time_bins.get(time_bin_key, [])
            return len(samples)

    def reset_time_aware_baselines(self) -> None:
        """Reset all time-aware baseline data."""
        with self._time_bins_lock:
            self._time_bins.clear()

        with self._baselines_lock:
            self._baselines.clear()


__all__ = [
    "AnomalyDetector",
    "DEFAULT_WINDOW_SIZE",
    "DEFAULT_Z_SCORE_THRESHOLD",
    "DEFAULT_SPIKE_THRESHOLD",
    "DEFAULT_IQR_MULTIPLIER",
    "DEFAULT_MIN_SAMPLES",
]
