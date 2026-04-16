"""cloudwatch/cloudwatch_core.py - CloudWatch Core Operations
Version: 2025-03-03_3
Purpose: Core CloudWatch operations implementation
License: Apache 2.0
Copyright 2025 Joseph Hersey

This module provides core CloudWatch operations implementation following
the SUGA-ISP architecture pattern. All operations are implemented as
standalone functions that can be called through the gateway interface.

Design Principles:
- Graceful failure (don't break Lambda if metrics fail)
- Consistent error sanitization for security
- Correlation ID tracking for debugging
- Type-safe parameter handling
"""

from typing import Any, Optional

from lee.cloudwatch.cloudwatch_client import (
    MetricDimension,
    MetricUnit,
    get_cloudwatch_client,
)
from lee.cloudwatch.security_patterns import sanitize_cloudwatch_error
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def _get_correlation_id(prefix: str = "cw") -> str:
    """Generate correlation ID for tracking."""
    return generate_correlation_id(prefix)


def _handle_cloudwatch_error(
    error: Exception,
    operation_name: str,
    correlation_id: str,
) -> bool:
    """Unified error handling for CloudWatch operations.

    Consolidates duplicate error handling logic across CloudWatch functions.
    Sanitizes errors, logs warnings via gateway, and returns False.

    Args:
        error: The exception that occurred
        operation_name: Name of the CloudWatch operation (e.g., "record_metric")
        correlation_id: Correlation ID for tracking

    Returns:
        False (indicating operation failed)
    """
    sanitized_error = sanitize_cloudwatch_error(str(error))
    try:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_warning",
            message=f"CloudWatch {operation_name} failed: {sanitized_error}",
            corr_id=correlation_id,
        )
    except (KeyError, AttributeError, RuntimeError):
        # Gateway unavailable - logging is optional
        ...
    return False


