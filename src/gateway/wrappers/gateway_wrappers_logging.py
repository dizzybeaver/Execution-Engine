"""
gateway/wrappers/gateway_wrappers_logging.py
Version: 2025-12-08_1
Purpose: LOGGING interface gateway wrappers
License: Apache 2.0

CHANGES (2025-12-08_1):
- Moved to gateway/wrappers/ subdirectory
- Updated version for logging/ subdirectory refactoring
- No functional changes (wrappers use gateway pattern correctly)
"""

from typing import Optional
from gateway_core import GatewayInterface, execute_operation


def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, **kwargs)


def log_error(message: str, error: Optional[Exception] = None, **kwargs) -> None:
    """Log error message."""
    execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, **kwargs)


def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, **kwargs)


def log_operation_start(operation_name: str, **kwargs) -> None:
    """
    Log operation start.
    
    Args:
        operation_name: Name of operation being started
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation_name=operation_name, **kwargs)


def log_operation_success(operation_name: str, duration_ms: float, **kwargs) -> None:
    """
    Log operation success.
    
    Args:
        operation_name: Name of operation that succeeded
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation_name=operation_name, duration_ms=duration_ms, **kwargs)


def log_operation_failure(operation_name: str, error: str, **kwargs) -> None:
    """
    Log operation failure.
    
    Args:
        operation_name: Name of operation that failed
        error: Error description
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation_name=operation_name, error=error, **kwargs)


__all__ = [
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
]
