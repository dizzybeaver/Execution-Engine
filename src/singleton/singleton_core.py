"""
singleton/singleton_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for singleton interface
License: Apache 2.0
"""

from typing import Any, Dict, Callable, Optional

from singleton.singleton_manager import (
    SingletonOperation,
    get_singleton_manager
)


def execute_singleton_operation(operation: SingletonOperation,
                                correlation_id: str = None, **kwargs):
    """
    Universal singleton operation executor with error handling.

    Args:
        operation: SingletonOperation enum value
        correlation_id: Optional correlation ID for debug tracking
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation is invalid
        Exception: If operation execution fails
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    from debug import debug_timing

    if correlation_id is None:
        correlation_id = generate_correlation_id()

    if not isinstance(operation, SingletonOperation):
        raise ValueError(f"Invalid operation type: {type(operation)}")

    debug_log(correlation_id, "SINGLETON",
             "execute_singleton_operation called",
             operation=operation.value)

    with debug_timing(correlation_id, "SINGLETON", "execute_singleton_operation",
                     operation=operation.value):
        try:
            manager = get_singleton_manager()

            if operation == SingletonOperation.GET:
                result = manager.get(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="GET")
                return result
            elif operation == SingletonOperation.SET:
                result = manager.set(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="SET")
                return result
            elif operation == SingletonOperation.HAS:
                result = manager.has(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="HAS")
                return result
            elif operation == SingletonOperation.DELETE:
                result = manager.delete(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="DELETE")
                return result
            elif operation == SingletonOperation.CLEAR:
                result = manager.clear(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="CLEAR")
                return result
            elif operation == SingletonOperation.GET_STATS:
                result = manager.get_stats(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="GET_STATS")
                return result
            elif operation == SingletonOperation.RESET:
                result = manager.reset(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="RESET")
                return result
            elif operation == SingletonOperation.RESET_ALL:
                result = manager.reset_all(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="RESET_ALL")
                return result
            elif operation == SingletonOperation.EXISTS:
                result = manager.exists(correlation_id=correlation_id, **kwargs)
                debug_log(correlation_id, "SINGLETON", "execute_singleton_operation completed",
                         success=True, operation="EXISTS")
                return result
            else:
                raise ValueError(f"Unknown singleton operation: {operation}")
        except Exception as e:
            debug_log(correlation_id, "SINGLETON",
                     f"Operation failed: {str(e)}",
                     operation=operation.value)
            raise Exception(f"Singleton operation '{operation.value}' failed: {e}") from e


def get_implementation(name: str, factory_func: Optional[Callable] = None,
                      correlation_id: str = None, **kwargs) -> Any:
    """
    Get or create singleton instance.
    
    Args:
        name: Singleton name
        factory_func: Optional factory function
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Singleton instance or None
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    from debug import debug_timing

    if correlation_id is None:
        correlation_id = generate_correlation_id()

    if not name:
        raise ValueError("Parameter 'name' is required for get operation")

    debug_log(correlation_id, "SINGLETON", "get_implementation called",
             name=name, has_factory=factory_func is not None)

    with debug_timing(correlation_id, "SINGLETON", "get_implementation",
                     name=name, has_factory=factory_func is not None):
        try:
            result = get_singleton_manager().get(
                name=name,
                factory_func=factory_func,
                correlation_id=correlation_id
            )
            debug_log(correlation_id, "SINGLETON", "get_implementation completed",
                     success=True, name=name)
            return result
        except Exception as e:
            debug_log(correlation_id, "SINGLETON", "get_implementation failed",
                     error_type=type(e).__name__, error=str(e), name=name)
            raise


def set_implementation(name: str, instance: Any, 
                      correlation_id: str = None, **kwargs):
    """
    Set singleton instance.
    
    Args:
        name: Singleton name
        instance: Instance to store
        correlation_id: Optional correlation ID for debug tracking
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not name:
        raise ValueError("Parameter 'name' is required for set operation")
    if instance is None and 'instance' not in kwargs:
        raise ValueError("Parameter 'instance' is required for set operation")
    
    debug_log(correlation_id, "SINGLETON", "set_implementation called",
             name=name, instance_type=type(instance).__name__)
    
    return get_singleton_manager().set(
        name=name,
        instance=instance,
        correlation_id=correlation_id
    )


def has_implementation(name: str, correlation_id: str = None, **kwargs) -> bool:
    """
    Check if singleton exists.
    
    Args:
        name: Singleton name
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        True if exists, False otherwise
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not name:
        raise ValueError("Parameter 'name' is required for has operation")
    
    debug_log(correlation_id, "SINGLETON", "has_implementation called", name=name)
    
    return get_singleton_manager().has(
        name=name,
        correlation_id=correlation_id
    )


def delete_implementation(name: str, correlation_id: str = None, **kwargs) -> bool:
    """
    Delete singleton instance.
    
    Args:
        name: Singleton name
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        True if deleted, False otherwise
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not name:
        raise ValueError("Parameter 'name' is required for delete operation")
    
    debug_log(correlation_id, "SINGLETON", "delete_implementation called", name=name)
    
    return get_singleton_manager().delete(
        name=name,
        correlation_id=correlation_id
    )


def clear_implementation(correlation_id: str = None, **kwargs) -> int:
    """
    Clear all singleton instances.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Count of singletons cleared
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SINGLETON", "clear_implementation called")
    
    return get_singleton_manager().clear(correlation_id=correlation_id)


def get_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get singleton statistics.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Statistics dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SINGLETON", "get_stats_implementation called")
    
    return get_singleton_manager().get_stats(correlation_id=correlation_id)


def reset_implementation(correlation_id: str = None, **kwargs) -> bool:
    """
    Reset singleton manager state.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        True if reset successful, False otherwise
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "SINGLETON", "reset_implementation called")
    
    return get_singleton_manager().reset(correlation_id=correlation_id)


__all__ = [
    'execute_singleton_operation',
    'get_implementation',
    'set_implementation',
    'has_implementation',
    'delete_implementation',
    'clear_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
