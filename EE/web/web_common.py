"""
Web Common Module - EE Web Domain Gateway

This module provides common error handling and utilities for the Web domain gateway.
It extends the Gateway reference implementation with EE-specific error handling.

Architecture Layer: Layer 1 - Domain Gateway Infrastructure
Part of: Web Domain Gateway (gateway.web)

Based on: D:\\Code\\Project\\Gateway\\Web\\web_common.py
"""

from __future__ import annotations
from typing import Optional, Dict, Any

class WebConsoleError(Exception):
    """Base error for the EE Web Console.

    This error class provides enhanced error handling for web console operations
    with HTTP-specific context and error codes.

    Attributes:
        message: Human-readable error description
        http_status: Associated HTTP status code
        error_code: Optional error code for categorization
        context: Optional dictionary with error context
        source: Source component (defaults to "WebGateway")

    Example:
        >>> raise WebConsoleError("Invalid JSON payload", http_status=400)
        >>> raise WebConsoleError.from_exception(ValueError("bad data"), http_status=400)
    """

    def __init__(
        self,
        message: str,
        http_status: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a WebConsoleError.

        Args:
            message: Human-readable error description
            http_status: Associated HTTP status code (default: 500)
            error_code: Optional error code for categorization
            context: Optional dictionary with error context
        """
        self.http_status = http_status

        # Build error context with HTTP-specific information
        error_context = {
            "http_status": http_status,
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=message,
            error_code=error_code or "WEB_CONSOLE_ERROR",
            context=error_context,
            source="WebGateway",
        )

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        http_status: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> WebConsoleError:
        """Create a WebConsoleError from another exception.

        This factory method provides error chaining support by wrapping
        other exceptions in WebConsoleError while preserving the original
        exception information.

        Args:
            exc: The original exception to wrap
            http_status: Associated HTTP status code
            error_code: Optional error code for categorization
            context: Optional additional context

        Returns:
            A new WebConsoleError with the original exception chained

        Example:
            >>> try:
            ...     json.loads(invalid_data)
            ... except ValueError as e:
            ...     raise WebConsoleError.from_exception(e, http_status=400)
        """
        error_context = {
            "original_type": type(exc).__name__,
            "original_message": str(exc),
        }
        if context:
            error_context.update(context)

        new_error = cls(
            message=str(exc),
            http_status=http_status,
            error_code=error_code or cls._infer_error_code(exc, http_status),
            context=error_context,
        )
        # Use exception chaining (Python 3+)
        raise new_error from exc

    @staticmethod
    def _infer_error_code(exc: Exception, http_status: int) -> str:
        """Infer error code from exception type and HTTP status.

        Args:
            exc: Exception to analyze
            http_status: Associated HTTP status code

        Returns:
            Appropriate error code string
        """
        exc_type = type(exc).__name__

        # Map exception types to error codes
        error_code_map = {
            "KeyError": "KEY_NOT_FOUND",
            "ValueError": "INVALID_VALUE",
            "TypeError": "TYPE_ERROR",
            "AttributeError": "ATTRIBUTE_ERROR",
            "IndexError": "INDEX_ERROR",
            "RuntimeError": "RUNTIME_ERROR",
            "JSONDecodeError": "INVALID_JSON",
        }

        # Map HTTP status codes to error codes
        status_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }

        # Try exception type first, then HTTP status
        error_code = error_code_map.get(exc_type)
        if not error_code:
            error_code = status_code_map.get(http_status, "UNKNOWN_ERROR")

        return error_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation.

        Returns:
            Dictionary with all error information including HTTP status
        """
        result = super().to_dict()
        result["http_status"] = self.http_status
        return result


class InvalidJSONError(WebConsoleError):
    """Raised when JSON parsing fails."""

    def __init__(
        self,
        message: str = "Invalid JSON payload",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an InvalidJSONError.

        Args:
            message: Human-readable error description
            context: Optional additional context
        """
        super().__init__(
            message=message,
            http_status=400,
            error_code="INVALID_JSON",
            context=context,
        )


class RouteExecutionError(WebConsoleError):
    """Raised when route execution fails."""

    def __init__(
        self,
        route: str,
        original_error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a RouteExecutionError.

        Args:
            route: The route that failed to execute
            original_error: The original exception
            context: Optional additional context
        """
        error_context = {
            "route": route,
            "original_error_type": type(original_error).__name__,
            "original_error_message": str(original_error),
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=f"Route execution failed: {route}",
            http_status=500,
            error_code="ROUTE_EXECUTION_ERROR",
            context=error_context,
        )


class ConsoleNotStartedError(WebConsoleError):
    """Raised when trying to use a console that hasn't been started."""

    def __init__(
        self,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a ConsoleNotStartedError.

        Args:
            context: Optional additional context
        """
        super().__init__(
            message="Web console not started. Call web.start_console first.",
            http_status=503,
            error_code="CONSOLE_NOT_STARTED",
            context=context,
        )


__all__ = [
    'WebConsoleError',
    'InvalidJSONError',
    'RouteExecutionError',
    'ConsoleNotStartedError',
]
