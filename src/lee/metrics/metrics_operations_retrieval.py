"""metrics/metrics_operations_retrieval.py

Version: 2025-12-23_2
Purpose: Metrics retrieval operations with SUGA-ISP compliant debug tracing
Project: LEE
License: Apache 2.0

SPLIT FROM: metrics_operations.py (>350 lines)
CONTAINS: Metrics getter operations (get_* functions)
"""

from contextlib import nullcontext
from typing import Any, Optional

from lee.metrics.metrics_operations_core import MetricsCoreOperations

# SUGA-ISP compliant gateway imports (module level only)
try:
    from lee.gateway import GatewayInterface, execute_operation
    from lee.gateway.gateway_core import generate_correlation_id
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False


class MetricsRetrievalOperations(MetricsCoreOperations):
    """Metrics retrieval operations with debug tracing."""

    def get_response_metrics(self, correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get response metrics."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_response_metrics called")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_response_metrics")
        except ImportError:
            from contextlib import nullcontext
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                result = {
                    "total_responses": self._response_metrics.total_responses,
                    "successful_responses": self._response_metrics.successful_responses,
                    "error_responses": self._response_metrics.error_responses,
                    "success_rate": self._response_metrics.success_rate(),
                }
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_response_metrics completed",
                                     success=True, total_responses=result["total_responses"])
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return result
            except (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_response_metrics failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_response_metrics failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_http_metrics(self, correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get HTTP metrics."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_http_metrics called")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_http_metrics")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                result = {
                    "total_requests": self._http_metrics.total_requests,
                    "successful_requests": self._http_metrics.successful_requests,
                    "failed_requests": self._http_metrics.failed_requests,
                    "avg_response_time_ms": self._http_metrics.avg_response_time_ms,
                    "requests_by_method": dict(self._http_metrics.requests_by_method),
                    "requests_by_status": dict(self._http_metrics.requests_by_status),
                }
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_http_metrics completed",
                                     success=True, total_requests=result["total_requests"])
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return result
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_http_metrics failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_http_metrics failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None,
                                    correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get circuit breaker metrics."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_circuit_breaker_metrics called",
                             has_circuit_name=circuit_name is not None)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_circuit_breaker_metrics")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                if circuit_name:
                    if circuit_name in self._circuit_breaker_metrics:
                        metrics = self._circuit_breaker_metrics[circuit_name]
                        result = {
                            "circuit_name": metrics.circuit_name,
                            "total_calls": metrics.total_calls,
                            "successful_calls": metrics.successful_calls,
                            "failed_calls": metrics.failed_calls,
                            "circuit_opens": metrics.circuit_opens,
                            "half_open_attempts": metrics.half_open_attempts,
                        }
                    else:
                        result = {}
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="METRICS",
                                         message="get_circuit_breaker_metrics completed",
                                         success=True, circuit_name=circuit_name)
                    except ImportError:
                        # Optional dependency - continue if unavailable
                        ...
                    return result
                return {name: self.get_circuit_breaker_metrics(name) for name in self._circuit_breaker_metrics.keys()}
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_circuit_breaker_metrics failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_circuit_breaker_metrics failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_dispatcher_stats(self, correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get dispatcher stats."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_dispatcher_stats called")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_dispatcher_stats")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                stats = {}
                for key, timings in self._dispatcher_timings.items():
                    if timings:
                        stats[key] = {
                            "count": self._dispatcher_call_counts[key],
                            "avg_ms": sum(timings) / len(timings),
                            "min_ms": min(timings),
                            "max_ms": max(timings),
                        }
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_dispatcher_stats completed",
                                     success=True, interface_count=len(stats))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return stats
            except (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_dispatcher_stats failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_dispatcher_stats failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_operation_metrics(self, correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get operation metrics."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_operation_metrics called")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_operation_metrics")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                result = {op: {
                    "count": data["count"],
                    "avg_ms": data["total_ms"] / data["count"] if data["count"] > 0 else 0,
                    "total_ms": data["total_ms"],
                } for op, data in self._operation_metrics.items()}
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_operation_metrics completed",
                                     success=True, operation_count=len(result))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return result
            except (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_operation_metrics failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_operation_metrics failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise

    def get_performance_report(self, slow_threshold_ms: float = 100.0,
                               correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get performance report."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("met")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="METRICS",
                             message="get_performance_report called",
                             slow_threshold_ms=slow_threshold_ms)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id, scope="METRICS",
                                         operation_name="get_performance_report",
                                         slow_threshold_ms=slow_threshold_ms)
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                from datetime import datetime

                from lee.metrics.metrics_helper import calculate_percentiles
                operations = {}
                for op, data in self._operation_metrics.items():
                    if data["durations"] and data["count"] > 0:
                        percentiles = calculate_percentiles(data["durations"])
                        operations[op] = {
                            "count": data["count"],
                            "avg_ms": data["total_ms"] / data["count"],
                            "min_ms": min(data["durations"]),
                            "max_ms": max(data["durations"]),
                            "p50_ms": percentiles["p50"],
                            "p95_ms": percentiles["p95"],
                            "p99_ms": percentiles["p99"],
                        }
                slow_operations = [
                    {"operation": op, "p95_ms": metrics["p95_ms"], "max_ms": metrics["max_ms"]}
                    for op, metrics in operations.items()
                    if metrics["p95_ms"] > slow_threshold_ms
                ]
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "metrics_version": "2025-12-23_2",
                    "slow_threshold_ms": slow_threshold_ms,
                    "operations": operations,
                    "slow_operations": slow_operations,
                    "slow_operation_count": len(slow_operations),
                }
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_performance_report completed",
                                     success=True, slow_operation_count=len(slow_operations))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return result
            except (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError, ImportError) as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_performance_report failed",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="METRICS",
                                     message="get_performance_report failed with unexpected error",
                                     error_type=type(e).__name__, error=str(e))
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                raise


__all__ = [
    "MetricsRetrievalOperations",
]
