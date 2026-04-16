# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Create standardized error response factory

"""ha_errors.py - Home Assistant Error Response Factory

Provides standardized error response generation with correlation IDs for
consistent error handling across all HA gateway operations.

All error responses include:
- correlation_id: For tracking and debugging
- error_type: Category of error
- message: Human-readable error description
- timestamp: When error occurred
- context: Additional debugging context
"""

import time
from datetime import datetime, UTC
from typing import Any

from lee.gateway import GatewayInterface, execute_operation


def error_response(
    error_type: str,
    message: str,
    correlation_id: str = None,
    **context: Any,
) -> dict[str, Any]:
    """Create standardized error response with correlation ID.

    Args:
        error_type: Category of error (e.g., 'import_error', 'validation_error')
        message: Human-readable error description
        correlation_id: Optional correlation ID for tracking
        **context: Additional debugging context (operation, interface, etc.)

    Returns:
        Dictionary with standardized error format:
        {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'correlation_id': correlation_id,
            'timestamp': ISO timestamp,
            'context': {...}
        }

    """
    # Generate correlation ID if not provided
    if correlation_id is None:
        correlation_id = f"ha_err_{int(time.time() * 1000)}"

    # Build error response (use different variable name to avoid shadowing function)
    response_dict = {
        "success": False,
        "error": message,
        "error_type": error_type,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Add additional context if provided
    if context:
        response_dict["context"] = context

    # Log error with correlation ID (avoid parameter name conflicts)
    log_context = {k: v for k, v in context.items() if k not in ["interface", "operation"]}
    execute_operation(
        GatewayInterface.LOGGING,
        "log_error",
        message=f"[{correlation_id}] {error_type}: {message}",
        corr_id=correlation_id,
        **log_context,
    )

    return response_dict


def validation_error(
    message: str,
    field: str = None,
    correlation_id: str = None,
    **context: Any,
) -> dict[str, Any]:
    """Create validation error response.

    Args:
        message: Validation error description
        field: Optional field name that failed validation
        correlation_id: Optional correlation ID for tracking
        **context: Additional debugging context

    Returns:
        Standardized error response with error_type='validation_error'

    """
    error_context = {"field": field} if field else {}
    error_context.update(context)

    return error_response(
        error_type="validation_error",
        message=message,
        correlation_id=correlation_id,
        **error_context,
    )


def import_error(
    module_name: str,
    interface: str = None,
    correlation_id: str = None,
    original_error: str = None,
) -> dict[str, Any]:
    """Create import error response.

    Args:
        module_name: Module that failed to import
        interface: Optional interface name
        correlation_id: Optional correlation ID for tracking
        original_error: Optional original error message

    Returns:
        Standardized error response with error_type='import_error'

    """
    message = f"Failed to import module '{module_name}'"
    if interface:
        message += f" for {interface}"

    if original_error:
        message += f": {original_error}"

    context = {"module_name": module_name}
    if interface:
        context["interface"] = interface

    return error_response(
        error_type="import_error",
        message=message,
        correlation_id=correlation_id,
        **context,
    )


def execution_error(
    operation: str,
    interface: str = None,
    correlation_id: str = None,
    original_error: str = None,
) -> dict[str, Any]:
    """Create execution error response.

    Args:
        operation: Operation that failed
        interface: Optional interface name
        correlation_id: Optional correlation ID for tracking
        original_error: Optional original error message

    Returns:
        Standardized error response with error_type='execution_error'

    """
    message = f"Failed to execute {operation}"
    if interface:
        message = f"Failed to execute {interface}.{operation}"

    if original_error:
        message += f": {original_error}"

    context = {"operation": operation}
    if interface:
        context["interface"] = interface

    return error_response(
        error_type="execution_error",
        message=message,
        correlation_id=correlation_id,
        **context,
    )


def timeout_error(
    operation: str,
    timeout_seconds: float,
    correlation_id: str = None,
) -> dict[str, Any]:
    """Create timeout error response.

    Args:
        operation: Operation that timed out
        timeout_seconds: Timeout duration
        correlation_id: Optional correlation ID for tracking

    Returns:
        Standardized error response with error_type='timeout_error'

    """
    message = f"Operation '{operation}' timed out after {timeout_seconds}s"

    return error_response(
        error_type="timeout_error",
        message=message,
        correlation_id=correlation_id,
        operation=operation,
        timeout_seconds=timeout_seconds,
    )


def connection_error(
    service: str,
    correlation_id: str = None,
    original_error: str = None,
) -> dict[str, Any]:
    """Create connection error response.

    Args:
        service: Service that failed to connect
        correlation_id: Optional correlation ID for tracking
        original_error: Optional original error message

    Returns:
        Standardized error response with error_type='connection_error'

    """
    message = f"Failed to connect to {service}"
    if original_error:
        message += f": {original_error}"

    return error_response(
        error_type="connection_error",
        message=message,
        correlation_id=correlation_id,
        service=service,
    )


def not_found_error(
    resource_type: str,
    resource_id: str = None,
    correlation_id: str = None,
) -> dict[str, Any]:
    """Create not found error response.

    Args:
        resource_type: Type of resource (e.g., 'entity', 'service')
        resource_id: Optional resource identifier
        correlation_id: Optional correlation ID for tracking

    Returns:
        Standardized error response with error_type='not_found_error'

    """
    message = f"{resource_type} not found"
    if resource_id:
        message = f"{resource_type} '{resource_id}' not found"

    context = {"resource_type": resource_type}
    if resource_id:
        context["resource_id"] = resource_id

    return error_response(
        error_type="not_found_error",
        message=message,
        correlation_id=correlation_id,
        **context,
    )


def permission_error(
    action: str,
    resource: str = None,
    correlation_id: str = None,
) -> dict[str, Any]:
    """Create permission error response.

    Args:
        action: Action that requires permission
        resource: Optional resource being accessed
        correlation_id: Optional correlation ID for tracking

    Returns:
        Standardized error response with error_type='permission_error'

    """
    message = f"Permission denied for action '{action}'"
    if resource:
        message = f"Permission denied to {resource} for '{action}'"

    context = {"action": action}
    if resource:
        context["resource"] = resource

    return error_response(
        error_type="permission_error",
        message=message,
        correlation_id=correlation_id,
        **context,
    )
