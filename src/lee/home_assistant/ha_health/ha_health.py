# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


# ha_health.py
"""ha_health.py - Health Check and Monitoring
Version: 1.0.0
Date: 2025-11-05
Purpose: Health checks for Home Assistant integration

Architecture:
Provides health check endpoints for monitoring and diagnostics.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from typing import Any


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


# SUGA-ISP compliant imports - only core gateway functions
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import HA modules
from lee.home_assistant import ha_interconnect

# Rate limiting stats now implemented


def check_ha_connectivity(_timeout: int = 5) -> dict[str, Any]:
    """Check Home Assistant connectivity.

    Tests basic connectivity to HA API.

    Args:
        _timeout: Connection timeout in seconds (unused)

    Returns:
        Health check result with status and details

    """
    correlation_id = generate_correlation_id("ha")

    try:
        # Try to get HA config (tests config loading and caching)
        result = ha_interconnect.config_get_ha_config()

        if result.get("success"):
            config = result.get("data", {})

            return {
                "status": "healthy" if config.get("enabled") else "disabled",
                "enabled": config.get("enabled", False),
                "has_url": bool(config.get("base_url")),
                "has_token": bool(config.get("access_token")),
                "timestamp": time.time(),
            }
        return {
            "status": "unhealthy",
            "error": result.get("error", "Unknown error"),
            "timestamp": time.time(),
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Network error in health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Network error in health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except (ValueError, TypeError, KeyError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Data error in health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Data error in health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Health check failed: {e!s}")

        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }


def check_circuit_breaker_health() -> dict[str, Any]:
    """Check circuit breaker status.

    Returns circuit breaker state and statistics.

    Returns:
        Circuit breaker health information

    """
    try:
        # Get circuit breaker stats for HA
        stats = execute_operation(GatewayInterface.CIRCUIT_BREAKER, "get_stats",
                                name="home_assistant")

        if not stats:
            return {
                "status": "unknown",
                "message": "Circuit breaker stats not available",
            }

        state = stats.get("state", "unknown")

        return {
            "status": "healthy" if state == "closed" else "degraded",
            "state": state,
            "failure_count": stats.get("failure_count", 0),
            "success_count": stats.get("success_count", 0),
            "last_failure": stats.get("last_failure_time"),
            "timestamp": time.time(),
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Network error in circuit breaker health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Network error in circuit breaker health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except (ValueError, TypeError, KeyError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Data error in circuit breaker health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Data error in circuit breaker health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Circuit breaker health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Circuit breaker health check failed: {e!s}")

        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }


def check_logging_fuse_health() -> dict[str, Any]:
    """Check LoggingFuse status.

    Returns health information for all LoggingFuse instances.
    Provides visibility into logging system degradation.

    Returns:
        LoggingFuse health information with status and details

    """
    correlation_id = generate_correlation_id("lfh")

    try:
        from lee.circuit_breaker import get_logging_fuse_health  # pylint: disable=import-outside-toplevel

        health_report = get_logging_fuse_health(correlation_id=correlation_id)

        if health_report.get("success"):
            return {
                "status": "healthy" if health_report.get("blown_fuses", 0) == 0 else "degraded",
                "total_fuses": health_report.get("total_fuses", 0),
                "blown_fuses": health_report.get("blown_fuses", 0),
                "fuses": health_report.get("fuses", {}),
                "interpretation": health_report.get("interpretation", ""),
                "timestamp": time.time(),
            }

        return {
            "status": "unknown",
            "error": health_report.get("error", "Unknown error"),
            "timestamp": time.time(),
        }

    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] LoggingFuse health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] LoggingFuse health check failed: {e!s}")

        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }


def check_rate_limiter_health() -> dict[str, Any]:
    """Check rate limiter status.

    Returns rate limiter statistics and health.

    Returns:
        Rate limiter health information

    """
    try:
        from lee.home_assistant.ha_devices.ha_devices_helpers import (  # pylint: disable=import-outside-toplevel
            get_rate_limit_stats,
        )

        stats = get_rate_limit_stats()

        if not stats.get("success"):
            return {
                "status": "error",
                "error": stats.get("error"),
                "timestamp": time.time(),
            }

        # Determine health based on error rate and call volume
        error_rate = stats.get("error_rate", 0)

        if error_rate > 10:
            status = "unhealthy"
        elif error_rate > 5:
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "stats": stats,
            "timestamp": time.time(),
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Network error in rate limiter health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Network error in rate limiter health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except (ValueError, TypeError, KeyError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Data error in rate limiter health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Data error in rate limiter health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }
    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Rate limiter health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Rate limiter health check failed: {e!s}")

        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
        }


def check_cache_health() -> dict[str, Any]:
    """Check cache system health.

    Tests cache connectivity and basic operations.

    Returns:
        Cache health information

    """
    correlation_id = generate_correlation_id("ha")

    try:
        # Test cache read
        test_key = f"health_check_{correlation_id}"

        # Try to get (should be None)
        _ = execute_operation(GatewayInterface.CACHE, "get", key=test_key)  # Verify cache is operational

        return {
            "status": "healthy",
            "operational": True,
            "timestamp": time.time(),
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Network error in cache health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Network error in cache health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "operational": False,
            "timestamp": time.time(),
        }
    except (ValueError, TypeError, KeyError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Data error in cache health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Data error in cache health check: {e!s}")
        return {
            "status": "error",
            "error": str(e),
            "operational": False,
            "timestamp": time.time(),
        }
    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Cache health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"Cache health check failed: {e!s}")

        return {
            "status": "error",
            "error": str(e),
            "operational": False,
            "timestamp": time.time(),
        }


def get_overall_health(include_details: bool = True) -> dict[str, Any]:  # pylint: disable=R0912
    """Get overall system health.

    Aggregates health checks from all components.

    Args:
        include_details: Include detailed health info for each component

    Returns:
        Overall health status with component details

    """
    correlation_id = generate_correlation_id("ha")

    try:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_debug",
                           message=f"[{correlation_id}] Running overall health check")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Running overall health check")

        # Run all health checks
        ha_health = check_ha_connectivity()
        cb_health = check_circuit_breaker_health()
        rl_health = check_rate_limiter_health()
        cache_health = check_cache_health()
        lf_health = check_logging_fuse_health()

        # Determine overall status
        statuses = [
            ha_health.get("status"),
            cb_health.get("status"),
            rl_health.get("status"),
            cache_health.get("status"),
            lf_health.get("status"),
        ]

        # Overall health logic:
        # - healthy: all components healthy
        # - degraded: some components degraded but functional
        # - unhealthy: critical component unhealthy
        # - error: any component in error state

        if "error" in statuses:
            overall_status = "error"
        elif "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses or "throttled" in statuses:
            overall_status = "degraded"
        elif all(s in ["healthy", "disabled"] for s in statuses):
            overall_status = "healthy"
        else:
            overall_status = "unknown"

        result = {
            "success": True,
            "message": "Health check complete",
            "data": {
                "status": overall_status,
                "timestamp": time.time(),
            },
        }

        if include_details:
            result["data"]["components"] = {
                "home_assistant": ha_health,
                "circuit_breaker": cb_health,
                "rate_limiter": rl_health,
                "cache": cache_health,
                "logging_fuse": lf_health,
            }

        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                           message=f"[{correlation_id}] Health check complete: {overall_status}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Health check complete: {overall_status}")

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Network error in overall health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Network error in overall health check: {e!s}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "HEALTH_CHECK_FAILED",
            "data": {
                "timestamp": time.time(),
            },
        }
    except (ValueError, TypeError, KeyError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Data error in overall health check: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Data error in overall health check: {e!s}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "HEALTH_CHECK_FAILED",
            "data": {
                "timestamp": time.time(),
            },
        }
    except RuntimeError as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Overall health check failed: {e!s}")
        except (ImportError, RuntimeError):
            if _is_debug_mode():
                print(f"[{correlation_id}] Overall health check failed: {e!s}")

        return {
            "success": False,
            "error": str(e),
            "error_code": "HEALTH_CHECK_FAILED",
            "data": {
                "timestamp": time.time(),
            },
        }


def get_health_summary() -> dict[str, Any]:
    """Get brief health summary.

    Quick health check without detailed component info.

    Returns:
        Brief health summary

    """
    result = get_overall_health(include_details=False)

    if result.get("success"):
        data = result.get("data", {})
        return {
            "healthy": data.get("status") == "healthy",
            "status": data.get("status"),
            "timestamp": data.get("timestamp"),
        }

    return {
        "healthy": False,
        "status": "error",
        "error": result.get("error"),
        "timestamp": time.time(),
    }


__all__ = [
    "check_cache_health",
    "check_circuit_breaker_health",
    "check_ha_connectivity",
    "check_logging_fuse_health",
    "check_rate_limiter_health",
    "get_health_summary",
    "get_overall_health",
]

# EOF
