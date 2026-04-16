"""interface_cloudwatch.py - CloudWatch Metrics Interface Router

Version: 2026-04-02_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import re
from collections.abc import Sequence
from typing import Any

# Import shared security patterns
from lee.cloudwatch.security_patterns import sanitize_dimension_value
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


def _validate_metric_name(metric_name: str) -> str:
    """Validate and sanitize metric name to prevent injection attacks.

    MEDIUM SEVERITY: Prevents metric name injection which could lead to
    unauthorized metric creation or information disclosure.

    Security measures:
    - Only allows alphanumeric characters and _.:/@#-
    - Removes control characters
    - Enforces 255 character limit
    - Strips leading/trailing whitespace

        metric_name: Raw metric name

        Validated metric name

    Raises:
        ValueError: If metric name is invalid or contains only forbidden characters

    """
    if not isinstance(metric_name, str):
        raise ValueError("metric_name must be a string")

    # Remove control characters
    metric_name = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", metric_name)

    # Strip whitespace
    metric_name = metric_name.strip()

    # Enforce length limit
    if len(metric_name) > 255:
        metric_name = metric_name[:255]

    # Validate allowed characters: alphanumeric, space, and _.:/@#-
    # Use re.sub() to remove invalid characters (more efficient than loop)
    sanitized = re.sub(r"[^A-Za-z0-9\s_.:/@#-]", "", metric_name)

    # Remove consecutive spaces and trim
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if not sanitized:
        raise ValueError(
            "metric_name must contain valid characters "
            "(alphanumeric, space, and _.:/@#-)",
        )

    return sanitized


def _sanitize_dimension_name(name: str) -> str:
    """Sanitize dimension name to prevent injection and credential exfiltration.

    MEDIUM SEVERITY: Validates dimension names to prevent injection attacks
    and ensures they comply with CloudWatch naming requirements.

    Security measures:
    - Only allows alphanumeric characters and _.:/@#-
    - Removes control characters
    - Enforces 255 character limit
    - Strips leading/trailing whitespace

        name: Raw dimension name

        Sanitized dimension name

    Raises:
        ValueError: If dimension name is invalid or contains only forbidden characters

    """
    if not isinstance(name, str):
        raise ValueError("dimension name must be a string")

    # Remove control characters
    name = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", name)

    # Strip whitespace
    name = name.strip()

    # Enforce length limit
    if len(name) > 255:
        name = name[:255]

    # Validate allowed characters: alphanumeric, space, and _.:/@#-
    # Use re.sub() to remove invalid characters (more efficient than loop)
    sanitized = re.sub(r"[^A-Za-z0-9\s_.:/@#-]", "", name)

    # Remove consecutive spaces and trim
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if not sanitized:
        raise ValueError(
            "dimension name must contain valid characters "
            "(alphanumeric, space, and _.:/@#-)",
        )

    return sanitized


def _validate_dimension_length(dimension: dict[str, str]) -> None:
    """Validate dimension name and value length.

    INFO SEVERITY: Ensures dimensions comply with CloudWatch limits
    to avoid API rejection.

        dimension: Dimension dictionary with 'name' and 'value' keys

    Raises:
        ValueError: If dimension name or value exceeds 255 characters

    """
    if "name" in dimension and len(dimension["name"]) > 255:
        raise ValueError("Dimension name must be 255 characters or less")

    if "value" in dimension and len(dimension["value"]) > 255:
        raise ValueError("Dimension value must be 255 characters or less")


def _validate_metric_params(kwargs: dict[str, Any], operation: str) -> None:
    """Validate metric parameters with security sanitization."""
    if "metric_name" not in kwargs:
        raise ValueError(
            f"cloudwatch.{operation} requires 'metric_name' parameter",
        )

    # Validate and sanitize metric_name (prevent injection)
    metric_name = kwargs.get("metric_name")
    kwargs["metric_name"] = _validate_metric_name(metric_name)

    # Validate value if present
    if "value" in kwargs:
        try:
            kwargs["value"] = float(kwargs["value"])
        except (ValueError, TypeError) as exc:
            raise ValueError("value must be numeric") from exc

    # Validate duration_ms if present
    if "duration_ms" in kwargs:
        try:
            kwargs["duration_ms"] = float(kwargs["duration_ms"])
        except (ValueError, TypeError) as exc:
            raise ValueError("duration_ms must be numeric") from exc

    # Validate and sanitize dimensions if present
    if "dimensions" in kwargs and kwargs["dimensions"] is not None:
        dimensions = kwargs["dimensions"]
        if not isinstance(dimensions, Sequence):
            raise ValueError("dimensions must be a sequence")
        sanitized_dimensions = []
        for dim in dimensions:
            if not isinstance(dim, dict):
                raise ValueError("each dimension must be a dict")
            if "name" not in dim or "value" not in dim:
                raise ValueError(
                    "each dimension must have 'name' and 'value' keys",
                )

            # Validate dimension length
            _validate_dimension_length(dim)

            # Sanitize dimension name and value (prevent credential exfiltration)
            sanitized_dim = {
                "name": _sanitize_dimension_name(dim["name"]),
                "value": sanitize_dimension_value(dim["value"]),
            }
            sanitized_dimensions.append(sanitized_dim)

        kwargs["dimensions"] = sanitized_dimensions


def _get_cloudwatch_functions():
    """Lazy import CloudWatch core functions (SUGA-ISP compliant)."""
    # pylint: disable=import-outside-toplevel
    try:
        from lee.cloudwatch.cloudwatch_core import (
            _flush_implementation,
            _flush_on_shutdown_implementation,
            _get_buffer_size_implementation,
            _get_stats_implementation,
            _increment_counter_implementation,
            _is_enabled_implementation,
            _record_metric_implementation,
            _record_timing_implementation,
            _reset_implementation,
        )
        return {
            "record": _record_metric_implementation,
            "record_metric": _record_metric_implementation,
            "increment": _increment_counter_implementation,
            "increment_counter": _increment_counter_implementation,
            "timing": _record_timing_implementation,
            "record_timing": _record_timing_implementation,
            "flush": _flush_implementation,
            "flush_metrics": _flush_implementation,
            "flush_on_shutdown": _flush_on_shutdown_implementation,
            "get_buffer_size": _get_buffer_size_implementation,
            "is_enabled": _is_enabled_implementation,
            "get_stats": _get_stats_implementation,
            "reset": _reset_implementation,
            "reset_cloudwatch": _reset_implementation,
        }
    except ImportError as e:
        raise RuntimeError(f"Failed to import CloudWatch core functions: {e}") from e


def _get_cloudwatch_impls():
    """Lazy import CloudWatch core functions (SUGA-ISP compliant)."""
    # pylint: disable=import-outside-toplevel
    try:
        from lee.cloudwatch.cloudwatch_core import (
            _flush_implementation,
            _flush_on_shutdown_implementation,
            _get_buffer_size_implementation,
            _get_stats_implementation,
            _increment_counter_implementation,
            _is_enabled_implementation,
            _record_metric_implementation,
            _record_timing_implementation,
            _reset_implementation,
        )
        return {
            "record": _record_metric_implementation,
            "record_metric": _record_metric_implementation,
            "increment": _increment_counter_implementation,
            "increment_counter": _increment_counter_implementation,
            "timing": _record_timing_implementation,
            "record_timing": _record_timing_implementation,
            "flush": _flush_implementation,
            "flush_metrics": _flush_implementation,
            "flush_on_shutdown": _flush_on_shutdown_implementation,
            "get_buffer_size": _get_buffer_size_implementation,
            "is_enabled": _is_enabled_implementation,
            "get_stats": _get_stats_implementation,
            "reset": _reset_implementation,
            "reset_cloudwatch": _reset_implementation,
        }
    except ImportError as e:
        raise RuntimeError(f"Failed to import CloudWatch core functions: {e}") from e


def _record_impl(**kwargs):
    """Record a CloudWatch metric."""
    _validate_metric_params(kwargs, "record")
    return _get_cloudwatch_impls()["record"](**kwargs)


def _record_metric_impl(**kwargs):
    """Record a CloudWatch metric."""
    _validate_metric_params(kwargs, "record_metric")
    return _get_cloudwatch_impls()["record_metric"](**kwargs)


def _increment_impl(**kwargs):
    """Increment a counter metric."""
    _validate_metric_params(kwargs, "increment")
    return _get_cloudwatch_impls()["increment"](**kwargs)


def _increment_counter_impl(**kwargs):
    """Increment a counter metric."""
    _validate_metric_params(kwargs, "increment_counter")
    return _get_cloudwatch_impls()["increment_counter"](**kwargs)


def _timing_impl(**kwargs):
    """Record a timing metric."""
    _validate_metric_params(kwargs, "timing")
    return _get_cloudwatch_impls()["timing"](**kwargs)


def _record_timing_impl(**kwargs):
    """Record a timing metric."""
    _validate_metric_params(kwargs, "record_timing")
    return _get_cloudwatch_impls()["record_timing"](**kwargs)


def _flush_impl(**kwargs):
    """Flush buffered metrics."""
    return _get_cloudwatch_impls()["flush"](**kwargs)


def _flush_metrics_impl(**kwargs):
    """Flush buffered metrics."""
    return _get_cloudwatch_impls()["flush_metrics"](**kwargs)


def _flush_on_shutdown_impl(**kwargs):
    """Flush on Lambda shutdown."""
    return _get_cloudwatch_impls()["flush_on_shutdown"](**kwargs)


def _get_buffer_size_impl(**kwargs):
    """Get current buffer size."""
    return _get_cloudwatch_impls()["get_buffer_size"](**kwargs)


def _is_enabled_impl(**kwargs):
    """Check if CloudWatch is enabled."""
    return _get_cloudwatch_impls()["is_enabled"](**kwargs)


def _get_stats_impl(**kwargs):
    """Get CloudWatch client statistics."""
    return _get_cloudwatch_impls()["get_stats"](**kwargs)


def _reset_impl(**kwargs):
    """Reset failure count."""
    return _get_cloudwatch_impls()["reset"](**kwargs)


def _reset_cloudwatch_impl(**kwargs):
    """Reset failure count."""
    return _get_cloudwatch_impls()["reset_cloudwatch"](**kwargs)


_CLOUDWATCH_DISPATCH = {
    "record": _record_impl,
    "record_metric": _record_metric_impl,
    "increment": _increment_impl,
    "increment_counter": _increment_counter_impl,
    "timing": _timing_impl,
    "record_timing": _record_timing_impl,
    "flush": _flush_impl,
    "flush_metrics": _flush_metrics_impl,
    "flush_on_shutdown": _flush_on_shutdown_impl,
    "get_buffer_size": _get_buffer_size_impl,
    "is_enabled": _is_enabled_impl,
    "get_stats": _get_stats_impl,
    "reset": _reset_impl,
    "reset_cloudwatch": _reset_cloudwatch_impl,
}


class _CloudWatchRouter(BaseSimpleDispatchRouter):
    """Router for CloudWatch interface operations.

    Attributes:
        interface_name: Name of the interface
        core_module: Dummy module for base router
        dispatch_map: Dictionary mapping operations to handlers
    """

    def __init__(self):
        """Initialize CloudWatch router with dummy module and dispatch map."""
        class DummyModule:
            """Dummy module for BaseSimpleDispatchRouter compatibility."""

        super().__init__(
            interface_name="CloudWatch",
            core_module=DummyModule(),
            dispatch_map=_CLOUDWATCH_DISPATCH
        )


_cloudwatch_router = _CloudWatchRouter()


def execute_cloudwatch_operation(operation: str, **kwargs) -> Any:
    """Execute CloudWatch operation with validation and error handling.

    Pattern: Interface -> Core (lazy import)

    Args:
        operation: Operation name (record_metric, increment_counter, etc.)
        **kwargs: Operation-specific parameters

    Returns:
        Operation result (typically bool for success/failure)

    Raises:
        ValueError: Unknown operation or invalid parameters
        RuntimeError: Implementation import failure

    Valid Operations:
        - record_metric: Record a CloudWatch metric
          Required: metric_name, value
          Optional: unit, dimensions, namespace

        - increment_counter: Increment a counter metric
          Required: metric_name
          Optional: value (default 1.0), dimensions, namespace

        - record_timing: Record a timing metric
          Required: metric_name, duration_ms
          Optional: dimensions, namespace

        - flush: Flush buffered metrics
        - flush_on_shutdown: Flush on Lambda shutdown
        - get_buffer_size: Get current buffer size
        - is_enabled: Check if CloudWatch is enabled
        - get_stats: Get CloudWatch client statistics
        - reset: Reset failure count

    """
    return _cloudwatch_router.execute(operation, **kwargs)


__all__ = ["execute_cloudwatch_operation"]