def _record_metric_implementation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    metric_name: str,
    value: float,
    unit: str = "Count",
    dimensions: Optional[list[dict[str, str]]] = None,
    namespace: Optional[str] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Record a CloudWatch metric.

        metric_name: Metric name
        value: Metric value
        unit: Metric unit (Count, Milliseconds, Bytes, etc.)
        dimensions: Optional list of {name, value} dicts
        namespace: Optional CloudWatch namespace
        correlation_id: Optional correlation ID

        True if metric recorded successfully, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        # Map unit string to enum
        try:
            metric_unit = MetricUnit[unit]
        except KeyError:
            metric_unit = MetricUnit.Count

        # Convert dimension dicts to MetricDimension objects
        metric_dimensions = None
        if dimensions:
            metric_dimensions = [
                MetricDimension(name=d["name"], value=d["value"])
                for d in dimensions
            ]

        # Get client and record metric
        client = get_cloudwatch_client()
        return client.put_metric(
            metric_name=metric_name,
            value=value,
            unit=metric_unit,
            dimensions=metric_dimensions,
            namespace=namespace,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        # Expected errors - invalid data types or missing keys
        return _handle_cloudwatch_error(e, "record_metric", correlation_id)
    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        return _handle_cloudwatch_error(e, "record_metric", correlation_id)


def _increment_counter_implementation(
    metric_name: str,
    value: float = 1.0,
    dimensions: Optional[list[dict[str, str]]] = None,
    namespace: Optional[str] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Increment a CloudWatch counter metric.

        metric_name: Metric name
        value: Value to increment by (default 1.0)
        dimensions: Optional list of {name, value} dicts
        namespace: Optional CloudWatch namespace
        correlation_id: Optional correlation ID

        True if counter incremented successfully, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        # Convert dimension dicts to MetricDimension objects
        metric_dimensions = None
        if dimensions:
            metric_dimensions = [
                MetricDimension(name=d["name"], value=d["value"])
                for d in dimensions
            ]

        # Get client and increment counter
        client = get_cloudwatch_client()
        return client.increment_counter(
            metric_name=metric_name,
            value=value,
            dimensions=metric_dimensions,
            namespace=namespace,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        # Expected errors - invalid data types or missing keys
        return _handle_cloudwatch_error(e, "increment_counter", correlation_id)
    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        return _handle_cloudwatch_error(e, "increment_counter", correlation_id)


def _record_timing_implementation(
    metric_name: str,
    duration_ms: float,
    dimensions: Optional[list[dict[str, str]]] = None,
    namespace: Optional[str] = None,
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Record a timing metric in milliseconds.

        metric_name: Metric name
        duration_ms: Duration in milliseconds
        dimensions: Optional list of {name, value} dicts
        namespace: Optional CloudWatch namespace
        correlation_id: Optional correlation ID

        True if timing recorded successfully, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        # Convert dimension dicts to MetricDimension objects
        metric_dimensions = None
        if dimensions:
            metric_dimensions = [
                MetricDimension(name=d["name"], value=d["value"])
                for d in dimensions
            ]

        # Get client and record timing
        client = get_cloudwatch_client()
        return client.record_timing(
            metric_name=metric_name,
            duration_ms=duration_ms,
            dimensions=metric_dimensions,
            namespace=namespace,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        # Expected errors - invalid data types or missing keys
        return _handle_cloudwatch_error(e, "record_timing", correlation_id)
    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        return _handle_cloudwatch_error(e, "record_timing", correlation_id)


def _flush_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Flush buffered metrics to CloudWatch.

        correlation_id: Optional correlation ID

        True if flush successful, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        return client.flush()

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch flush failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except (KeyError, AttributeError, RuntimeError):
            # Gateway unavailable - logging is optional
            pass
        return False


def _flush_on_shutdown_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Flush metrics on Lambda shutdown.

        correlation_id: Optional correlation ID

        True if flush successful, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        return client.flush_on_shutdown()

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch flush_on_shutdown failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except ImportError:
            pass
        return False


def _get_buffer_size_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> int:
    """Get current buffer size.

        correlation_id: Optional correlation ID

        Number of metrics in buffer

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        return client.get_buffer_size()

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch get_buffer_size failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except ImportError:
            pass
        return 0


def _is_enabled_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Check if CloudWatch metrics are enabled.

        correlation_id: Optional correlation ID

        True if enabled, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        return client.is_enabled()

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch is_enabled failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except ImportError:
            pass
        return False


def _get_stats_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> dict[str, Any]:
    """Get CloudWatch client statistics.

        correlation_id: Optional correlation ID

        Statistics dictionary

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        return {
            "enabled": client.is_enabled(),
            "buffer_size": client.get_buffer_size(),
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch get_stats failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except ImportError:
            pass
        return {
            "enabled": False,
            "buffer_size": 0,
            "error": sanitized_error,
        }


def _reset_implementation(
    correlation_id: Optional[str] = None,
    **_kwargs,
) -> bool:
    """Reset CloudWatch client failure count.

        correlation_id: Optional correlation ID

        True if reset successful, False otherwise

    """
    if correlation_id is None:
        correlation_id = _get_correlation_id()

    try:
        client = get_cloudwatch_client()
        client.reset_failure_count()
        return True

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network/system errors - CloudWatch unavailable
        sanitized_error = sanitize_cloudwatch_error(str(e))
        try:
            execute_operation(GatewayInterface.LOGGING,
                "log_warning",
                message=f"CloudWatch reset failed: {sanitized_error}",
                corr_id=correlation_id,
            )
        except ImportError:
            pass
        return False


__all__ = [
    "_flush_implementation",
    "_flush_on_shutdown_implementation",
    "_get_buffer_size_implementation",
    "_get_stats_implementation",
    "_increment_counter_implementation",
    "_is_enabled_implementation",
    "_record_metric_implementation",
    "_record_timing_implementation",
    "_reset_implementation",
]
