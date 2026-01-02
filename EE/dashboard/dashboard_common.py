"""Dashboard Common Module for EE.

This module provides common error handling and utilities for the Dashboard
Domain Gateway in EE.

Architecture Layer: Domain Gateway - Dashboard Domain - Core Infrastructure

Based on:
    D:\\Code\\Project\\Gateway\\Web\\web_common.py

Integration:
    - Extends GatewayError from gateway_common
    - Provides Dashboard-specific error types
    - Used across all Dashboard gateway components
"""

from __future__ import annotations

class DashboardError(Exception):
    """Base error for Dashboard gateway failures in EE.

    This error class represents all failures that occur within the Dashboard
    Domain Gateway, including server startup errors, request handling errors,
    response building errors, and template rendering errors.

    Attributes:
        message: Human-readable error description
        error_code: Error code (default: "DASHBOARD_ERROR")
        context: Optional error context (request info, endpoint details, etc.)
        source: Source component (default: "DashboardGateway")

    Example:
        >>> raise DashboardError(
        ...     message="Failed to start dashboard server",
        ...     context={"port": 8080, "host": "127.0.0.1"}
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DASHBOARD_ERROR",
        context: dict | None = None,
        source: str = "DashboardGateway",
    ) -> None:
        """Initialize a DashboardError.

        Args:
            message: Human-readable error description
            error_code: Error code for categorization (default: "DASHBOARD_ERROR")
            context: Optional dictionary with error context
            source: Source component name (default: "DashboardGateway")

        Example:
            >>> raise DashboardError(
            ...     message="Failed to handle request",
            ...     error_code="REQUEST_HANDLER_ERROR",
            ...     context={"path": "/exec/test", "method": "POST"}
            ... )
        """
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            source=source,
        )


class DashboardServerError(DashboardError):
    """Error raised when Dashboard server operations fail.

    This error is raised for failures related to server lifecycle operations,
    such as server startup, shutdown, port binding errors, and socket errors.

    Attributes:
        message: Human-readable error description
        host: Server host address
        port: Server port number
        context: Optional additional error context

    Example:
        >>> raise DashboardServerError(
        ...     message="Port already in use",
        ...     host="127.0.0.1",
        ...     port=8080
        ... )
    """

    def __init__(
        self,
        message: str,
        host: str = "unknown",
        port: int = 0,
        context: dict | None = None,
    ) -> None:
        """Initialize a DashboardServerError.

        Args:
            message: Human-readable error description
            host: Server host address (default: "unknown")
            port: Server port number (default: 0)
            context: Optional additional error context

        Example:
            >>> raise DashboardServerError(
            ...     message="Failed to bind to port",
            ...     host="0.0.0.0",
            ...     port=8080,
            ...     context={"error_code": "EADDRINUSE"}
            ... )
        """
        server_context = {
            "host": host,
            "port": port,
        }
        if context:
            server_context.update(context)

        super().__init__(
            message=message,
            error_code="DASHBOARD_SERVER_ERROR",
            context=server_context,
            source="DashboardServer",
        )


class DashboardRequestError(DashboardError):
    """Error raised when Dashboard request processing fails.

    This error is raised for failures related to HTTP request handling,
    such as invalid JSON, malformed requests, unsupported methods, and
    endpoint not found errors.

    Attributes:
        message: Human-readable error description
        method: HTTP method (GET, POST, etc.)
        path: Request path
        context: Optional additional error context

    Example:
        >>> raise DashboardRequestError(
        ...     message="Invalid JSON in request body",
        ...     method="POST",
        ...     path="/exec/test"
        ... )
    """

    def __init__(
        self,
        message: str,
        method: str = "unknown",
        path: str = "/",
        context: dict | None = None,
    ) -> None:
        """Initialize a DashboardRequestError.

        Args:
            message: Human-readable error description
            method: HTTP method (default: "unknown")
            path: Request path (default: "/")
            context: Optional additional error context

        Example:
            >>> raise DashboardRequestError(
            ...     message="Endpoint not found",
            ...     method="GET",
            ...     path="/unknown/endpoint",
            ...     context={"available_endpoints": ["/", "/list-all"]}
            ... )
        """
        request_context = {
            "method": method,
            "path": path,
        }
        if context:
            request_context.update(context)

        super().__init__(
            message=message,
            error_code="DASHBOARD_REQUEST_ERROR",
            context=request_context,
            source="DashboardHandler",
        )


__all__ = [
    'DashboardError',
    'DashboardServerError',
    'DashboardRequestError',
]
