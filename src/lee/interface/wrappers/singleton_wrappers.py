"""singleton_wrappers.py - INTERNAL Singleton Interface Wrappers
Version: 2026-04-04_1 (Refactored with function factory)
Description: Internal wrapper functions for SINGLETON interface (SUGA-ISP compliant)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions.
External modules MUST use gateway.execute_operation() instead of importing directly.
These wrappers are owned by the interface and should not be imported outside the interface.

SUGA-ISP Pattern:
- External modules: gateway.execute_operation(GatewayInterface.SINGLETON, 'get', ...)
- Interface uses these internal wrappers for implementation
- Core receives calls from interface wrappers only

REFACTORING: Function factory pattern eliminates ~1000 lines of duplicate code
"""

# ===== SUGA-ISP COMPLIANT - NO INTERNAL HELPERS =====
# All debug operations route through Gateway (ISP) - NO internal helpers allowed

import random
import time
from typing import Any, Optional
from collections.abc import Callable

import importlib

from lee.gateway import GatewayInterface, execute_operation

# ===== FUNCTION FACTORY =====


def _create_singleton_wrapper(
    operation_name: str,
    module_name: str,
    core_function: str,
    log_params: Optional[list[str]] = None,
    use_singleton_core: bool = False
) -> Callable:
    """Create a singleton wrapper function with standard logging and error handling.

    Args:
        operation_name: Name of the operation (e.g., 'singleton_get')
        module_name: Module to import from (e.g., 'singleton_generic')
        core_function: Function to call in core module
        log_params: Parameter names to log (e.g., ['name', 'instance'])
        use_singleton_core: If True, use SingletonCore() instead of direct import

    Returns:
        Wrapper function with standard logging and error handling
    """
    def wrapper(correlation_id: str = None, **kwargs) -> Any:
        if correlation_id is None:
            correlation_id = f"int_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

        log_args = {"corr_id": correlation_id, "scope": "INTERFACE", "message": f"{operation_name} called"}
        if log_params:
            for param in log_params:
                if param in kwargs:
                    if param == "instance" and "instance" in kwargs:
                        log_args["instance_type"] = type(kwargs["instance"]).__name__
                    else:
                        log_args[param] = kwargs[param]

        execute_operation(GatewayInterface.DEBUG, "log", **log_args)

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name=operation_name) as _:
            try:
                if use_singleton_core:
                    from lee.singleton import SingletonCore  # pylint: disable=import-outside-toplevel
                    manager = SingletonCore()
                    core_func = getattr(manager, core_function)
                    result = core_func(correlation_id=correlation_id, **kwargs)
                else:
                    # Dynamic import from lee.singleton module
                    core_module_import = importlib.import_module(f"lee.singleton.{module_name}", "lee.singleton")
                    core_func = getattr(core_module_import, core_function)
                    result = core_func(correlation_id=correlation_id, **kwargs)

                execute_operation(GatewayInterface.DEBUG, "log",
                                  corr_id=correlation_id, scope="INTERFACE",
                                  message=f"{operation_name} completed", success=True)
                return result
            except (AttributeError, KeyError, RuntimeError, ValueError, TypeError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                  corr_id=correlation_id, scope="INTERFACE",
                                  message=f"{operation_name} operation error",
                                  error_type=type(e).__name__, error=str(e))
                raise

    wrapper.__name__ = operation_name
    wrapper.__doc__ = f"{operation_name} wrapper function"
    return wrapper


# ===== SINGLETON OPERATIONS =====

singleton_get = _create_singleton_wrapper(
    operation_name="singleton_get",
    module_name="singleton_generic",
    core_function="get_implementation",
    log_params=["name"]
)

singleton_set = _create_singleton_wrapper(
    operation_name="singleton_set",
    module_name="singleton_generic",
    core_function="set_implementation",
    log_params=["name", "instance"]
)

