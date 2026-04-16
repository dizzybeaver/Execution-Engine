# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-28 - LoggingFuse health check implementation


"""logging_fuse_health.py - LoggingFuse Health Reporting
Version: 1.0.0
Date: 2026-03-28
Purpose: Health reporting for LoggingFuse system

Provides health check functions for LoggingFuse instances. LoggingFuse is a
simple failure tracking class (NOT a CircuitBreaker) that records when logging
operations fail. Unlike CBFuse, LoggingFuse does not have thresholds or disable
logic - it simply tracks failure history.

Key Functions:
    - get_logging_fuse_health(): Complete LoggingFuse health report
    - register_logging_fuse(): Register a LoggingFuse instance for tracking
    - unregister_logging_fuse(): Unregister a LoggingFuse instance
    - get_all_logging_fuses(): Get all registered LoggingFuse instances

Registry Pattern:
    - Global registry tracks all LoggingFuse instances by name
    - Auto-registration in LoggingFuse.__init__() via modified class
    - Health checks query registry for complete status

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Any

from lee.gateway.gateway_core import (
    GatewayInterface,
    execute_operation,
    generate_correlation_id,
)

# Relative imports to avoid circular dependency
from .logging_fuse import (
    LoggingFuse,
    get_logging_fuse_registry,
)


def get_all_logging_fuses() -> dict[str, LoggingFuse]:
    """Get all registered LoggingFuse instances.

    Returns:
        Dictionary mapping fuse names to LoggingFuse instances

    Example:
        >>> fuses = get_all_logging_fuses()
        >>> for name, fuse in fuses.items():
        ...     print(f"{name}: {fuse.is_blown()}")
    """
    return get_logging_fuse_registry()


def get_logging_fuse_health(correlation_id: str = None) -> dict[str, Any]:
    """Get comprehensive LoggingFuse health report.

    Generates a complete health report for all registered LoggingFuse
    instances. Unlike CBFuse (circuit breaker fuse), LoggingFuse does NOT
    have thresholds, recovery logic, or disable behavior - it simply records
    that a failure occurred at some point.

    Args:
        correlation_id: Optional correlation ID for tracing

    Returns:
        Dictionary containing:
            - success: True if report generated successfully
            - timestamp: Report generation timestamp
            - total_fuses: Number of registered LoggingFuse instances
            - blown_fuses: Number with fuse=True (failed at some point)
            - operational_fuses: Number with fuse=False (never failed)
            - fuses: Dict of individual fuse statuses
            - interpretation: Human-readable summary

    Example:
        >>> report = get_logging_fuse_health()
        >>> print(report['interpretation'])
        'All logging systems operational - no failures detected'
        >>> print(report['blown_fuses'])
        0
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("lfh")

    try:
        try:

            execute_operation(GatewayInterface.LOGGING, "log_debug",
            message=f"[{correlation_id}] Generating LoggingFuse health report",
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        # Get all registered fuses
        fuses = get_all_logging_fuses()
        total_fuses = len(fuses)

        # Build individual fuse statuses
        fuse_statuses = {}
        blown_count = 0
        operational_count = 0

        for name, fuse in fuses.items():
            status = fuse.get_status()
            fuse_statuses[name] = status

            if status["fuse"]:
                blown_count += 1
            else:
                operational_count += 1

        # Generate interpretation
        interpretation = _generate_fuse_interpretation(
            total_fuses, blown_count, operational_count
        )

        # Build health report
        report = {
            "success": True,
            "timestamp": time.time(),
            "total_fuses": total_fuses,
            "blown_fuses": blown_count,
            "operational_fuses": operational_count,
            "fuses": fuse_statuses,
            "interpretation": interpretation,
        }

        status_msg = (
            f"[{correlation_id}] LoggingFuse health report complete: "
            f"{blown_count}/{total_fuses} blown"
        )
        try:

            execute_operation(GatewayInterface.LOGGING, "log_info",
            message=status_msg,
            total_fuses=total_fuses,
            blown_fuses=blown_count,
            operational_fuses=operational_count,
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        return report

    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ConnectionError, OSError) as e:
        try:

            execute_operation(GatewayInterface.LOGGING, "log_error",
            message=f"[{correlation_id}] LoggingFuse health report failed: {e!s}",
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        return {
            "success": False,
            "error": str(e),
            "timestamp": time.time(),
            "total_fuses": 0,
            "blown_fuses": 0,
            "operational_fuses": 0,
            "fuses": {},
            "interpretation": f"Error generating health report: {e}",
        }


def _generate_fuse_interpretation(
    total_fuses: int,
    blown_count: int,
    operational_count: int
) -> str:
    """Generate human-readable fuse health interpretation.

    Args:
        total_fuses: Total number of registered fuses
        blown_count: Number of blown fuses (failed at some point)
        operational_count: Number of operational fuses (never failed)

    Returns:
        Human-readable interpretation string
    """
    if total_fuses == 0:
        return (
            "No LoggingFuse instances registered - "
            "no logging systems tracked"
        )

    if blown_count == 0:
        return (
            f"All {operational_count} logging systems operational - "
            f"no failures detected"
        )

    if operational_count == 0:
        return (
            f"All {blown_count} logging systems have experienced failures - "
            "investigate logging infrastructure"
        )

    return (
        f"{operational_count} logging systems operational, "
        f"{blown_count} have experienced failures - "
        "review degraded logging components"
    )


__all__ = [
    "get_all_logging_fuses",
    "get_logging_fuse_health",
]
