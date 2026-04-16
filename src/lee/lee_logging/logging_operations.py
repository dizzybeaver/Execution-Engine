"""
logging/logging_operations.py
Version: 2025-12-08_1
Purpose: Logging operation dispatcher with performance monitoring
License: Apache 2.0

CHANGES (2025-12-08_1):
- Moved to logging/ subdirectory
- Updated imports for logging/ subdirectory
- Removed _MANAGER reference (deprecated)
"""

import logging
import os
import time

from lee.gateway import GatewayInterface, execute_operation
from lee.lee_logging.logging_generic import (
    _execute_log_debug_implementation,
    _execute_log_error_implementation,
    _execute_log_info_implementation,
    _execute_log_operation_failure_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_reset_implementation,
    _execute_log_warning_implementation,
)
from lee.lee_logging.logging_types import LogOperation

_USE_GENERIC_OPERATIONS = os.environ.get("USE_GENERIC_OPERATIONS", "true").lower() == "true"

logger = logging.getLogger(__name__)

def execute_logging_operation(operation: LogOperation, *_args, **kwargs):
    """Universal logging operation executor with dispatcher performance monitoring.

    NOTE: This function is retained for backward compatibility but is deprecated.
    Core modules should NOT import from interface layers (SUGA-ISP violation).
    This function now implements core logging directly.
    """
    operation_str = operation.value if isinstance(operation, LogOperation) else str(operation)

    # FIXED: Removed debug logging call that caused infinite recursion
    # logging_operations calling DEBUG.log which calls execute_operation which may trigger LOGGING operations
    # This creates a circular dependency: LOGGING → DEBUG → LOGGING → DEBUG → ...

    start_time = time.time()

    # FIXED: Removed debug timing call that caused infinite recursion
    # Use nullcontext instead of trying to call DEBUG operations
    from contextlib import nullcontext  # pylint: disable=import-outside-toplevel
    timing_ctx = nullcontext()

    with timing_ctx:
        try:
            # Direct implementation (SUGA-ISP compliant - no interface imports)
            result = _execute_logging_core(operation_str, **kwargs)

            # FIXED: Removed debug logging call that caused infinite recursion
            ...
        except (ValueError, TypeError, KeyError, RuntimeError, ConnectionError, OSError):
            # FIXED: Removed debug logging call that caused infinite recursion
            ...

    duration_ms = (time.time() - start_time) * 1000
    _record_dispatcher_metric(operation, duration_ms)

    return result


def _execute_logging_core(operation: str, **kwargs):
    """Core logging implementation without interface dependencies."""

    core_functions = {
        "log_info": _execute_log_info_implementation,
        "log_error": _execute_log_error_implementation,
        "log_warning": _execute_log_warning_implementation,
        "log_debug": _execute_log_debug_implementation,
        "log_operation_start": _execute_log_operation_start_implementation,
        "log_operation_success": _execute_log_operation_success_implementation,
        "log_operation_failure": _execute_log_operation_failure_implementation,
        "reset": _execute_log_reset_implementation,
        "reset_logging": _execute_log_reset_implementation,
    }

    handler = core_functions.get(operation)
    if not handler:
        raise ValueError(f"Unknown logging operation: {operation}")

    return handler(**kwargs)


def _record_dispatcher_metric(operation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation."""
    try:
        execute_operation(
            GatewayInterface.OBSERVABILITY,
            "record_dispatcher_timing",
            interface_name="LoggingCore",
            operation_name=operation.value if isinstance(operation, LogOperation) else str(operation),
            duration_ms=duration_ms,
        )
    except (ImportError, AttributeError, ValueError, TypeError, KeyError, RuntimeError, ConnectionError):
        # Optional dependency - continue if unavailable
        ...


# ===== EXPORTS =====

__all__ = [
    "execute_logging_operation",
]
