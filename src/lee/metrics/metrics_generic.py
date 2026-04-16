"""metrics/metrics_generic.py

Version: 2025-12-23_2
Purpose: Core metrics base class with SUGA-ISP compliant debug tracing
Project: LEE
License: Apache 2.0

CONTAINS: MetricsCore base class
"""

import os
import threading
import time
from collections import OrderedDict, defaultdict, deque
from contextlib import nullcontext
from typing import Any, Optional

from lee.metrics.metrics_types import HTTPClientMetrics, ResponseMetrics


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"

# Memory limits for metrics (2026-03-29 fix)
MAX_METRICS_KEYS = 10000
MAX_HISTOGRAM_SAMPLES = 100  # Reduced from 1000 for memory efficiency
MAX_DISPATCHER_SAMPLES = 100  # Reduced from 1000 for memory efficiency

# Lazy imports for gateway to avoid circular dependency
_GatewayInterface = None
_execute_operation = None
_generate_correlation_id = None
_gateway_lock = threading.Lock()  # Thread safety for lazy imports


def _get_gateway():  # pylint: disable=global-statement
    """Get gateway imports with thread-safe lazy initialization.

    Uses double-checked locking pattern for performance in Lambda concurrent execution.
    Fast path: check without lock (read-only)
    Slow path: acquire lock only when initialization needed
    """
    global _GatewayInterface, _execute_operation, _generate_correlation_id

    # Fast path: check without lock (read-only, safe in Python)
    if _execute_operation is not None:
        return _GatewayInterface, _execute_operation, _generate_correlation_id

    # Slow path: acquire lock for initialization
    with _gateway_lock:
        # Double-check: another thread may have initialized while we waited
        if _execute_operation is not None:
            return _GatewayInterface, _execute_operation, _generate_correlation_id

        # Initialize gateway imports
        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            from lee.gateway.gateway_core import generate_correlation_id  # pylint: disable=import-outside-toplevel
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _generate_correlation_id = generate_correlation_id
        except ImportError:
            # Optional dependency - continue if unavailable
            if _is_debug_mode():
                print("[DEBUG] Metrics: Gateway import failed - continuing without gateway")

    return _GatewayInterface, _execute_operation, _generate_correlation_id


def _safe_debug_log(message: str, **_kwargs):
    """Safely log debug message without raising errors."""
    try:
        _gi, eo = _get_gateway()
        if eo is not None:
            _GatewayInterface, _execute_operation, _generate_correlation_id = _get_gateway()
            eo(_GatewayInterface.DEBUG, "log", message=message)
    except (AttributeError, TypeError, ValueError):
        # Optional dependency - continue if unavailable
        ...


def _safe_debug_timing(operation_name: str, **_kwargs):
    """Safely get debug timing context."""
    try:
        gi, eo = _get_gateway()
        if eo is not None and gi is not None:
            return eo(gi.DEBUG, "timing", operation_name=operation_name)
    except (AttributeError, TypeError, ValueError):
        # Optional dependency - continue if unavailable
        ...
    return nullcontext()


