"""
interface/interface_initialization.py
Version: 2025-12-13_1
Purpose: Initialization interface router with import protection
License: Apache 2.0
"""

from typing import Any

# Import protection
try:
    import initialization
    _INITIALIZATION_AVAILABLE = True
    _INITIALIZATION_IMPORT_ERROR = None
except ImportError as e:
    _INITIALIZATION_AVAILABLE = False
    _INITIALIZATION_IMPORT_ERROR = str(e)


_VALID_INITIALIZATION_OPERATIONS = [
    'initialize', 'get_config', 'is_initialized', 'reset',
    'get_status', 'get_stats', 'set_flag', 'get_flag'
]


def execute_initialization_operation(operation: str, **kwargs) -> Any:
    """
    Route initialization operation requests to internal implementations.
    
    Args:
        operation: Initialization operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Initialization interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    if not _INITIALIZATION_AVAILABLE:
        raise RuntimeError(
            f"Initialization interface unavailable: {_INITIALIZATION_IMPORT_ERROR}"
        )
    
    if operation not in _VALID_INITIALIZATION_OPERATIONS:
        raise ValueError(
            f"Unknown initialization operation: '{operation}'. "
            f"Valid: {', '.join(_VALID_INITIALIZATION_OPERATIONS)}"
        )
    
    if operation == 'initialize':
        return initialization.initialize_implementation(**kwargs)
    
    elif operation == 'get_config':
        return initialization.get_config_implementation(**kwargs)
    
    elif operation == 'is_initialized':
        return initialization.is_initialized_implementation(**kwargs)
    
    elif operation == 'reset':
        return initialization.reset_implementation(**kwargs)
    
    elif operation == 'get_status':
        return initialization.get_status_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return initialization.get_stats_implementation(**kwargs)
    
    elif operation == 'set_flag':
        if 'flag_name' not in kwargs:
            raise ValueError("initialization.set_flag requires 'flag_name' parameter")
        if 'value' not in kwargs:
            raise ValueError("initialization.set_flag requires 'value' parameter")
        if not isinstance(kwargs['flag_name'], str):
            raise TypeError(f"'flag_name' must be str, got {type(kwargs['flag_name']).__name__}")
        return initialization.set_flag_implementation(**kwargs)
    
    elif operation == 'get_flag':
        if 'flag_name' not in kwargs:
            raise ValueError("initialization.get_flag requires 'flag_name' parameter")
        if not isinstance(kwargs['flag_name'], str):
            raise TypeError(f"'flag_name' must be str, got {type(kwargs['flag_name']).__name__}")
        return initialization.get_flag_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled initialization operation: '{operation}'")


__all__ = ['execute_initialization_operation']
