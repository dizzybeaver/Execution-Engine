"""
interface/interface_circuit_breaker.py
Version: 2025-12-13_1
Purpose: Circuit breaker interface router with import protection
License: Apache 2.0
"""

from typing import Any, Callable, Dict

# Import protection
try:
    import circuit_breaker
    _CIRCUIT_BREAKER_AVAILABLE = True
    _CIRCUIT_BREAKER_IMPORT_ERROR = None
except ImportError as e:
    _CIRCUIT_BREAKER_AVAILABLE = False
    _CIRCUIT_BREAKER_IMPORT_ERROR = str(e)


_VALID_CIRCUIT_BREAKER_OPERATIONS = [
    'get', 'call', 'get_all_states', 'reset_all', 'get_stats', 'reset'
]


def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any:
    """
    Route circuit breaker operations to internal implementations.
    
    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Circuit Breaker interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    # Check availability
    if not _CIRCUIT_BREAKER_AVAILABLE:
        raise RuntimeError(
            f"Circuit Breaker interface unavailable: {_CIRCUIT_BREAKER_IMPORT_ERROR}"
        )
    
    if operation not in _VALID_CIRCUIT_BREAKER_OPERATIONS:
        raise ValueError(
            f"Unknown circuit breaker operation: '{operation}'. "
            f"Valid: {', '.join(_VALID_CIRCUIT_BREAKER_OPERATIONS)}"
        )
    
    if operation == 'get':
        if 'name' not in kwargs:
            raise ValueError("circuit_breaker.get requires 'name' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"'name' must be str, got {type(kwargs['name']).__name__}")
        return circuit_breaker.get_breaker_implementation(**kwargs)
    
    elif operation == 'call':
        if 'name' not in kwargs:
            raise ValueError("circuit_breaker.call requires 'name' parameter")
        if 'func' not in kwargs:
            raise ValueError("circuit_breaker.call requires 'func' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"'name' must be str, got {type(kwargs['name']).__name__}")
        if not callable(kwargs['func']):
            raise TypeError(f"'func' must be callable, got {type(kwargs['func']).__name__}")
        return circuit_breaker.execute_with_breaker_implementation(**kwargs)
    
    elif operation == 'get_all_states':
        return circuit_breaker.get_all_states_implementation(**kwargs)
    
    elif operation == 'reset_all':
        return circuit_breaker.reset_all_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return circuit_breaker.get_stats_implementation(**kwargs)
    
    elif operation == 'reset':
        return circuit_breaker.reset_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled circuit breaker operation: '{operation}'")


__all__ = ['execute_circuit_breaker_operation']
