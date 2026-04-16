"""debug/debug_core.py
Version: 2025-12-08_1
Purpose: Core debug functionality with hierarchical control
License: Apache 2.0
"""

import time
import uuid
from contextlib import contextmanager
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.lee_debug.debug_config import get_debug_config

# Global trace context storage for Lambda (single-threaded)
_TRACE_CONTEXT: dict[str, Any] = {}

def debug_log(corr_id: str, scope: str, message: str, **context: Any) -> None:
    """Single-line debug logging with hierarchical control.
        corr_id: Correlation ID
        scope: Debug scope (ALEXA, HA, CACHE, etc.)
        **context: Additional context to log

    """

    # Lazy import gateway to avoid circular dependency
    def _log() -> Any:
        return execute_operation(GatewayInterface.LOGGING, "debug")

    config = get_debug_config()
    if not config.is_debug_enabled(scope):
        return  # Fast path: instant return when disabled

    # Format message with context
    context_str = ", ".join(f"{k}={v}" for k, v in context.items()) if context else ""
    full_message = f"[{corr_id}] [{scope}-DEBUG] {message}"
    if context_str:
        full_message += f" ({context_str})"

    _log()(full_message)

@contextmanager
def debug_timing(corr_id: str, scope: str, operation: str, **context: Any) -> Any:
    """Timing context manager with hierarchical control.
    
    Usage:
        with debug_timing(corr_id, "ALEXA", "enrichment"):
            # operation
    
        scope: Debug scope
        operation: Operation name
        **context: Additional context
    """

    # Lazy import gateway
    def _log():
        return execute_operation(GatewayInterface.LOGGING, "log_info")

    config = get_debug_config()

    # Debug log at start if enabled
    if config.is_debug_enabled(scope):
        debug_log(corr_id, scope, f"Starting {operation}", **context)

    # Timing measurement if enabled
    start_time = time.perf_counter() if config.is_timing_enabled(scope) else None

    try:
        yield
    finally:
        if start_time is not None:
            duration_ms = (time.perf_counter() - start_time) * 1000
            _log()(f"[{corr_id}] [{scope}-TIMING] {operation}: {duration_ms:.2f}ms")

def generate_correlation_id() -> str:
    """Generate correlation ID for request tracking."""
    return str(uuid.uuid4())[:13]

def generate_trace_id() -> str:
    """Generate trace ID for distributed tracing."""
    return str(uuid.uuid4())

def set_trace_context(trace_id: str, **context) -> None:
    """Set trace context for log correlation.

        trace_id: Trace ID
        **context: Additional context to store

    """
    # Implementation using thread-local or context vars
    # For Lambda (single-threaded), use global dict
    global _TRACE_CONTEXT  # pylint: disable=global-variable-undefined
    _TRACE_CONTEXT[trace_id] = {
        "trace_id": trace_id,
        "timestamp": time.time(),
        **context,
    }

def get_trace_context(trace_id: str) -> Optional[dict[str, Any]]:
    """Get trace context by ID.
    
        trace_id: Trace ID
        
        Context dict or None if not found

    """
    if "_TRACE_CONTEXT" not in globals():
        return None
    return globals()["_TRACE_CONTEXT"].get(trace_id)

def clear_trace_context(trace_id: str) -> None:
    """Clear trace context.
    
        trace_id: Trace ID to clear

    """
    if "_TRACE_CONTEXT" in globals():
        globals()["_TRACE_CONTEXT"].pop(trace_id, None)

__all__ = [
    "clear_trace_context",
    "debug_log",
    "debug_timing",
    "generate_correlation_id",
    "generate_trace_id",
    "get_trace_context",
    "set_trace_context",
]
