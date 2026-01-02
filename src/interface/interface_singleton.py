"""
interface/interface_singleton.py
Version: 2025-12-13_1
Purpose: Singleton interface router with import protection
License: Apache 2.0
"""

from typing import Any

# Import protection
try:
    import singleton
    _SINGLETON_AVAILABLE = True
    _SINGLETON_IMPORT_ERROR = None
except ImportError as e:
    _SINGLETON_AVAILABLE = False
    _SINGLETON_IMPORT_ERROR = str(e)


_VALID_SINGLETON_OPERATIONS = [
    'get', 'set', 'has', 'delete', 'clear', 'stats', 'get_stats', 'reset'
]


def _validate_name_param(kwargs: dict, operation: str) -> None:
    """Validate name parameter presence and type."""
    if 'name' not in kwargs:
        raise ValueError(f"singleton.{operation} requires 'name' parameter")
    if not isinstance(kwargs['name'], str):
        raise TypeError(
            f"singleton.{operation} 'name' must be str, got {type(kwargs['name']).__name__}"
        )


def _validate_set_params(kwargs: dict, operation: str) -> None:
    """Validate set operation parameters."""
    _validate_name_param(kwargs, operation)
    if 'instance' not in kwargs:
        raise ValueError(f"singleton.{operation} requires 'instance' parameter")


def execute_singleton_operation(operation: str, **kwargs) -> Any:
    """
    Route singleton operation requests to internal implementations.
    
    Args:
        operation: The singleton operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Singleton interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    if not _SINGLETON_AVAILABLE:
        raise RuntimeError(
            f"Singleton interface unavailable: {_SINGLETON_IMPORT_ERROR}"
        )
    
    if operation == 'get':
        _validate_name_param(kwargs, operation)
        return singleton.get_implementation(**kwargs)
    
    elif operation == 'set':
        _validate_set_params(kwargs, operation)
        return singleton.set_implementation(**kwargs)
    
    elif operation == 'has':
        _validate_name_param(kwargs, operation)
        return singleton.has_implementation(**kwargs)
    
    elif operation == 'delete':
        _validate_name_param(kwargs, operation)
        return singleton.delete_implementation(**kwargs)
    
    elif operation == 'clear':
        return singleton.clear_implementation(**kwargs)
    
    elif operation == 'stats' or operation == 'get_stats':
        return singleton.get_stats_implementation(**kwargs)
    
    elif operation == 'reset':
        return singleton.reset_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown singleton operation: '{operation}'. "
            f"Valid: {', '.join(_VALID_SINGLETON_OPERATIONS)}"
        )


__all__ = ['execute_singleton_operation']
