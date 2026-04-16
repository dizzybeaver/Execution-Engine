"""lee_utility/error_handler.py
Version: 2026-03-26_1
Purpose: Standardized error handling for LEE system
License: Apache 2.0

Provides unified error handling across all LEE modules, replacing generic
Exception handling with specific exception types for better error diagnosis
and recovery.

Exception Categories:
1. Gateway Unavailable: ImportError, AttributeError - acceptable for standalone usage
2. Invalid Input: ValueError, TypeError, KeyError - parameter validation errors
3. Network Operations: ConnectionError, TimeoutError - expected network failures
4. Runtime Issues: RuntimeError, MemoryError, OSError - system-level errors
5. Security Issues: PermissionError, SecurityError - security-related errors
6. Unexpected Errors: Generic Exception - fallback for unknown issues
"""

import os
from typing import Any, Literal, Optional

try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    GatewayInterface = None
    execute_operation = None


ErrorCategory = Literal[
    "Gateway Unavailable",
    "Invalid Input",
    "Network Operation",
    "Runtime Error",
    "Security Error",
    "Unexpected Error"
]

ErrorSeverity = Literal["debug", "info", "warning", "error", "critical"]


class UnifiedErrorHandler:
    """Standardized error handling for all LEE operations.

    Supports configurable categorization for different subsystems (cache, gateway, etc.).
    """

    def __init__(
        self,
        operation_name: str = "operation",
        correlation_id: str = None,
        scope: str = "LEE_SYSTEM",
        categorization_rules: Optional[dict[str, tuple[list[type[Exception]], ErrorSeverity]]] = None
    ):
        """Initialize unified error handler.

        Args:
            operation_name: Name of the operation for logging
            correlation_id: Request correlation ID for tracing
            scope: Operational scope for logging categorization
            categorization_rules: Optional custom categorization rules mapping
                                 category names to (exception_types, severity) tuples
        """
        self.operation_name = operation_name
        self.correlation_id = correlation_id
        self.scope = scope
        self._sanitize_exceptions = self._should_sanitize()
        self._categorization_rules = categorization_rules

    def _should_sanitize(self) -> bool:
        """Determine if exception sanitization should be enabled.

        Returns:
            True if exceptions should be sanitized (production mode)

        Security: Always sanitize except in controlled test environments
        with explicit disable flag. Prevents information disclosure in
        staging and production environments.
        """
        # Default to production environment for security
        env = os.getenv("ENVIRONMENT", "production").lower()

        # Only allow disabling sanitization in controlled test environments
        if env in ("test", "development"):
            # Require explicit flag to disable sanitization
            return os.getenv("DISABLE_ERROR_SANITIZATION", "false").lower() != "true"

        # Always sanitize in production and staging
        return True

    # pylint: disable=too-many-arguments
    def handle_exception(
        self,
        exception: Exception,
        context: str = "",
        gateway_interface: Any = None,
        execute_op: Any = None,
        re_raise: bool = True
    ) -> Optional[dict[str, Any]]:
        """Handle exception with specific error types and standardized logging.

        This method provides specific exception handling for all LEE operations,
        replacing generic Exception catching with targeted error diagnosis and
        recovery.

        Args:
            exception: The exception to handle
            context: Additional context about where error occurred
            gateway_interface: Gateway interface for logging (optional)
            execute_op: Execute operation function for logging (optional)
            re_raise: Whether to re-raise the exception after logging

        Returns:
            None if re_raise=True, standardized error response dict if re_raise=False

        Raises:
            Re-raises the original exception if re_raise=True
        """
        if gateway_interface is None:
            gateway_interface = GatewayInterface
        if execute_op is None:
            execute_op = execute_operation

        error_category, severity = self._categorize_exception(exception)

        self._log_error(
            exception=exception,
            context=context,
            error_category=error_category,
            severity=severity,
            gateway_interface=gateway_interface,
            execute_op=execute_op
        )

        if not re_raise:
            return self._create_error_response(exception, error_category, context)

        raise exception

    # pylint: disable=too-many-return-statements
    def _categorize_exception(self, exception: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Categorize exception by type for appropriate handling.

        Supports custom categorization rules for subsystem-specific handling.

        Args:
            exception: The exception to categorize

        Returns:
            Tuple of (error_category, severity)
        """
        # Use custom categorization rules if provided
        if self._categorization_rules:
            for category, (exception_types, severity) in self._categorization_rules.items():
                if isinstance(exception, tuple(exception_types)):
                    return category, severity

        # Default categorization rules
        if isinstance(exception, (ImportError, AttributeError)):
            return "Gateway Unavailable", "debug"
        if isinstance(exception, (ValueError, TypeError, KeyError)):
            return "Invalid Input", "warning"
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return "Network Operation", "error"
        if isinstance(exception, (RuntimeError, MemoryError, OSError)):
            return "Runtime Error", "critical"
        if isinstance(exception, PermissionError):
            return "Security Error", "critical"
        return "Unexpected Error", "error"

    # pylint: disable=too-many-arguments
    def _log_error(
        self,
        exception: Exception,
        context: str,
        error_category: ErrorCategory,
        severity: ErrorSeverity,
        gateway_interface: Any,
        execute_op: Any
    ) -> None:
        """Log error with appropriate severity and context.

        Args:
            exception: The exception to log
            context: Additional context about where error occurred
            error_category: Category of error for filtering
            severity: Log severity level
            gateway_interface: Gateway interface for logging
            execute_op: Execute operation function for logging
        """
        if not _GATEWAY_AVAILABLE or not execute_op or not gateway_interface:
            return

        try:
            error_msg = self._sanitize_exception(exception) if self._sanitize_exceptions else str(exception)

            log_params = {
                "message": f"{error_category} in {self.operation_name}",
                "scope": self.scope,
                "exception_type": type(exception).__name__,
                "op_name": self.operation_name,
            }

            if context:
                log_params["extra_context"] = context

            if self.correlation_id:
                log_params["corr_id"] = self.correlation_id

            if error_msg:
                log_params["error"] = error_msg

            self._route_log_by_severity(severity, log_params, gateway_interface, execute_op)

        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

    def _route_log_by_severity(
        self,
        severity: ErrorSeverity,
        log_params: dict[str, Any],
        gateway_interface: Any,
        execute_op: Any
    ) -> None:
        """Route log message to appropriate log level.

        Args:
            severity: Log severity level
            log_params: Logging parameters
            gateway_interface: Gateway interface
            execute_op: Execute operation function
        """
        # Route to appropriate log level using dictionary dispatch (O(1) lookup)
        def _log_critical():
            execute_op(gateway_interface.LOGGING, "log_error", **log_params)

        def _log_error():
            execute_op(gateway_interface.LOGGING, "log_error", **log_params)

        def _log_warning():
            execute_op(gateway_interface.LOGGING, "log_warning", **log_params)

        def _log_info():
            execute_op(gateway_interface.LOGGING, "log_info", **log_params)

        def _log_debug():
            execute_op(gateway_interface.LOGGING, "log_debug", **log_params)

        severity_dispatch = {
            "critical": _log_critical,
            "error": _log_error,
            "warning": _log_warning,
            "info": _log_info,
        }

        log_handler = severity_dispatch.get(severity, _log_debug)
        log_handler()

    def _sanitize_exception(self, exception: Exception) -> str:
        """Sanitize exception details to prevent information disclosure.

        Args:
            exception: The exception to sanitize

        Returns:
            Sanitized error message
        """
        error_msg = str(exception)[:500]

        sanitized_msg = error_msg.replace("/var/task/", "[APP]/")
        sanitized_msg = sanitized_msg.replace("/opt/python/", "[LIB]/")
        sanitized_msg = sanitized_msg.replace(os.path.abspath(os.path.dirname(__file__)), "[APP]")

        sanitized_msg = sanitized_msg.replace("\\\\var\\task\\", "[APP]\\")
        sanitized_msg = sanitized_msg.replace("\\\\opt\\python\\", "[LIB]\\")

        import re  # noqa: E402
        sanitized_msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', sanitized_msg)
        sanitized_msg = re.sub(r'[A-Fa-f0-9]{32,}', '[TOKEN]', sanitized_msg)

        return f"{type(exception).__name__}: {sanitized_msg}"

    def _create_error_response(
        self,
        exception: Exception,
        error_category: ErrorCategory,
        context: str
    ) -> dict[str, Any]:
        """Create standardized error response dictionary.

        Args:
            exception: The exception that occurred
            error_category: Category of the error
            context: Additional context

        Returns:
            Standardized error response dictionary
        """
        return {
            "success": False,
            "error": self._sanitize_exception(exception) if self._sanitize_exceptions else str(exception),
            "error_type": type(exception).__name__,
            "error_category": error_category,
            "operation": self.operation_name,
            "context": context if context else None,
            "correlation_id": self.correlation_id
        }


# pylint: disable=too-many-arguments
def handle_error(
    exception: Exception,
    operation_name: str = "operation",
    context: str = "",
    correlation_id: str = None,
    scope: str = "LEE_SYSTEM",
    gateway_interface: Any = None,
    execute_op: Any = None,
    re_raise: bool = True
) -> Optional[dict[str, Any]]:
    """Convenience function for handling exceptions with standardized error handling.

    Usage:
        except ValueError as e:
            return handle_error(
                exception=e,
                operation_name="cache_get",
                context="Failed to retrieve value",
                correlation_id=corr_id,
                re_raise=False
            )

    Args:
        exception: The exception to handle
        operation_name: Name of the operation for logging
        context: Additional context about where error occurred
        correlation_id: Request correlation ID for tracing
        scope: Operational scope for logging categorization
        gateway_interface: Gateway interface for logging (optional)
        execute_op: Execute operation function for logging (optional)
        re_raise: Whether to re-raise the exception after logging

    Returns:
        None if re_raise=True, standardized error response dict if re_raise=False

    Raises:
        Re-raises the original exception if re_raise=True
    """
    handler = UnifiedErrorHandler(
        operation_name=operation_name,
        correlation_id=correlation_id,
        scope=scope
    )
    return handler.handle_exception(
        exception=exception,
        context=context,
        gateway_interface=gateway_interface,
        execute_op=execute_op,
        re_raise=re_raise
    )


def create_error_response(
    error: str | Exception,
    operation: str = "operation",
    error_category: ErrorCategory = "Unexpected Error",
    context: str = ""
) -> dict[str, Any]:
    """Create standardized error response dictionary without logging.

    Use this when you need to return an error response but don't want to
    trigger logging (e.g., for expected failures that don't need to be logged).

    Args:
        error: Error message or exception
        operation: Name of the operation that failed
        error_category: Category of the error
        context: Additional context about the error

    Returns:
        Standardized error response dictionary
    """
    if isinstance(error, Exception):
        error_msg = str(error)
        error_type = type(error).__name__
    else:
        error_msg = str(error)
        error_type = "Error"

    return {
        "success": False,
        "error": error_msg,
        "error_type": error_type,
        "error_category": error_category,
        "operation": operation,
        "context": context if context else None
    }


__all__ = [
    "UnifiedErrorHandler",
    "handle_error",
    "create_error_response",
    "ErrorCategory",
    "ErrorSeverity",
]
