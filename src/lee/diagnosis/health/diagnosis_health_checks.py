"""diagnosis/health/diagnosis_health_checks.py
Version: 2025-12-08_1
Purpose: Basic component and gateway health checks
License: Apache 2.0
"""

from typing import Any


def check_component_health(**_kwargs) -> dict[str, Any]:
    """Check component health."""
    try:
        from lee.gateway import check_all_components  # pylint: disable=import-outside-toplevel
        return check_all_components()
    except ImportError:
        return {"success": False, "error": "Gateway not available"}


def check_gateway_health(**_kwargs) -> dict[str, Any]:
    """Check gateway health."""
    try:
        from lee.gateway import get_gateway_stats  # pylint: disable=import-outside-toplevel
        stats = get_gateway_stats()
        return {
            "success": True,
            "healthy": stats.get("operations_count", 0) > 0,
        }
    except ImportError:
        return {"success": False, "error": "Gateway not available"}


def generate_health_report(**_kwargs) -> dict[str, Any]:
    """Generate comprehensive health report."""
    try:
        from debug_stats import (  # pylint: disable=import-outside-toplevel
            get_dispatcher_stats,
            get_optimization_stats,
            get_system_stats,
        )
        from debug_verification import verify_registry_operations  # pylint: disable=import-outside-toplevel
        from lee.diagnosis.diagnosis_core import (  # pylint: disable=import-outside-toplevel
            validate_gateway_routing,
            validate_imports,
            validate_system_architecture,
        )
        from lee.diagnosis.diagnosis_performance import diagnose_system_health  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        return {
            "success": False,
            "error": f"Required modules not available: {e}",
        }

    try:
        dispatcher_stats = get_dispatcher_stats()
    except (ImportError, AttributeError, RuntimeError, KeyError):
        dispatcher_stats = {"error": "dispatcher stats not available"}

    return {
        "timestamp": "2025-12-08",
        "system_health": diagnose_system_health(),
        "validation": {
            "architecture": validate_system_architecture(),
            "imports": validate_imports(),
            "gateway_routing": validate_gateway_routing(),
            "registry_operations": verify_registry_operations(),
        },
        "stats": get_system_stats(),
        "optimization": get_optimization_stats(),
        "dispatcher_performance": dispatcher_stats,
    }


__all__ = [
    "check_component_health",
    "check_gateway_health",
    "generate_health_report",
]
