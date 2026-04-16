"""Load Prediction Gateway Integration for LEE Lambda Performance

Gateway integration functions for the load prediction system.
Provides SUGA-ISP compliant access through the SINGLETON interface.

Zero external dependencies - uses only Python stdlib.
"""

import threading
import time
from typing import Any, Optional

from lee.performance.classes.LoadPrediction import LoadPrediction
from lee.performance.classes.LoadPredictor_class import (
    DEFAULT_HISTORY_WINDOW,
    DEFAULT_MIN_SAMPLES,
    LoadPredictor,
)

# Singleton instance for Lambda load prediction
_load_predictor: Optional[LoadPredictor] = None
_load_predictor_lock = threading.Lock()
_load_predictor_initialized = False


def get_load_predictor(
    history_window: int = DEFAULT_HISTORY_WINDOW,
    reset: bool = False,
) -> LoadPredictor:
    """Get or create thread-safe singleton load predictor."""
    # pylint: disable=global-statement
    # Required for singleton pattern with thread-safe lazy initialization
    global _load_predictor, _load_predictor_initialized

    if _load_predictor is None or reset:
        with _load_predictor_lock:
            if _load_predictor is None or reset:
                if reset and _load_predictor is not None:
                    _load_predictor.reset()
                else:
                    _load_predictor = LoadPredictor(
                        history_window=history_window,
                        min_samples=DEFAULT_MIN_SAMPLES,
                    )
                _load_predictor_initialized = True

    return _load_predictor


def reset_load_predictor() -> None:
    """Reset the load predictor singleton state."""
    # pylint: disable=global-statement
    # Required for singleton pattern reset
    global _load_predictor_initialized

    with _load_predictor_lock:
        if _load_predictor is not None:
            _load_predictor.reset()
        _load_predictor_initialized = False


# ===== GATEWAY INTEGRATION FUNCTIONS =====

def load_predictor_record(
    duration_ms: float,
    success: bool = True,
    correlation_id: Optional[str] = None,
) -> None:
    """Record a request using the load predictor singleton."""
    _ = correlation_id  # Reserved for future tracing
    predictor = get_load_predictor()
    predictor.record_request(
        timestamp=time.time(),
        duration_ms=duration_ms,
        success=success,
    )


def load_predictor_predict(
    minutes_ahead: int = 5,
    correlation_id: Optional[str] = None,
) -> LoadPrediction:
    """Predict load using the load predictor singleton."""
    _ = correlation_id  # Reserved for future tracing
    predictor = get_load_predictor()
    return predictor.predict_load(minutes_ahead=minutes_ahead)


def load_predictor_get_stats(
    correlation_id: Optional[str] = None,
) -> dict[str, Any]:
    """Get pattern statistics from the load predictor."""
    _ = correlation_id  # Reserved for future tracing
    predictor = get_load_predictor()
    return predictor.get_pattern_stats()


def load_predictor_reset(correlation_id: Optional[str] = None) -> None:
    """Reset the load predictor state."""
    _ = correlation_id  # Reserved for future tracing
    reset_load_predictor()


__all__ = [
    "get_load_predictor",
    "reset_load_predictor",
    "load_predictor_record",
    "load_predictor_predict",
    "load_predictor_get_stats",
    "load_predictor_reset",
]
