"""
interface_debug.py
Version: 2025-12-13_1
Purpose: DEBUG interface router (INT-14) - Runtime inspection
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import from debug package instead of debug_core module
"""

from typing import Any

_DEBUG_AVAILABLE = True
_DEBUG_IMPORT_ERROR = None

try:
    from debug import (
        debug_log,
        debug_timing,
        generate_correlation_id,
        generate_trace_id,
        set_trace_context,
        get_trace_context,
        clear_trace_context
    )
except ImportError as e:
    _DEBUG_AVAILABLE = False
    _DEBUG_IMPORT_ERROR = str(e)

def execute_debug_operation(operation: str, **kwargs) -> Any:
    """
    Route debug operations to core implementations.
    
    Args:
        operation: Debug operation name
        **kwargs: Operation parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If DEBUG unavailable
        ValueError: If unknown operation
    """
    if not _DEBUG_AVAILABLE:
        raise RuntimeError(f"DEBUG unavailable: {_DEBUG_IMPORT_ERROR}")
    
    if operation == 'log':
        return debug_log(**kwargs)
    elif operation == 'timing':
        return debug_timing(**kwargs)
    elif operation == 'generate_correlation_id':
        return generate_correlation_id()
    elif operation == 'generate_trace_id':
        return generate_trace_id()
    elif operation == 'set_trace_context':
        return set_trace_context(**kwargs)
    elif operation == 'get_trace_context':
        return get_trace_context(**kwargs)
    elif operation == 'clear_trace_context':
        return clear_trace_context(**kwargs)
    else:
        raise ValueError(f"Unknown debug operation: {operation}")

__all__ = ['execute_debug_operation']
