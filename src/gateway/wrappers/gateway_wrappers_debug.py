"""
gateway_wrappers_debug.py
Version: 2025-12-13_1
Purpose: Gateway wrappers for DEBUG interface (INT-14)
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import path from interface.interface_debug
"""

from typing import Any, Dict, Optional

def debug_log(corr_id: str, scope: str, message: str, **context) -> None:
    """
    Single-line debug logging with hierarchical control.
    
    Args:
        corr_id: Correlation ID
        scope: Debug scope (ALEXA, HA, CACHE, etc.)
        message: Debug message
        **context: Additional context
    """
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('log', corr_id=corr_id, scope=scope, 
                                   message=message, **context)

def debug_timing(corr_id: str, scope: str, operation: str, **context):
    """
    Timing context manager with hierarchical control.
    
    Usage:
        with debug_timing(corr_id, "ALEXA", "enrichment"):
            # operation code
    
    Args:
        corr_id: Correlation ID
        scope: Debug scope
        operation: Operation name
        **context: Additional context
    """
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('timing', corr_id=corr_id, scope=scope,
                                   operation=operation, **context)

def generate_correlation_id() -> str:
    """Generate correlation ID for request tracking."""
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('generate_correlation_id')

def generate_trace_id() -> str:
    """Generate trace ID for distributed tracing."""
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('generate_trace_id')

def set_trace_context(trace_id: str, **context) -> None:
    """
    Set trace context for log correlation.
    
    Args:
        trace_id: Trace ID
        **context: Context to store
    """
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('set_trace_context', trace_id=trace_id, **context)

def get_trace_context(trace_id: str) -> Optional[Dict[str, Any]]:
    """
    Get trace context by ID.
    
    Args:
        trace_id: Trace ID
        
    Returns:
        Context dict or None
    """
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('get_trace_context', trace_id=trace_id)

def clear_trace_context(trace_id: str) -> None:
    """
    Clear trace context.
    
    Args:
        trace_id: Trace ID
    """
    from interface.interface_debug import execute_debug_operation
    return execute_debug_operation('clear_trace_context', trace_id=trace_id)

__all__ = [
    'debug_log',
    'debug_timing',
    'generate_correlation_id',
    'generate_trace_id',
    'set_trace_context',
    'get_trace_context',
    'clear_trace_context'
]
