# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""PERFORMANCE interface router for performance observability.

Provides gateway access to cold start tracking, resource profiling, anomaly detection,
and load prediction operations through the SUGA-ISP pattern.

Operations:
- get_cold_start_metrics: Get comprehensive cold start metrics
- is_cold_start: Check if current invocation is a cold start
- get_import_summary: Get summary of module import timings
- get_profile_stats: Get aggregated stats for an operation
- get_all_profile_stats: Get stats for all profiled operations
- reset_profiler: Reset resource profiler state
- get_performance_report: Get comprehensive performance report

Anomaly Detection (6 operations):
- detect_anomaly: Detect anomaly using specified algorithm
- add_anomaly_sample: Add sample to detector
- get_anomaly_stats: Get anomaly statistics
- reset_anomaly_detector: Clear detector
- get_anomaly_cache_status: Get cache status
- clear_anomaly_cache: Clear cache

Time-Aware Baselines (6 operations):
- add_time_aware_sample: Add sample with time bin
- learn_baselines: Force baseline learning
- is_deviation_from_baseline: Check deviation
- get_baselines: Get all baselines
- get_time_bin_sample_count: Get sample count for bin
- reset_time_aware_baselines: Clear baselines

Load Prediction (4 operations):
- record_load_request: Record request
- predict_load: Predict load for time slot
- get_load_stats: Get load statistics
- reset_load_predictor: Clear request history
"""

import time
from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.performance')
def _import_performance():
    from lee.performance import (
        get_cold_start_tracker,
        get_load_predictor,
        get_performance_detector,
        get_resource_profiler,
    )
    return {
        'get_cold_start_tracker': get_cold_start_tracker,
        'get_load_predictor': get_load_predictor,
        'get_performance_detector': get_performance_detector,
        'get_resource_profiler': get_resource_profiler,
    }


_performance_funcs = _import_performance()
_PERFORMANCE_AVAILABLE = _import_performance.__dict__.get(
    '_PERFORMANCE_AVAILABLE',
    False
)
_PERFORMANCE_IMPORT_ERROR = _import_performance.__dict__.get(
    '_PERFORMANCE_IMPORT_ERROR',
    None
)

if _PERFORMANCE_AVAILABLE:
    get_cold_start_tracker = _performance_funcs['get_cold_start_tracker']
    get_load_predictor = _performance_funcs['get_load_predictor']
    get_performance_detector = _performance_funcs['get_performance_detector']
    get_resource_profiler = _performance_funcs['get_resource_profiler']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        raise RuntimeError(
            f"Performance interface unavailable: {_PERFORMANCE_IMPORT_ERROR}"
        )

    get_cold_start_tracker = _stub_unavailable
    get_resource_profiler = _stub_unavailable
    get_performance_detector = _stub_unavailable
    get_load_predictor = _stub_unavailable


# ===== Wrapper Implementations =====

def get_cold_start_metrics(**_kwargs) -> dict[str, Any]:
    """Get comprehensive cold start metrics.

    Returns ColdStartMetrics dataclass with container phase, import timings,
    and invocation counts.

    Gateway Example:
        metrics = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_cold_start_metrics'
        )
    """
    tracker = get_cold_start_tracker()
    metrics = tracker.get_metrics()

    # Handle both string and enum container_phase values
    container_phase = metrics.container_phase
    phase_value = getattr(container_phase, 'value', None)
    if phase_value is not None:
        container_phase = phase_value
    else:
        container_phase = str(container_phase)

    return {
        "container_phase": container_phase,
        "import_count": metrics.import_count,
        "total_import_time_ms": metrics.total_import_time_ms,
        "average_import_time_ms": metrics.average_import_time_ms,
        "slowest_import_ms": metrics.slowest_import_ms,
        "slowest_import_module": metrics.slowest_import_module,
        "cold_start_complete_time": metrics.cold_start_complete_time,
        "first_request_time": metrics.first_request_time,
        "invocation_count": metrics.invocation_count,
    }


def is_cold_start(**_kwargs) -> bool:
    """Check if current invocation is a cold start."""
    tracker = get_cold_start_tracker()
    return tracker.is_cold_start()


def get_import_summary(**_kwargs) -> dict[str, Any]:
    """Get summary of all recorded module import timings."""
    tracker = get_cold_start_tracker()
    return tracker.get_import_summary()


def _stats_to_dict(stats) -> dict[str, Any]:
    """Convert AggregatedProfileStats dataclass to dictionary."""
    return {
        "operation_name": stats.operation_name,
        "execution_count": stats.execution_count,
        "success_count": stats.success_count,
        "failure_count": stats.failure_count,
        "total_duration_ms": stats.total_duration_ms,
        "avg_duration_ms": stats.avg_duration_ms,
        "min_duration_ms": stats.min_duration_ms,
        "max_duration_ms": stats.max_duration_ms,
        "total_memory_allocated_bytes": stats.total_memory_allocated_bytes,
        "avg_memory_allocated_bytes": stats.avg_memory_allocated_bytes,
        "peak_memory_bytes": stats.peak_memory_bytes,
        "last_execution_time": stats.last_execution_time,
    }


def get_profile_stats(operation_name: str, **_kwargs) -> dict[str, Any]:
    """Get aggregated stats for an operation."""
    profiler = get_resource_profiler()
    stats = profiler.get_stats(operation_name)
    if stats:
        return _stats_to_dict(stats)
    return {}


def get_all_profile_stats(**_kwargs) -> dict[str, dict[str, Any]]:
    """Get stats for all profiled operations."""
    profiler = get_resource_profiler()
    all_stats = profiler.get_all_stats()
    return {name: _stats_to_dict(stats) for name, stats in all_stats.items()}


def reset_profiler(**_kwargs) -> None:
    """Reset resource profiler state."""
    profiler = get_resource_profiler()
    profiler.reset()


def get_performance_report(**_kwargs) -> dict[str, Any]:
    """Get comprehensive performance report."""
    tracker = get_cold_start_tracker()

    return {
        "cold_start": get_cold_start_metrics(),
        "import_summary": tracker.get_import_summary(),
        "profiler_stats": get_all_profile_stats(),
    }


# ===== Anomaly Detection Operations =====

def detect_anomaly(
    value: float,
    algorithm: str = "z_score",
    auto_add: bool = True,
    **_kwargs
) -> dict[str, Any]:
    """Detect anomaly using specified algorithm.

    Args:
        value: Value to check for anomaly
        algorithm: Detection algorithm ('z_score', 'spike', 'iqr', 'all')
        auto_add: Automatically add value to window after detection

    Returns:
        AnomalyResult as dictionary with detection details

    Gateway Example:
        result = execute_operation(
            GatewayInterface.PERFORMANCE,
            'detect_anomaly',
            value=1500.0,
            algorithm='z_score'
        )
    """
    detector = get_performance_detector()
    result = detector.detect(value, algorithm=algorithm, auto_add=auto_add)
    return result.to_dict()


def add_anomaly_sample(value: float, **_kwargs) -> None:
    """Add a sample to the anomaly detector.

    Args:
        value: Sample value to add

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'add_anomaly_sample',
            value=1500.0
        )
    """
    detector = get_performance_detector()
    detector.add_sample(value)


def get_anomaly_stats(**_kwargs) -> dict[str, Any]:
    """Get current statistics from the anomaly detector.

    Returns:
        Dictionary with statistical measures (count, mean, stdev, median, q1, q3, iqr)

    Gateway Example:
        stats = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_anomaly_stats'
        )
    """
    detector = get_performance_detector()
    return detector.get_stats()


def reset_anomaly_detector(**_kwargs) -> None:
    """Reset the anomaly detector state.

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'reset_anomaly_detector'
        )
    """
    detector = get_performance_detector()
    detector.reset()


def get_anomaly_cache_status(**_kwargs) -> dict[str, Any]:
    """Get cache status for anomaly detector.

    Returns:
        Dictionary with cache status information

    Gateway Example:
        status = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_anomaly_cache_status'
        )
    """
    detector = get_performance_detector()
    return {
        "cache_valid": detector._cache_valid,
        "samples_discarded": detector._samples_discarded,
        "sample_count": len(detector),
    }


def clear_anomaly_cache(**_kwargs) -> None:
    """Clear anomaly detector statistics cache.

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'clear_anomaly_cache'
        )
    """
    detector = get_performance_detector()
    with detector._cache_lock:
        detector._stats_cache = None
        detector._cache_valid = False


# ===== Time-Aware Baseline Operations =====

def add_time_aware_sample(
    value: float,
    timestamp: float | None = None,
    **_kwargs
) -> None:
    """Add a time-aware sample to the anomaly detector.

    Args:
        value: Sample value to add
        timestamp: Unix timestamp (defaults to current time if None)

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'add_time_aware_sample',
            value=1500.0,
            timestamp=time.time()
        )
    """
    if timestamp is None:
        timestamp = time.time()
    detector = get_performance_detector()
    detector.add_time_aware_sample(value, timestamp)


def learn_baselines(**_kwargs) -> dict[str, Any]:
    """Learn baselines from time-aware samples.

    Returns:
        Dictionary mapping time bin keys to baseline statistics

    Gateway Example:
        baselines = execute_operation(
            GatewayInterface.PERFORMANCE,
            'learn_baselines'
        )
    """
    detector = get_performance_detector()
    baselines = detector.learn_baselines()
    return {
        str(k): v.to_dict()
        for k, v in baselines.items()
    }


def is_deviation_from_baseline(
    value: float,
    timestamp: float | None = None,
    threshold_percentile: str = "p95",
    **_kwargs
) -> dict[str, Any]:
    """Check if value deviates from time-aware baseline.

    Args:
        value: Value to check
        timestamp: Unix timestamp (defaults to current time if None)
        threshold_percentile: Which percentile to use as threshold ('p95' or 'p99')

    Returns:
        Dictionary with is_deviation, baseline_stats, and message

    Gateway Example:
        result = execute_operation(
            GatewayInterface.PERFORMANCE,
            'is_deviation_from_baseline',
            value=1500.0,
            timestamp=time.time(),
            threshold_percentile='p95'
        )
    """
    if timestamp is None:
        timestamp = time.time()
    detector = get_performance_detector()
    is_dev, baseline, msg = detector.is_deviation_from_baseline(
        value, timestamp, threshold_percentile
    )
    return {
        "is_deviation": is_dev,
        "baseline_stats": baseline.to_dict() if baseline else None,
        "message": msg,
    }


def get_baselines(**_kwargs) -> dict[str, Any]:
    """Get all learned baselines.

    Returns:
        Dictionary mapping time bin keys to baseline statistics

    Gateway Example:
        baselines = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_baselines'
        )
    """
    detector = get_performance_detector()
    baselines = detector.get_baselines()
    return {
        str(k): v.to_dict()
        for k, v in baselines.items()
    }


def get_time_bin_sample_count(day_of_week: int, hour: int, **_kwargs) -> int:
    """Get the number of samples for a specific time bin.

    Args:
        day_of_week: Day of week (0=Monday, 6=Sunday)
        hour: Hour of day (0-23)

    Returns:
        Number of samples in the time bin

    Gateway Example:
        count = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_time_bin_sample_count',
            day_of_week=0,
            hour=14
        )
    """
    detector = get_performance_detector()
    return detector.get_time_bin_sample_count(day_of_week, hour)


def reset_time_aware_baselines(**_kwargs) -> None:
    """Reset all time-aware baseline data.

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'reset_time_aware_baselines'
        )
    """
    detector = get_performance_detector()
    detector.reset_time_aware_baselines()


# ===== Load Prediction Operations =====

def record_load_request(
    duration_ms: float,
    success: bool = True,
    timestamp: float | None = None,
    **_kwargs
) -> None:
    """Record a request using the load predictor.

    Args:
        duration_ms: Request duration in milliseconds
        success: Whether the request succeeded
        timestamp: Request timestamp (defaults to current time if None)

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'record_load_request',
            duration_ms=1500,
            success=True
        )
    """
    if timestamp is None:
        timestamp = time.time()
    predictor = get_load_predictor()
    predictor.record_request(
        timestamp=timestamp,
        duration_ms=duration_ms,
        success=success
    )


def predict_load(
    minutes_ahead: int = 5,
    current_time: float | None = None,
    **_kwargs
) -> dict[str, Any]:
    """Predict load for a future time window.

    Args:
        minutes_ahead: Minutes into the future to predict
        current_time: Current time (defaults to now if None)

    Returns:
        LoadPrediction as dictionary with prediction details

    Gateway Example:
        prediction = execute_operation(
            GatewayInterface.PERFORMANCE,
            'predict_load',
            minutes_ahead=5
        )
    """
    predictor = get_load_predictor()
    prediction = predictor.predict_load(
        minutes_ahead=minutes_ahead,
        current_time=current_time
    )
    return prediction.to_dict()


def get_load_stats(**_kwargs) -> dict[str, Any]:
    """Get pattern statistics from the load predictor.

    Returns:
        Dictionary with pattern statistics

    Gateway Example:
        stats = execute_operation(
            GatewayInterface.PERFORMANCE,
            'get_load_stats'
        )
    """
    predictor = get_load_predictor()
    return predictor.get_pattern_stats()


def reset_load_predictor(**_kwargs) -> None:
    """Reset the load predictor state.

    Gateway Example:
        execute_operation(
            GatewayInterface.PERFORMANCE,
            'reset_load_predictor'
        )
    """
    predictor = get_load_predictor()
    predictor.reset()


# ===== Dispatch Configuration =====

# Dispatch dictionary for O(1) operation routing
_PERFORMANCE_DISPATCH = {
    # Core operations
    "get_cold_start_metrics": get_cold_start_metrics,
    "is_cold_start": is_cold_start,
    "get_import_summary": get_import_summary,
    "get_profile_stats": get_profile_stats,
    "get_all_profile_stats": get_all_profile_stats,
    "reset_profiler": reset_profiler,
    "get_performance_report": get_performance_report,

    # Anomaly Detection operations
    "detect_anomaly": detect_anomaly,
    "add_anomaly_sample": add_anomaly_sample,
    "get_anomaly_stats": get_anomaly_stats,
    "reset_anomaly_detector": reset_anomaly_detector,
    "get_anomaly_cache_status": get_anomaly_cache_status,
    "clear_anomaly_cache": clear_anomaly_cache,

    # Time-Aware Baseline operations
    "add_time_aware_sample": add_time_aware_sample,
    "learn_baselines": learn_baselines,
    "is_deviation_from_baseline": is_deviation_from_baseline,
    "get_baselines": get_baselines,
    "get_time_bin_sample_count": get_time_bin_sample_count,
    "reset_time_aware_baselines": reset_time_aware_baselines,

    # Load Prediction operations
    "record_load_request": record_load_request,
    "predict_load": predict_load,
    "get_load_stats": get_load_stats,
    "reset_load_predictor": reset_load_predictor,
}


# ===== Router Implementation =====

class _PerformanceRouter(BaseSimpleDispatchRouter):
    """Router for Performance interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            """Dummy module for BaseSimpleDispatchRouter initialization."""

            pass

        super().__init__(
            interface_name="Performance",
            core_module=DummyModule(),
            dispatch_map=_PERFORMANCE_DISPATCH
        )


