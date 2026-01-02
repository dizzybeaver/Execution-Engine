"""
gateway_core.py - Core Gateway Implementation (SUGA-ISP)
Version: 2025-12-13_1
Description: Pattern-based registry with simplified routing

CHANGES (2025-12-13_1):
- FIXED: Import paths for interface modules (now in interface/ directory)
- Interface modules are interface.interface_xxx not interface_xxx

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional, Tuple, Callable
from collections import defaultdict

# FIXED: Import enum from separate file to prevent circular imports
from gateway_enums import GatewayInterface


# ===== PATTERN-BASED REGISTRY =====

_INTERFACE_ROUTERS: Dict[GatewayInterface, Tuple[str, str]] = {
    GatewayInterface.CACHE: ('interface.interface_cache', 'execute_cache_operation'),
    GatewayInterface.LOGGING: ('interface.interface_logging', 'execute_logging_operation'),
    GatewayInterface.SECURITY: ('interface.interface_security', 'execute_security_operation'),
    GatewayInterface.METRICS: ('interface.interface_metrics', 'execute_metrics_operation'),
    GatewayInterface.CONFIG: ('interface.interface_config', 'execute_config_operation'),
    GatewayInterface.SINGLETON: ('interface.interface_singleton', 'execute_singleton_operation'),
    GatewayInterface.INITIALIZATION: ('interface.interface_initialization', 'execute_initialization_operation'),
    GatewayInterface.HTTP_CLIENT: ('interface.interface_http', 'execute_http_operation'),
    GatewayInterface.WEBSOCKET: ('interface.interface_websocket', 'execute_websocket_operation'),
    GatewayInterface.CIRCUIT_BREAKER: ('interface.interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    GatewayInterface.UTILITY: ('interface.interface_utility', 'execute_utility_operation'),
    GatewayInterface.DEBUG: ('interface.interface_debug', 'execute_debug_operation'),
    GatewayInterface.DIAGNOSIS: ('interface.interface_diagnosis', 'execute_diagnosis_operation'),
    GatewayInterface.TEST: ('interface.interface_test', 'execute_test_operation'),
}

# Legacy alias for backwards compatibility
_OPERATION_REGISTRY = _INTERFACE_ROUTERS


# ===== FAST PATH CACHE =====

_fast_path_cache: Dict[Tuple[GatewayInterface, str], Tuple[Callable, str, str]] = {}
_fast_path_enabled = True
_operation_call_counts = defaultdict(int)


# ===== CORE EXECUTION ENGINE =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Execute operation through pattern-based routing.

    PATTERN-BASED ROUTING (v2025.10.17.18):
    All operations for an interface route to the same function.
    The interface's dispatch dictionary handles operation routing.

    Benefits:
    - Simpler registry (14 entries vs 100+)
    - Easier maintenance (add operation = 1 place)
    - Leverages interface dispatch dictionaries
    - Zero breaking changes

    Args:
        interface: The GatewayInterface to route through
        operation: The operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from interface implementation

    Raises:
        ValueError: If interface unknown
        RuntimeError: If module/function loading fails or execution fails
    """
    import importlib

    # NEW: Comprehensive debug tracing for exact failure point identification
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        from debug import generate_correlation_id
        correlation_id = generate_correlation_id()

    # Update kwargs with correlation_id for downstream functions
    kwargs['correlation_id'] = correlation_id

    from debug import debug_log, debug_timing

    debug_log(correlation_id, "GATEWAY", "execute_operation called",
              interface=str(interface), operation=operation,
              param_keys=list(kwargs.keys()), param_count=len(kwargs))

    with debug_timing(correlation_id, "GATEWAY", "execute_operation",
                     interface=str(interface), operation=operation):
        try:
            # Increment call count for fast path decision
            _operation_call_counts[(interface, operation)] += 1

            # Try fast path first if enabled
            if _fast_path_enabled:
                cache_key = (interface, operation)
                if cache_key in _fast_path_cache:
                    debug_log(correlation_id, "GATEWAY", "Using fast path cache",
                              interface=str(interface), operation=operation)
                    func, module_name, func_name = _fast_path_cache[cache_key]

                    try:
                        # Interface routers always need operation parameter
                        result = func(operation, **kwargs)
                        debug_log(correlation_id, "GATEWAY", "Fast path execution completed",
                                  interface=str(interface), operation=operation, success=True)
                        return result
                    except Exception as e:
                        debug_log(correlation_id, "GATEWAY", "Fast path execution failed",
                                  interface=str(interface), operation=operation,
                                  error_type=type(e).__name__, error=str(e))
                        raise RuntimeError(
                            f"Failed to execute {interface.value}.{operation}: {str(e)}"
                        ) from e

            debug_log(correlation_id, "GATEWAY", "Using slow path routing",
                      interface=str(interface), operation=operation)

            # Slow path: Pattern-based routing
            if interface not in _INTERFACE_ROUTERS:
                error_msg = f"Unknown interface: {interface.value}"
                debug_log(correlation_id, "GATEWAY", "Unknown interface error",
                          interface=str(interface), interface_value=interface.value)
                raise ValueError(error_msg)

            module_name, func_name = _INTERFACE_ROUTERS[interface]

            # Lazy import with error handling
            try:
                debug_log(correlation_id, "GATEWAY", "Importing module",
                          module_name=module_name, interface=str(interface))
                module = importlib.import_module(module_name)
            except ImportError as e:
                error_msg = f"Failed to import module '{module_name}' for {interface.value}: {str(e)}"
                debug_log(correlation_id, "GATEWAY", "Module import failed",
                          module_name=module_name, interface=str(interface),
                          error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

            try:
                debug_log(correlation_id, "GATEWAY", "Getting function",
                          func_name=func_name, module_name=module_name)
                func = getattr(module, func_name)
            except AttributeError as e:
                error_msg = f"Function '{func_name}' not found in module '{module_name}' for {interface.value}: {str(e)}"
                debug_log(correlation_id, "GATEWAY", "Function not found",
                          func_name=func_name, module_name=module_name,
                          error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

            # Cache for fast path if operation is frequent
            if _fast_path_enabled and _operation_call_counts[(interface, operation)] >= 3:
                _fast_path_cache[(interface, operation)] = (func, module_name, func_name)
                debug_log(correlation_id, "GATEWAY", "Added to fast path cache",
                          interface=str(interface), operation=operation,
                          call_count=_operation_call_counts[(interface, operation)])

            # Execute operation (interface routers always need operation parameter)
            debug_log(correlation_id, "GATEWAY", "Executing interface function",
                      func_name=func_name, interface=str(interface), operation=operation)
            try:
                result = func(operation, **kwargs)
                debug_log(correlation_id, "GATEWAY", "execute_operation completed",
                          interface=str(interface), operation=operation, success=True)
                return result
            except Exception as e:
                error_msg = f"Failed to execute {interface.value}.{operation}: {str(e)}"
                debug_log(correlation_id, "GATEWAY", "Interface function execution failed",
                          interface=str(interface), operation=operation, func_name=func_name,
                          error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

        except Exception as e:
            # Catch any unexpected errors and ensure they're logged
            debug_log(correlation_id, "GATEWAY", "execute_operation unexpected error",
                      interface=str(interface), operation=operation,
                      error_type=type(e).__name__, error=str(e))
            raise


# ===== INITIALIZATION =====

def initialize_lambda() -> Dict[str, Any]:
    """Initialize Lambda execution environment."""
    return {
        'gateway_initialized': True,
        'fast_path_enabled': _fast_path_enabled,
        'interface_count': len(_INTERFACE_ROUTERS)
    }


# ===== STATISTICS =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        'total_interfaces': len(_INTERFACE_ROUTERS),
        'fast_path_entries': len(_fast_path_cache),
        'fast_path_enabled': _fast_path_enabled,
        'operation_counts': dict(_operation_call_counts)
    }


def reset_gateway_state() -> Dict[str, Any]:
    """
    Reset gateway state including fast path cache and operation counts.
    
    Returns:
        Dict containing counts of cleared items
    """
    global _fast_path_cache, _operation_call_counts
    
    fast_path_count = len(_fast_path_cache)
    operation_count = len(_operation_call_counts)
    
    _fast_path_cache.clear()
    _operation_call_counts.clear()
    
    return {
        'fast_path_entries_cleared': fast_path_count,
        'operation_counts_cleared': operation_count,
        'state_reset': True
    }


# ===== FAST PATH MANAGEMENT =====

def set_fast_path_threshold(threshold: int) -> None:
    """Set fast path activation threshold (for future use)."""
    pass


def enable_fast_path() -> None:
    """Enable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = True


def disable_fast_path() -> None:
    """Disable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = False


def clear_fast_path_cache() -> int:
    """Clear fast path cache and return number of entries cleared."""
    global _fast_path_cache
    count = len(_fast_path_cache)
    _fast_path_cache.clear()
    return count


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return {
        'enabled': _fast_path_enabled,
        'cache_size': len(_fast_path_cache),
        'cached_operations': list(_fast_path_cache.keys())
    }


# ===== RESPONSE HELPERS =====

def create_error_response(error: str, error_code: str, details: Any = None) -> Dict[str, Any]:
    """Create standardized error response for INTERNAL use."""
    return {
        'success': False,
        'error': error,
        'error_code': error_code,
        'details': details
    }

def create_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """Create standardized success response for INTERNAL use."""
    return {
        'success': True,
        'message': message,
        'data': data
    }


# ===== EXPORTS =====

__all__ = [
    'GatewayInterface',  # Re-exported from gateway_enums
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    'reset_gateway_state',
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    'create_error_response',
    'create_success_response',
    '_OPERATION_REGISTRY',  # Legacy alias
    '_INTERFACE_ROUTERS',
]

# EOF
