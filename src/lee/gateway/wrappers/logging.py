"""Logging Wrapper Functions

Direct access to logging operations (7 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import logging

    # Log info message
    logging.log_info(message='System started')

    # Log error with exception
    logging.log_error(message='Connection failed', error=exc)

    # Log warning
    logging.log_warning(message='High memory usage')

    # Log debug message
    logging.log_debug(message='Variable state', value=data)

    # Operation lifecycle logging
    logging.log_operation_start(operation_name='process_request')
    logging.log_operation_success(operation_name='process_request', duration_ms=45.2)
    logging.log_operation_failure(operation_name='process_request', error='Timeout')
"""

from typing import Any, Optional

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def log_info(message: str, **kwargs: Any) -> None:
    """Log info message.

    Args:
        message: Message to log
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, **kwargs)


def log_error(message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
    """Log error message.

    Args:
        message: Error message to log
        error: Exception object (optional)
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, **kwargs)


def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message.

    Args:
        message: Warning message to log
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, **kwargs)


def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message.

    Args:
        message: Debug message to log
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, **kwargs)


def log_operation_start(operation_name: str, **kwargs: Any) -> None:
    """Log operation start.

    Args:
        operation_name: Name of operation being started
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation_name=operation_name, **kwargs)


def log_operation_success(operation_name: str, duration_ms: float, **kwargs: Any) -> None:
    """Log operation success.

    Args:
        operation_name: Name of operation that succeeded
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation_name=operation_name, duration_ms=duration_ms, **kwargs)


def log_operation_failure(operation_name: str, error: str, **kwargs: Any) -> None:
    """Log operation failure.

    Args:
        operation_name: Name of operation that failed
        error: Error description
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation_name=operation_name, error=error, **kwargs)


__all__ = [
    'log_debug',
    'log_error',
    'log_info',
    'log_operation_failure',
    'log_operation_start',
    'log_operation_success',
    'log_warning',
]
