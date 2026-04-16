"""Load Prediction System for LEE Lambda Performance

Implements predictive load analysis based on historical request patterns.
Zero external dependencies - uses only Python stdlib.
"""

import datetime
import statistics
import threading
import time
from collections import deque
from functools import lru_cache
from typing import Any, Optional

from lee.performance.classes.LoadPrediction import DAY_NAMES, LoadPrediction
from lee.performance.classes.RequestRecord import RequestRecord

# ===== CONSTANTS =====

DEFAULT_HISTORY_WINDOW: int = 1000
DEFAULT_MIN_SAMPLES: int = 10
SLOTS_PER_DAY: int = 24
SLOTS_PER_WEEK: int = 168
DEFAULT_CONFIDENCE: float = 0.0
MAX_CONFIDENCE: float = 1.0
MAX_SAMPLES_PER_SLOT: int = 1000
MAX_MINUTES_AHEAD: int = 1440


class LoadPredictor:
    """Load prediction system using time slot pattern analysis."""
    # pylint: disable=too-many-instance-attributes
    # All 11 attributes are necessary for thread-safe load prediction with caching

    def __init__(
        self,
        history_window: int = DEFAULT_HISTORY_WINDOW,
        min_samples: int = DEFAULT_MIN_SAMPLES,
    ):
        """Initialize load predictor with input validation."""
        if not isinstance(history_window, int) or history_window <= 0:
            raise ValueError("LoadPredictor: history_window must be positive integer")
        if not isinstance(min_samples, int) or min_samples <= 0:
            raise ValueError("LoadPredictor: min_samples must be positive integer")

        self.history_window = history_window
        self.min_samples = min_samples
        self.full_confidence_samples = min_samples * 3

        self._requests: deque[RequestRecord] = deque(maxlen=history_window)
        self._requests_lock = threading.Lock()
        self._patterns: dict[tuple[int, int], deque[float]] = {}
        self._patterns_lock = threading.Lock()
        self._last_request_time: Optional[float] = None
        self._last_request_time_lock = threading.Lock()

        self._cached_predict_load = lru_cache(maxsize=128)(self._predict_load_impl)
        self._cached_get_pattern_stats = lru_cache(maxsize=1)(self._get_pattern_stats_impl)

    def record_request(
        self,
        timestamp: float,
        duration_ms: float,
        success: bool = True,
    ) -> None:
        """Record a request for pattern learning."""
        if not isinstance(timestamp, (int, float)) or timestamp < 0:
            raise ValueError("LoadPredictor.record_request: timestamp must be non-negative numeric")
        if not isinstance(duration_ms, (int, float)) or duration_ms < 0:
            raise ValueError("LoadPredictor.record_request: duration_ms must be non-negative numeric")

        dt = datetime.datetime.utcfromtimestamp(timestamp)
        day_of_week = dt.weekday()
        hour = dt.hour

        record = RequestRecord(
            timestamp=timestamp,
            day_of_week=day_of_week,
            hour=hour,
            duration_ms=duration_ms,
            success=success,
        )

        with self._requests_lock:
            self._requests.append(record)

        time_slot = (day_of_week, hour)
        with self._patterns_lock:
            if time_slot not in self._patterns:
                self._patterns[time_slot] = deque(maxlen=MAX_SAMPLES_PER_SLOT)
            self._patterns[time_slot].append(duration_ms)

        with self._last_request_time_lock:
            self._last_request_time = timestamp

        # Clear prediction cache when new data recorded
        self._cached_predict_load.cache_clear()

    def _predict_load_impl(
        self,
        minutes_ahead: int = 5,
        current_time: Optional[float] = None,
    ) -> LoadPrediction:
        """Predict load for a future time window."""
        # pylint: disable=too-many-locals
        # Required for complex time series analysis with multiple intermediate calculations
        if not isinstance(minutes_ahead, (int, float)) or minutes_ahead < 0 or minutes_ahead > MAX_MINUTES_AHEAD:
            raise ValueError(f"LoadPredictor.predict_load: minutes_ahead must be 0-{MAX_MINUTES_AHEAD}")

        if current_time is None:
            current_time = time.time()

        target_time = current_time + (minutes_ahead * 60)
        dt = datetime.datetime.utcfromtimestamp(target_time)
        day_of_week = dt.weekday()
        hour = dt.hour
        time_slot = (day_of_week, hour)

        with self._patterns_lock:
            durations = list(self._patterns.get(time_slot, deque()))

        with self._requests_lock:
            total_requests = len(self._requests)

        sample_size = len(durations)

        if sample_size == 0:
            return LoadPrediction(
                predicted_requests_per_minute=1.0,
                confidence=DEFAULT_CONFIDENCE,
                sample_size=0,
                time_slot=time_slot,
                predicted_duration_ms=1000.0,
                pattern_description=f"No historical data for {DAY_NAMES[day_of_week]} {hour:02d}:00. Using conservative baseline.",
            )

        if sample_size < self.min_samples:
            predicted_duration = statistics.mean(durations) if durations else 1000.0
            confidence = min(sample_size / self.full_confidence_samples, MAX_CONFIDENCE)

            with self._patterns_lock:
                slots_with_data = len(self._patterns)

            if slots_with_data > 0:
                avg_requests_per_slot = total_requests / slots_with_data
                predicted_rpm = avg_requests_per_slot / 60
            else:
                predicted_rpm = 1.0

            return LoadPrediction(
                predicted_requests_per_minute=predicted_rpm,
                confidence=confidence,
                sample_size=sample_size,
                time_slot=time_slot,
                predicted_duration_ms=predicted_duration,
                pattern_description=f"Limited data for {DAY_NAMES[day_of_week]} {hour:02d}:00 ({sample_size} samples, {confidence * 100:.0f}% confidence). Based on {total_requests} total requests across {slots_with_data} time slots.",
            )

        predicted_duration = statistics.mean(durations)
        confidence = min(sample_size / self.full_confidence_samples, 1.0)
        slot_request_count = sample_size

        with self._requests_lock:
            if len(self._requests) > 1:
                oldest = self._requests[0].timestamp
                newest = self._requests[-1].timestamp
                time_span_days = (newest - oldest) / 86400
            else:
                time_span_days = 1.0

        if time_span_days > 0:
            slot_occurrences = time_span_days
            avg_requests_per_slot = slot_request_count / slot_occurrences
            predicted_rpm = avg_requests_per_slot / 60
        else:
            predicted_rpm = 1.0

        slots_with_data = len(self._patterns)

        return LoadPrediction(
            predicted_requests_per_minute=predicted_rpm,
            confidence=confidence,
            sample_size=sample_size,
            time_slot=time_slot,
            predicted_duration_ms=predicted_duration,
            pattern_description=f"{DAY_NAMES[day_of_week]} {hour:02d}:00: {confidence * 100:.0f}% confidence based on {sample_size} samples. Predicting {predicted_rpm:.2f} req/min over {slots_with_data} active time slots.",
        )

    def predict_load(
        self,
        minutes_ahead: int = 5,
        current_time: Optional[float] = None,
    ) -> LoadPrediction:
        """Predict load for a future time window (cached wrapper)."""
        if current_time is None:
            current_time = time.time()

        # Round current_time to nearest second for cache hit optimization
        current_time_rounded = int(current_time)

        return self._cached_predict_load(minutes_ahead, current_time_rounded)

    def _get_pattern_stats_impl(self) -> dict[str, Any]:
        """Get statistics about learned patterns (internal implementation)."""
        with self._requests_lock:
            total_requests = len(self._requests)

        with self._patterns_lock:
            unique_time_slots = len(self._patterns)
            slots_with_data = [(slot, len(durations)) for slot, durations in self._patterns.items()]

        total_samples = sum(count for _, count in slots_with_data)

        return {
            "total_requests": total_requests,
            "unique_time_slots": unique_time_slots,
            "slots_with_data": slots_with_data,
            "total_samples": total_samples,
            "history_window": self.history_window,
            "min_samples": self.min_samples,
            "full_confidence_threshold": self.full_confidence_samples,
            "coverage_percentage": (unique_time_slots / SLOTS_PER_WEEK) * 100 if SLOTS_PER_WEEK > 0 else 0,
        }

    def get_pattern_stats(self) -> dict[str, Any]:
        """Get statistics about learned patterns (cached wrapper)."""
        return self._cached_get_pattern_stats()

    def reset(self) -> None:
        """Reset predictor state, clearing all patterns."""
        with self._requests_lock, self._patterns_lock, self._last_request_time_lock:
            self._requests.clear()
            self._patterns.clear()
            self._last_request_time = None

        # Clear all caches when reset
        self._cached_predict_load.cache_clear()
        self._cached_get_pattern_stats.cache_clear()

    def __len__(self) -> int:
        """Return current number of requests in history."""
        with self._requests_lock:
            return len(self._requests)


__all__ = [
    "LoadPredictor",
    "DEFAULT_HISTORY_WINDOW",
    "DEFAULT_MIN_SAMPLES",
]
