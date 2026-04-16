"""diagnosis/diagnosis_performance.py
Version: 2025-12-21_1
Purpose: Performance diagnosis for gateway components
License: Apache 2.0
"""

import gc
import random
import time
from contextlib import nullcontext
from typing import Any

from lee.gateway import GatewayInterface, execute_operation


def diagnose_system_health(**_kwargs) -> dict[str, Any]:
    """Comprehensive system health diagnosis."""
    # Generate correlation ID inline (SUGA-ISP compliant)
    # Correlation ID - non-security-critical, use fast random
    corr_id = f"perf_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Starting comprehensive system health diagnosis")
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=corr_id, scope="DIAGNOSIS")
    except ImportError:
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.diagnosis.health.diagnosis_health_checks import (  # pylint: disable=import-outside-toplevel
                check_component_health,
                check_gateway_health,
            )

            component_health = check_component_health()
            gateway_health = check_gateway_health()
            memory_info = diagnose_memory_usage()

            result = {
                "success": True,
                "component_health": component_health,
                "gateway_health": gateway_health,
                "memory": memory_info,
            }

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="System health diagnosis completed",
                                 component_healthy=component_health.get("success", False),
                                 gateway_healthy=gateway_health.get("success", False))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return result
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, ConnectionError, TimeoutError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="System health diagnosis failed",
                                 error=str(e))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {
                "success": False,
                "error": str(e),
            }


def diagnose_utility_performance(**_kwargs) -> dict[str, Any]:
    """Comprehensive system health diagnosis."""
    # Generate correlation ID inline (SUGA-ISP compliant)
    corr_id = f"perf_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Starting comprehensive system health diagnosis")
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=corr_id, scope="DIAGNOSIS")
    except ImportError:
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.diagnosis.health.diagnosis_health_checks import (  # pylint: disable=import-outside-toplevel
                check_component_health,
                check_gateway_health,
            )

            component_health = check_component_health()
            gateway_health = check_gateway_health()
            memory_info = diagnose_memory_usage()

            result = {
                "success": True,
                "component_health": component_health,
                "gateway_health": gateway_health,
                "memory": memory_info,
            }

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="System health diagnosis completed",
                                 component_healthy=component_health.get("success", False),
                                 gateway_healthy=gateway_health.get("success", False))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return result
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, ConnectionError, TimeoutError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="System health diagnosis failed",
                                 error=str(e))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {
                "success": False,
                "error": str(e),
            }


def diagnose_component_performance(component: str = None, **_kwargs) -> dict[str, Any]:
    """Performance diagnosis for gateway or specific component."""
    # Generate correlation ID inline (SUGA-ISP compliant)
    corr_id = f"perf_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"
    component_name = component or "gateway"

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Diagnosing component performance", component=component_name)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=corr_id, scope="DIAGNOSIS")
    except ImportError:
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.gateway import get_gateway_stats  # pylint: disable=import-outside-toplevel
            gateway_stats = get_gateway_stats()

            result = {
                "success": True,
                "component": component_name,
                "gateway_operations": gateway_stats.get("total_interfaces", 0),
                "fast_path_enabled": gateway_stats.get("fast_path_enabled", False),
                "call_counts": gateway_stats.get("operation_counts", {}),
            }

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="Component performance diagnosis completed",
                                 component=component_name, operations=result["gateway_operations"])
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return result
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, ConnectionError, TimeoutError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="DIAGNOSIS",
                                 message="Component performance diagnosis failed",
                                 component=component_name, error=str(e))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {
                "success": False,
                "component": component_name,
                "error": str(e),
            }


def diagnose_memory_usage(**_kwargs) -> dict[str, Any]:
    """Memory usage diagnosis."""
    # Generate correlation ID inline (SUGA-ISP compliant)
    corr_id = f"perf_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Starting memory usage diagnosis")
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=corr_id, scope="DIAGNOSIS")
    except ImportError:
        timing_ctx = nullcontext()

    with timing_ctx:
        gc_stats = getattr(gc, "get_stats", None)
        _ = gc_stats() if gc_stats is not None else []  # Stats collected implicitly
        objects_count = len(gc.get_objects())
        garbage_count = len(gc.garbage)
        collections_count = gc.get_count()

        result = {
            "success": True,
            "objects": objects_count,
            "garbage": garbage_count,
            "collections": collections_count,
        }

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=corr_id, scope="DIAGNOSIS",
                             message="Memory usage diagnosis completed",
                             objects=objects_count, garbage=garbage_count)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        return result


def diagnose_initialization_performance(**kwargs) -> dict[str, Any]:
    """Backward compatibility wrapper - use TEST interface instead."""
    return execute_operation(GatewayInterface.TEST, "test_initialization_performance", **kwargs)


def diagnose_utility_performance_legacy(**kwargs) -> dict[str, Any]:
    """Backward compatibility wrapper - use TEST interface instead."""
    return execute_operation(GatewayInterface.TEST, "test_utility_performance", **kwargs)


def diagnose_singleton_performance(**kwargs) -> dict[str, Any]:
    """Backward compatibility wrapper - use TEST interface instead."""
    return execute_operation(GatewayInterface.TEST, "test_singleton_performance", **kwargs)


__all__ = [
    "diagnose_component_performance",
    "diagnose_initialization_performance",
    "diagnose_memory_usage",
    "diagnose_singleton_performance",
    "diagnose_system_health",
    "diagnose_utility_performance",
    "diagnose_utility_performance_legacy",
]