class MetricsCore:  # pylint: disable=too-many-instance-attributes
    """Core metrics manager base class."""

    def __init__(self, correlation_id: str = None, **_kwargs):
        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        self.correlation_id = correlation_id

        # Import gateway for debug logging (may fail during early initialization)
        execute_operation = None
        GatewayInterface = None
        try:
            from lee.gateway import GatewayInterface  # pylint: disable=import-outside-toplevel
            from lee.gateway import execute_operation as exec_op  # pylint: disable=import-outside-toplevel
            execute_operation = exec_op
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="METRICS",
                           message="MetricsCore.__init__ called")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        if execute_operation is not None:
            try:
                timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                             corr_id=correlation_id, scope="METRICS",
                                             operation_name="MetricsCore.__init__")
            except (ImportError, AttributeError, TypeError, ValueError):
                timing_ctx = nullcontext()
        else:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                # Use OrderedDict with size limit for metrics (LRU eviction)
                self._metrics = OrderedDict()
                self._counters = OrderedDict()
                self._gauges = OrderedDict()
                self._histograms = defaultdict(lambda: deque(maxlen=MAX_HISTOGRAM_SAMPLES))
                self._response_metrics = ResponseMetrics()
                self._http_metrics = HTTPClientMetrics()
                self._circuit_breaker_metrics = {}
                self._dispatcher_timings = defaultdict(lambda: deque(maxlen=MAX_DISPATCHER_SAMPLES))
                self._dispatcher_call_counts = defaultdict(int)
                self._operation_metrics = defaultdict(lambda: {"count": 0, "total_ms": 0, "durations": deque(maxlen=MAX_HISTOGRAM_SAMPLES)})

                if execute_operation is not None:
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="METRICS",
                                       message="MetricsCore.__init__ completed", success=True)
                    except ImportError:
                        # Optional dependency - continue if unavailable
                        ...
            except (ValueError, TypeError, AttributeError, ZeroDivisionError, RuntimeError) as e:
                if execute_operation is not None:
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                       message="MetricsCore.__init__ failed",
                                       error_type=type(e).__name__, error=str(e))
                    except ImportError:
                        # Optional dependency - continue if unavailable
                        ...
                raise

    def record_metric(self, name: str, value: float, dimensions: Optional[dict[str, str]] = None,
                     correlation_id: str = None, **_kwargs) -> bool:
        """Record metric value."""
        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="METRICS",
                           message="record_metric called",
                           name=name, value=value, has_dimensions=dimensions is not None)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="record_metric",
                                         name=name, value=value, has_dimensions=dimensions is not None)
        except (ImportError, AttributeError, TypeError, ValueError):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                key = self._build_metric_key(name, dimensions)
                # Enforce size limit with LRU eviction for metrics
                if len(self._metrics) >= MAX_METRICS_KEYS:
                    # Evict oldest entry (OrderedDict maintains insertion order)
                    self._metrics.popitem(last=False)
                self._metrics[key] = value
                try:
                    from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="METRICS",
                                   message="record_metric completed",
                                   success=True, metric_key=key)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return True
            except (ValueError, TypeError, AttributeError, ZeroDivisionError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="METRICS",
                                   message="record_metric failed",
                                   error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def increment_counter(self, name: Optional[str] = None, value: int = 1, correlation_id: str = None, **_kwargs) -> int:
        """Increment counter.

        This allows cache operations to call with metric_name parameter.
        """
        # Support parameter alias for backward compatibility
        if name is None and 'metric_name' in _kwargs:
            name = _kwargs['metric_name']
        elif name is None:
            raise ValueError("increment_counter requires either 'name' or 'metric_name' parameter")

        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="METRICS",
                           message="increment_counter called",
                           name=name, value=value)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="increment_counter",
                                         name=name, value=value)
        except (ImportError, AttributeError, TypeError, ValueError):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                # Enforce size limit with LRU eviction for counters
                if name not in self._counters:
                    if len(self._counters) >= MAX_METRICS_KEYS:
                        # Evict oldest entry
                        self._counters.popitem(last=False)
                    self._counters[name] = 0
                self._counters[name] += value
                result = self._counters[name]
                try:
                    from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="METRICS",
                                   message="increment_counter completed",
                                   success=True, new_count=result)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return result
            except (ValueError, TypeError, AttributeError, ZeroDivisionError) as e:
                try:
                    from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="METRICS",
                                   error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_stats(self, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
        """Get all statistics."""
        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        _safe_debug_log("get_stats called", corr_id=correlation_id, scope="METRICS")
        timing_ctx = _safe_debug_timing("get_stats", corr_id=correlation_id, scope="METRICS")

        with timing_ctx:
            try:
                stats = {
                    "metrics": dict(self._metrics),
                    "counters": dict(self._counters),
                    "gauges": dict(self._gauges),
                    "histograms": {k: list(v) for k, v in self._histograms.items()},
                }

                _safe_debug_log("get_stats completed", corr_id=correlation_id, scope="METRICS",
                               success=True, metrics_count=len(stats["metrics"]),
                               counters_count=len(stats["counters"]))
                return stats
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                _safe_debug_log("get_stats failed", corr_id=correlation_id, scope="METRICS",
                               error_type=type(e).__name__, error=str(e))
                raise

    def record_operation_metric(self, operation_name: str, success: bool, duration_ms: float,
                               error_type: Optional[str], correlation_id: str = None, **_kwargs) -> bool:  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Record operation metric."""
        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        _safe_debug_log("record_operation_metric called", corr_id=correlation_id, scope="METRICS",
                       operation_name=operation_name, success=success, duration_ms=duration_ms,
                       has_error=error_type is not None)

        timing_ctx = _safe_debug_timing("record_operation_metric", corr_id=correlation_id, scope="METRICS")

        with timing_ctx:
            try:
                dimensions = {"operation": operation_name, "success": str(success)}
                if error_type:
                    dimensions["error_type"] = error_type
                self.record_metric(f"operation.{operation_name}.count", 1.0, dimensions)
                if duration_ms > 0:
                    self.record_metric(f"operation.{operation_name}.duration_ms", duration_ms, dimensions)
                    op_key = operation_name
                    self._operation_metrics[op_key]["count"] += 1
                    self._operation_metrics[op_key]["total_ms"] += duration_ms
                    self._operation_metrics[op_key]["durations"].append(duration_ms)
                _safe_debug_log("record_operation_metric completed", corr_id=correlation_id, scope="METRICS",
                               success=True)
                return True
            except (ValueError, TypeError, AttributeError, ZeroDivisionError) as e:
                _safe_debug_log("record_operation_metric failed", corr_id=correlation_id, scope="METRICS",
                               error_type=type(e).__name__, error=str(e))
                raise

    def record_error_response(self, error_type: str, severity: str, category: str,
                             correlation_id: str = None, **_kwargs) -> bool:
        """Record error response."""
        if correlation_id is None:
            correlation_id = _generate_correlation_id("metric") if _generate_correlation_id else f"metric_{int(time.time() * 1000)}"

        _safe_debug_log("record_error_response called", corr_id=correlation_id, scope="METRICS",
                       error_type=error_type, severity=severity, category=category)

        timing_ctx = _safe_debug_timing("record_error_response", corr_id=correlation_id, scope="METRICS",
                                       error_type=error_type, severity=severity, category=category)

        with timing_ctx:
            try:
                dimensions = {"error_type": error_type, "severity": severity, "category": category}
                self.record_metric("error.response.count", 1.0, dimensions)
                _safe_debug_log("record_error_response completed", corr_id=correlation_id, scope="METRICS",
                               success=True)
                return True
            except (ValueError, TypeError, AttributeError) as e:
                _safe_debug_log("record_error_response failed", corr_id=correlation_id, scope="METRICS",
                               error_type=type(e).__name__, error=str(e))
                raise

    def _build_metric_key(self, name: str, dimensions: Optional[dict[str, str]]) -> str:
        """Build metric key from name and dimensions."""
        if not dimensions:
            return name
        dim_str = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dim_str}]"


# SINGLETON instance (lazy initialization to avoid circular dependency)
_MANAGEMENT = None
_management_lock = threading.Lock()  # Thread safety for singleton


def _get_management() -> MetricsCore:  # pylint: disable=global-statement
    """Get or create the metrics management singleton with thread-safe lazy initialization.

    Uses double-checked locking pattern for performance in Lambda concurrent execution.
    Fast path: check without lock (read-only)
    Slow path: acquire lock only when initialization needed
    """
    global _MANAGEMENT

    # Fast path: check without lock (read-only, safe in Python)
    if _MANAGEMENT is not None:
        return _MANAGEMENT

    # Slow path: acquire lock for initialization
    with _management_lock:
        # Double-check: another thread may have initialized while we waited
        if _MANAGEMENT is not None:
            return _MANAGEMENT

        # Initialize singleton
        _MANAGEMENT = MetricsCore()

    return _MANAGEMENT


# Module-level functions for convenience
def record_metric(name: str, value: float, dimensions: Optional[dict[str, str]] = None, **kwargs) -> bool:
    """Module-level wrapper for record_metric."""
    return _get_management().record_metric(name, value, dimensions, **kwargs)


def increment_counter(name: Optional[str] = None, value: int = 1, **kwargs) -> int:
    """Module-level wrapper for increment_counter.

    Supports both 'name' and 'metric_name' parameters for backward compatibility.
    """
    # Support parameter alias for backward compatibility
    if name is None and 'metric_name' in kwargs:
        name = kwargs['metric_name']
    elif name is None:
        raise ValueError("increment_counter requires either 'name' or 'metric_name' parameter")

    return _get_management().increment_counter(name, value, **kwargs)


def get_stats(**kwargs) -> dict[str, Any]:
    """Module-level wrapper for get_stats."""
    return _get_management().get_stats(**kwargs)


__all__ = [
    "_get_management",
    "MetricsCore",
    "get_stats",
    "increment_counter",
    "record_metric",
]
