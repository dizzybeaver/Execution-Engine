# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-28 - CBFuse health integration implementation


"""circuit_breaker_health.py - CBFuse Health Integration
Version: 1.0.0
Date: 2026-03-28
Purpose: Health reporting for CBFuse (Circuit Breaker Fuse) system

Provides health check functions that integrate CBFuse status into overall
system health reports. CBFuse provides permanent trip history that survives
circuit breaker resets, allowing health checks to distinguish between
"never failed" and "recovered after failure".

Key Functions:
    - get_cbfuse_health_report(): Complete CBFuse health report
    - format_cbfuse_status(): Format individual breaker status
    - get_cbfuse_alerts(): Return blown fuse alerts with recommendations

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Any

from lee.circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager
from lee.gateway.gateway_core import (
    GatewayInterface,
    execute_operation,
    generate_correlation_id,
)


def get_cbfuse_health_report(correlation_id: str = None) -> dict[str, Any]:
    """Get comprehensive CBFuse health report.

    Generates a complete health report for all circuit breakers with their
    CBFuse status. Includes overall system status, individual breaker states,
    blown fuse alerts, and actionable recommendations.

    Args:
        correlation_id: Optional correlation ID for tracing

    Returns:
        Dictionary containing:
            - success: True if report generated successfully
            - overall_status: 'healthy', 'degraded', 'unhealthy', or 'unknown'
            - timestamp: Report generation timestamp
            - total_breakers: Total number of circuit breakers
            - monitored_breakers: Breakers with enable_cbfuse=True
            - expected_breakers: Breakers with enable_cbfuse=False
            - blown_fuses: Count of blown fuses (cbfuse=True)
            - breakers: Dict of all breaker statuses with cbfuse info
            - alerts: List of blown fuse alerts with recommendations
            - interpretation: Human-readable summary

    Example:
        >>> report = get_cbfuse_health_report()
        >>> print(report['overall_status'])
        'degraded'
        >>> print(report['alerts'][0]['recommendation'])
        'Investigate observability breaker trip - unexpected failure'
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cbh")

    try:
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                "log_debug",
                message=f"[{correlation_id}] Generating CBFuse health report",
            )
        except (ImportError, AttributeError, KeyError, TypeError):
            # Optional dependency - continue if unavailable
            ...

        # Get circuit breaker manager
        manager = get_circuit_breaker_manager()

        # Get CBFuse summary from manager
        summary = manager.get_cbfuse_summary(correlation_id=correlation_id)

        if "error" in summary:
            return {
                "success": False,
                "error": summary.get("error"),
                "overall_status": "unknown",
                "timestamp": time.time(),
            }

        # Extract breaker information
        breakers = summary.get("breakers", {})
        blown_fuses = summary.get("blown_fuses", 0)
        total_breakers = summary.get("total_breakers", 0)

        # Determine overall status
        overall_status = _determine_overall_status(summary)

        # Generate alerts for blown fuses
        alerts = get_cbfuse_alerts(correlation_id=correlation_id)

        # Generate interpretation
        interpretation = _generate_health_interpretation(summary, alerts)

        # Build health report
        report = {
            "success": True,
            "overall_status": overall_status,
            "timestamp": time.time(),
            "total_breakers": total_breakers,
            "monitored_breakers": summary.get("monitored_breakers", 0),
            "expected_breakers": summary.get("expected_breakers", 0),
            "blown_fuses": blown_fuses,
            "breakers": breakers,
            "alerts": alerts,
            "interpretation": interpretation,
        }

        status_msg = (
            f"[{correlation_id}] CBFuse health report complete: {overall_status}"
        )
        try:

            execute_operation(GatewayInterface.LOGGING, "log_info",
            message=status_msg,
            overall_status=overall_status,
            blown_fuses=blown_fuses,
            total_breakers=total_breakers,
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        return report

    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ConnectionError, OSError) as e:
        try:

            execute_operation(GatewayInterface.LOGGING, "log_error",
            message=f"[{correlation_id}] CBFuse health report failed: {e!s}",
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        return {
            "success": False,
            "error": str(e),
            "overall_status": "error",
            "timestamp": time.time(),
        }


def format_cbfuse_status(breaker: dict[str, Any]) -> dict[str, Any]:
    """Format individual circuit breaker CBFuse status.

    Formats a circuit breaker's status into a human-readable format with
    clear interpretation of CBFuse state.

    Args:
        breaker: Circuit breaker status dict (from breaker.get_status())

    Returns:
        Dictionary containing:
            - name: Breaker name
            - healthy: Current circuit state (True = closed/operational)
            - cbfuse: CBFuse state (True = blown/tripped at some point)
            - enable_cbfuse: Whether fuse is enabled
            - interpretation: Human-readable status interpretation
            - recommendation: Actionable recommendation (if applicable)
            - failure_count: Current failure count
            - threshold: Failure threshold

    Example:
        >>> status = breaker.get_status()
        >>> formatted = format_cbfuse_status(status)
        >>> print(formatted['interpretation'])
        'TRIPPED at some point - investigate root cause'
        >>> print(formatted['recommendation'])
        'Investigate what trips observability breaker'
    """
    name = breaker.get("name", "unknown")
    cbfuse = breaker.get("cbfuse", False)
    enable_cbfuse = breaker.get("enable_cbfuse", True)
    healthy = breaker.get("healthy", True)
    failure_count = breaker.get("failure_count", 0)
    threshold = breaker.get("threshold", 5)

    # Generate interpretation
    if not enable_cbfuse:
        interpretation = "Expected breaker - no fuse (tripping is normal)"
        recommendation = None
    elif not cbfuse:
        interpretation = "Never tripped (clean history)"
        recommendation = None
    else:
        interpretation = "TRIPPED at some point - investigate root cause"
        if healthy:
            rec_msg = (
                f"{name} has recovered but tripped before - "
                f"investigate root cause"
            )
            recommendation = rec_msg
        else:
            recommendation = f"{name} is currently tripped - investigate and fix"

    return {
        "name": name,
        "healthy": healthy,
        "cbfuse": cbfuse,
        "enable_cbfuse": enable_cbfuse,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "failure_count": failure_count,
        "threshold": threshold,
    }


def get_cbfuse_alerts(correlation_id: str = None) -> list[dict[str, Any]]:
    """Get alerts for blown CBFuses.

    Returns a list of all blown fuses with actionable recommendations.
    Only monitored breakers (enable_cbfuse=True) generate alerts when blown.

    Args:
        correlation_id: Optional correlation ID for tracing

    Returns:
        List of alert dictionaries, each containing:
            - breaker_name: Name of the circuit breaker
            - severity: 'warning' (recovered) or 'critical' (currently tripped)
            - interpretation: Human-readable fuse status
            - recommendation: Actionable recommendation
            - failure_count: Current failure count
            - timestamp: Alert generation time

    Example:
        >>> alerts = get_cbfuse_alerts()
        >>> for alert in alerts:
        ...     print(f"{alert['breaker_name']}: {alert['recommendation']}")
        observability: Investigate observability breaker trip - unexpected failure
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("cba")

    alerts = []

    try:
        # Get circuit breaker manager
        manager = get_circuit_breaker_manager()

        # Get all breakers
        breakers = manager.get_all_breakers(correlation_id=correlation_id)

        # Check each breaker for blown fuses
        for name, breaker in breakers.items():
            if breaker.enable_cbfuse and breaker.cbfuse:
                # This is a monitored breaker with blown fuse
                status = breaker.get_status()
                formatted = format_cbfuse_status(status)

                # Determine severity
                if formatted["healthy"]:
                    severity = "warning"
                else:
                    severity = "critical"

                # Build alert
                alert = {
                    "breaker_name": name,
                    "severity": severity,
                    "interpretation": formatted["interpretation"],
                    "recommendation": formatted["recommendation"],
                    "failure_count": formatted["failure_count"],
                    "threshold": formatted["threshold"],
                    "timestamp": time.time(),
                }

                alerts.append(alert)

        # Log alert count
        if alerts:
            try:

                execute_operation(GatewayInterface.LOGGING, "log_warning",
                message=f"[{correlation_id}] CBFuse alerts generated",
                alert_count=len(alerts),
                breakers=[a["breaker_name"] for a in alerts],
            )

            except (ImportError, AttributeError):
                # Optional dependency - continue if unavailable
                ...

    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ConnectionError, OSError) as e:
        try:

            execute_operation(GatewayInterface.LOGGING, "log_error",
            message=f"[{correlation_id}] Failed to generate CBFuse alerts: {e!s}",
        )

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

    return alerts


def _determine_overall_status(summary: dict[str, Any]) -> str:
    """Determine overall health status from CBFuse summary.

    Args:
        summary: CBFuse summary from manager

    Returns:
        'healthy', 'degraded', 'unhealthy', or 'unknown'
    """
    blown_fuses = summary.get("blown_fuses", 0)
    monitored_breakers = summary.get("monitored_breakers", 0)
    breakers = summary.get("breakers", {})

    # Check for currently tripped breakers
    tripped_breakers = sum(
        1 for b in breakers.values() if not b.get("healthy", True)
    )

    if tripped_breakers > 0:
        # At least one breaker is currently tripped
        return "unhealthy"

    if blown_fuses > 0:
        # All breakers healthy but some have blown fuses (recovered)
        return "degraded"

    if monitored_breakers == 0:
        # No monitored breakers - can't determine health
        return "unknown"

    # All monitored breakers healthy, no blown fuses
    return "healthy"


def _generate_health_interpretation(
    summary: dict[str, Any],
    alerts: list[dict[str, Any]]
) -> str:
    """Generate human-readable health interpretation.

    Args:
        summary: CBFuse summary from manager
        alerts: List of blown fuse alerts

    Returns:
        Human-readable interpretation string
    """
    blown_fuses = summary.get("blown_fuses", 0)
    total_breakers = summary.get("total_breakers", 0)
    monitored_breakers = summary.get("monitored_breakers", 0)

    if total_breakers == 0:
        return "No circuit breakers registered - CBFuse monitoring not active"

    if monitored_breakers == 0:
        msg = (
            f"All {total_breakers} breakers are expected (no fuses) - "
            f"normal operation"
        )
        return msg

    if blown_fuses == 0:
        msg = (
            f"All {monitored_breakers} monitored breakers have clean history - "
            f"no trips detected"
        )
        return msg

    # Calculate recovered vs currently tripped (single pass optimization)
    critical_count = 0
    warning_count = 0
    for a in alerts:
        severity = a.get("severity", "")
        if severity == "critical":
            critical_count += 1
        elif severity == "warning":
            warning_count += 1

    if critical_count > 0:
        msg = (
            f"{critical_count} breaker(s) currently tripped, "
            f"{warning_count} recovered - immediate action needed"
        )
        return msg

    msg = (
        f"{warning_count} monitored breaker(s) have tripped and recovered - "
        f"investigate root causes"
    )
    return msg


__all__ = [
    "get_cbfuse_health_report",
    "format_cbfuse_status",
    "get_cbfuse_alerts",
]