singleton_has = _create_singleton_wrapper(
    operation_name="singleton_has",
    module_name="singleton_generic",
    core_function="has_implementation",
    log_params=["name"]
)

singleton_delete = _create_singleton_wrapper(
    operation_name="singleton_delete",
    module_name="singleton_generic",
    core_function="delete_implementation",
    log_params=["name"]
)

singleton_clear = _create_singleton_wrapper(
    operation_name="singleton_clear",
    module_name="singleton_generic",
    core_function="clear_implementation"
)

singleton_stats = _create_singleton_wrapper(
    operation_name="singleton_stats",
    module_name="singleton_generic",
    core_function="get_stats",
    use_singleton_core=True
)

singleton_get_stats = _create_singleton_wrapper(
    operation_name="singleton_get_stats",
    module_name="singleton_generic",
    core_function="get_stats_implementation"
)

singleton_reset = _create_singleton_wrapper(
    operation_name="singleton_reset",
    module_name="singleton_generic",
    core_function="reset_implementation"
)


# ===== ALIAS FUNCTIONS =====

def singleton_register(name: str, instance: Any, correlation_id: str = None) -> None:
    """Register singleton instance (alias for singleton_set).

    This function provides semantic naming for singleton registration
    while maintaining compatibility with code that imports singleton_register.

    Args:
        name: Singleton name
        instance: Instance to register
        correlation_id: Optional correlation ID for tracking
    """
    singleton_set(name=name, instance=instance, correlation_id=correlation_id)


# ===== MEMORY MONITORING OPERATIONS =====

get_memory_stats = _create_singleton_wrapper(
    operation_name="get_memory_stats",
    module_name="singleton_generic",
    core_function="get_memory_stats"
)

get_comprehensive_memory_stats = _create_singleton_wrapper(
    operation_name="get_comprehensive_memory_stats",
    module_name="singleton_generic",
    core_function="get_comprehensive_memory_stats"
)

check_lambda_memory_compliance = _create_singleton_wrapper(
    operation_name="check_lambda_memory_compliance",
    module_name="singleton_generic",
    core_function="check_lambda_memory_compliance"
)


# ===== LIFECYCLE OPERATIONS =====

initialize_singleton = _create_singleton_wrapper(
    operation_name="initialize_singleton",
    module_name="singleton_generic",
    core_function="initialize_implementation"
)

shutdown_singleton = _create_singleton_wrapper(
    operation_name="shutdown_singleton",
    module_name="singleton_generic",
    core_function="shutdown_implementation"
)


# ===== HEALTH CHECK OPERATIONS =====

health_check_singleton = _create_singleton_wrapper(
    operation_name="health_check_singleton",
    module_name="singleton_generic",
    core_function="health_check_implementation"
)


# ===== CONFIGURATION OPERATIONS =====

configure_singleton = _create_singleton_wrapper(
    operation_name="configure_singleton",
    module_name="singleton_generic",
    core_function="configure_implementation",
    log_params=["config"]
)

get_singleton_config = _create_singleton_wrapper(
    operation_name="get_singleton_config",
    module_name="singleton_generic",
    core_function="get_config_implementation"
)


# ===== THREAD SAFETY OPERATIONS =====

lock_singleton = _create_singleton_wrapper(
    operation_name="lock_singleton",
    module_name="singleton_generic",
    core_function="lock_implementation",
    log_params=["name"]
)

unlock_singleton = _create_singleton_wrapper(
    operation_name="unlock_singleton",
    module_name="singleton_generic",
    core_function="unlock_implementation",
    log_params=["name"]
)


# ===== DIAGNOSTIC OPERATIONS =====

get_singleton_diagnostics = _create_singleton_wrapper(
    operation_name="get_singleton_diagnostics",
    module_name="singleton_generic",
    core_function="get_diagnostics_implementation"
)

validate_singleton_state = _create_singleton_wrapper(
    operation_name="validate_singleton_state",
    module_name="singleton_generic",
    core_function="validate_state_implementation"
)
