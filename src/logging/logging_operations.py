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

import os
import time
import logging

from logging.logging_types import LogOperation

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


# ===== GENERIC OPERATION EXECUTION =====

def execute_logging_operation(operation: LogOperation, *args, **kwargs):
    """
    Universal logging operation executor with dispatcher performance monitoring.
    
    NOTE: This function is retained for backward compatibility but is deprecated.
    New code should use interface_logging.execute_logging_operation() instead.
    """
    start_time = time.time()
    
    # Route through interface for consistency
    try:
        # Lazy import to avoid circular dependencies
        from interface_logging import execute_logging_operation as interface_execute
        result = interface_execute(operation.value if isinstance(operation, LogOperation) else operation, **kwargs)
    except Exception as e:
        logger.error(f"Operation {operation} failed: {str(e)}")
        result = None
    
    duration_ms = (time.time() - start_time) * 1000
    _record_dispatcher_metric(operation, duration_ms)
    
    return result


def _record_dispatcher_metric(operation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation."""
    try:
        from gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.METRICS,
            'record_dispatcher_timing',
            interface_name='LoggingCore',
            operation_name=operation.value if isinstance(operation, LogOperation) else str(operation),
            duration_ms=duration_ms
        )
    except Exception:
        pass


# ===== EXPORTS =====

__all__ = [
    'execute_logging_operation',
]