_performance_router = _PerformanceRouter()


def execute_performance_operation(operation: str, **kwargs) -> Any:
    """Execute performance operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The performance operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from performance implementation
    """
    return _performance_router.execute(operation, **kwargs)


def list_performance_operations() -> list[str]:
    """List all available performance operations."""
    return list(_performance_router.dispatch_map.keys())


__all__ = [
    # Original operations (backward compatibility)
    "get_cold_start_metrics",
    "is_cold_start",
    "get_import_summary",
    "get_profile_stats",
    "get_all_profile_stats",
    "reset_profiler",
    "get_performance_report",

    # Anomaly Detection operations
    "detect_anomaly",
    "add_anomaly_sample",
    "get_anomaly_stats",
    "reset_anomaly_detector",
    "get_anomaly_cache_status",
    "clear_anomaly_cache",

    # Time-Aware Baseline operations
    "add_time_aware_sample",
    "learn_baselines",
    "is_deviation_from_baseline",
    "get_baselines",
    "get_time_bin_sample_count",
    "reset_time_aware_baselines",

    # Load Prediction operations
    "record_load_request",
    "predict_load",
    "get_load_stats",
    "reset_load_predictor",

    # Router functions
    "execute_performance_operation",
    "list_performance_operations",
    "_PERFORMANCE_AVAILABLE",
]
