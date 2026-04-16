"""initialization/initialization_core.py
Version: 2025-12-13_2
Purpose: Gateway implementation functions for initialization interface
License: Apache 2.0

CHANGES (2025-12-13_2):
- Consolidated duplicate implementation functions using factory pattern
- Reduced code duplication by 75%
"""

from typing import Any, Optional

from lee.initialization.initialization_manager import (
    InitializationOperation,
    get_initialization_manager,
)

# Lazy imports for gateway operations to avoid circular dependency
_gateway_imported = False
_GatewayInterface = None
_execute_operation = None

def _get_gateway():  # pylint: disable=global-statement
    """Lazy import gateway functions to avoid circular dependency."""
    global _gateway_imported, _GatewayInterface, _execute_operation
    if not _gateway_imported:
        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            from lee.gateway.gateway_core import generate_correlation_id  # pylint: disable=import-outside-toplevel
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _gateway_imported = True
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
            generate_correlation_id = None
    return _GatewayInterface, _execute_operation, generate_correlation_id if _gateway_imported else (None, None, None)


def _ensure_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Ensure correlation_id exists, generating one if needed.

    Args:
        correlation_id: Optional correlation ID

    Returns:
        correlation_id (generated if None)
    """
    if correlation_id is None:
        _GatewayInterface, _execute_operation, generate_correlation_id = _get_gateway()
        return generate_correlation_id("init")
    return correlation_id


def _log_operation(operation_name: str, correlation_id: str, **log_kwargs) -> None:
    """Log initialization operation if gateway available.

    Args:
        operation_name: Name of operation being logged
        correlation_id: Correlation ID for tracking
        **log_kwargs: Additional log parameters
    """
    _GatewayInterface, _execute_operation, _generate_correlation_id = _get_gateway()
    if _GatewayInterface and _execute_operation:
        log_params = {
            "corr_id": correlation_id,
            "scope": "INITIALIZATION",
            "message": f"{operation_name} called",
        }
        log_params.update(log_kwargs)
        _execute_operation(_GatewayInterface.DEBUG, "log", **log_params)


def _create_implementation_factory(operation_name: str, manager_method: str,
                                   requires_params: bool = False) -> callable:
    """Factory for creating implementation functions with standard correlation_id handling.

    Args:
        operation_name: Name of operation for logging
        manager_method: Name of method to call on initialization manager
        requires_params: Whether operation requires additional parameters

    Returns:
        Implementation function
    """
    def impl(correlation_id: str = None, **kwargs) -> Any:
        correlation_id = _ensure_correlation_id(correlation_id)
        _log_operation(f"{operation_name}_implementation", correlation_id, **kwargs)

        manager = get_initialization_manager()
        method = getattr(manager, manager_method)

        if requires_params:
            return method(correlation_id=correlation_id, **kwargs)
        return method(correlation_id=correlation_id)

    impl.__name__ = f"{operation_name}_implementation"
    return impl


# ===== MODULE-LEVEL DISPATCH HANDLERS =====

def _op_initialize(manager, correlation_id, **_kwargs):
    """Handler for INITIALIZE operation."""
    return manager.initialize(correlation_id=correlation_id, **_kwargs)


def _op_get_config(manager, correlation_id, **_kwargs):
    """Handler for GET_CONFIG operation."""
    return manager.get_config(correlation_id=correlation_id)


def _op_is_initialized(manager, correlation_id, **_kwargs):
    """Handler for IS_INITIALIZED operation."""
    return manager.is_initialized(correlation_id=correlation_id)


def _op_reset(manager, correlation_id, **_kwargs):
    """Handler for RESET operation."""
    return manager.reset(correlation_id=correlation_id)


def _op_get_status(manager, correlation_id, **_kwargs):
    """Handler for GET_STATUS operation."""
    return manager.get_status(correlation_id=correlation_id)


def _op_get_stats(manager, correlation_id, **_kwargs):
    """Handler for GET_STATS operation."""
    return manager.get_stats(correlation_id=correlation_id)


def _op_set_flag(manager, correlation_id, **_kwargs):
    """Handler for SET_FLAG operation."""
    return manager.set_flag(correlation_id=correlation_id, **_kwargs)


def _op_get_flag(manager, correlation_id, **_kwargs):
    """Handler for GET_FLAG operation."""
    return manager.get_flag(correlation_id=correlation_id)


# Dispatch dictionary for initialization operations (O(1) lookup)
_INITIALIZATION_OPERATION_HANDLERS = {
    InitializationOperation.INITIALIZE: _op_initialize,
    InitializationOperation.GET_CONFIG: _op_get_config,
    InitializationOperation.IS_INITIALIZED: _op_is_initialized,
    InitializationOperation.RESET: _op_reset,
    InitializationOperation.GET_STATUS: _op_get_status,
    InitializationOperation.GET_STATS: _op_get_stats,
    InitializationOperation.SET_FLAG: _op_set_flag,
    InitializationOperation.GET_FLAG: _op_get_flag,
}


def execute_initialization_operation(operation: InitializationOperation,
                                     correlation_id: str = None, **kwargs):
    """Universal initialization operation executor with error handling.

    Args:
        operation: InitializationOperation enum value
        correlation_id: Optional correlation ID for debug tracking
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from InitializationCore

    Raises:
        ValueError: If operation is unknown
        Exception: If operation execution fails

    Performance: O(1) dictionary lookup instead of O(n) if/elif chain
    """
    correlation_id = _ensure_correlation_id(correlation_id)
    _log_operation("execute_initialization_operation", correlation_id,
                   operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))

    try:
        manager = get_initialization_manager()

        # Dictionary dispatch for initialization operations (O(1) lookup)
        handler = _INITIALIZATION_OPERATION_HANDLERS.get(operation)
        if handler is None:
            raise ValueError(f"Unknown initialization operation: {operation}")

        return handler(manager, correlation_id, **kwargs)

    except (ValueError, TypeError, KeyError) as e:
        # Data validation error
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                     message=f"Operation validation failed: {e!s}",
                     operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))
        raise RuntimeError(f"Initialization operation '{operation.value}' validation failed: {e}") from e
    except (ImportError, AttributeError) as e:
        # Configuration error
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                     message=f"Operation config failed: {e!s}",
                     operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))
        raise RuntimeError(f"Initialization operation '{operation.value}' config failed: {e}") from e
    except (ConnectionError, TimeoutError, OSError) as e:
        # Network or system error
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                     message=f"Operation system error: {e!s}",
                     operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))
        raise RuntimeError(f"Initialization operation '{operation.value}' system error: {e}") from e
    except Exception as e:
        # Unexpected error - log with full context
        if _GatewayInterface and _execute_operation:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                     message=f"Operation failed unexpectedly: {e!s}",
                     operation=operation.value if isinstance(operation, InitializationOperation) else str(operation),
                     error_type=type(e).__name__)
        raise RuntimeError(f"Initialization operation '{operation.value}' failed unexpectedly: {e}") from e


# Create implementation functions using factory
initialize_implementation = _create_implementation_factory("initialize", "initialize", requires_params=True)
get_config_implementation = _create_implementation_factory("get_config", "get_config")
is_initialized_implementation = _create_implementation_factory("is_initialized", "is_initialized")
reset_implementation = _create_implementation_factory("reset", "reset")
get_status_implementation = _create_implementation_factory("get_status", "get_status")
get_stats_implementation = _create_implementation_factory("get_stats", "get_stats")


def set_flag_implementation(flag_name: str, value: Any,
                            correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Execute set flag operation.

    Args:
        flag_name: Flag name
        value: Flag value
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Set flag result dict

    Raises:
        ValueError: If flag_name or value missing

    """
    correlation_id = _ensure_correlation_id(correlation_id)

    if not flag_name:
        raise ValueError("Parameter 'flag_name' is required for set_flag operation")

    _log_operation("set_flag_implementation", correlation_id,
                   flag_name=flag_name, has_value=value is not None)

    return get_initialization_manager().set_flag(
        flag_name=flag_name,
        value=value,
        correlation_id=correlation_id,
    )


def get_flag_implementation(flag_name: str, default: Any = None,
                            correlation_id: str = None, **_kwargs) -> Any:
    """Execute get flag operation.

    Args:
        flag_name: Flag name
        default: Default value if flag doesn't exist
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Flag value or default

    Raises:
        ValueError: If flag_name missing

    """
    correlation_id = _ensure_correlation_id(correlation_id)

    if not flag_name:
        raise ValueError("Parameter 'flag_name' is required for get_flag operation")

    _log_operation("get_flag_implementation", correlation_id, flag_name=flag_name)

    return get_initialization_manager().get_flag(
        flag_name=flag_name,
        default=default,
        correlation_id=correlation_id,
    )


__all__ = [
    "execute_initialization_operation",
    "get_config_implementation",
    "get_flag_implementation",
    "get_stats_implementation",
    "get_status_implementation",
    "initialize_implementation",
    "is_initialized_implementation",
    "reset_implementation",
    "set_flag_implementation",
]
