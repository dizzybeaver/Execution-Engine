"""
Web Request Module - EE Web Domain Gateway

This module provides HTTP request parsing and validation for the Web domain gateway.
It handles JSON body parsing, route extraction, and request validation.

Architecture Layer: Layer 1 - Domain Gateway Infrastructure
Part of: Web Domain Gateway (gateway.web)

Based on: D:\\Code\\Project\\Gateway\\Web\\web_request.py
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from EE.web.web_common import WebConsoleError, InvalidJSONError


@dataclass
class WebRequest:
    """Parsed HTTP request for the EE Web Console.

    This dataclass represents a parsed HTTP request with all necessary
    information for routing and execution through the gateway system.

    Attributes:
        method: HTTP method (GET, POST, etc.)
        path: Request path (e.g., "/exec/config.get")
        route: Extracted route for execution (e.g., "config.get")
        payload: Parsed JSON payload as dictionary
        query_params: Optional query parameters from URL

    Example:
        >>> request = WebRequest.parse("POST", "/exec/config.get", body)
        >>> print(request.route)  # "config.get"
        >>> print(request.payload)  # {"key": "database.host"}
    """

    method: str
    path: str
    route: Optional[str]
    payload: Dict[str, Any]
    query_params: Optional[Dict[str, str]] = None

    @staticmethod
    def parse(method: str, path: str, body: bytes) -> "WebRequest":
        """Parse an HTTP request into a WebRequest object.

        This method validates the HTTP request, extracts the route,
        and parses the JSON body.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body as bytes

        Returns:
            Parsed WebRequest object

        Raises:
            InvalidJSONError: If JSON body is invalid
            WebConsoleError: If request parsing fails

        Example:
            >>> body = b'{"key": "database.host"}'
            >>> request = WebRequest.parse("POST", "/exec/config.get", body)
            >>> assert request.route == "config.get"
            >>> assert request.payload == {"key": "database.host"}
        """
        try:
            # Extract route from path
            route = WebRequest._extract_route(path)

            # Parse JSON body
            payload = {}
            if body:
                try:
                    payload = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError as e:
                    raise InvalidJSONError(
                        message=f"Invalid JSON body: {e}",
                        context={"body_preview": body[:100].decode("utf-8", errors="ignore")},
                    ) from e

            # Validate payload is a dictionary
            if payload and not isinstance(payload, dict):
                raise WebConsoleError(
                    message="JSON payload must be an object/dictionary",
                    http_status=400,
                    error_code="INVALID_PAYLOAD_TYPE",
                    context={"payload_type": type(payload).__name__},
                )

            return WebRequest(
                method=method.upper(),
                path=path,
                route=route,
                payload=payload,
            )

        except WebConsoleError:
            # Re-raise WebConsoleError as-is
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise WebConsoleError(
                message=f"Failed to parse request: {e}",
                http_status=500,
                error_code="REQUEST_PARSE_ERROR",
                context={"exception_type": type(e).__name__},
            ) from e

    @staticmethod
    def _extract_route(path: str) -> Optional[str]:
        """Extract route from request path.

        Args:
            path: Request path

        Returns:
            Extracted route or None if not an execution path

        Example:
            >>> _extract_route("/exec/config.get")
            'config.get'
            >>> _extract_route("/list-all")
            None
        """
        # Check if path is an execution path
        if path.startswith("/exec/"):
            route = path[len("/exec/") :]
            # Remove query string if present
            if "?" in route:
                route = route.split("?")[0]
            return route

        # Check for other special paths
        if path.startswith("/exec-domain/"):
            # Format: /exec-domain/{domain}/{operation}
            rest = path[len("/exec-domain/") :]
            parts = rest.split("/", 1)
            if len(parts) == 2:
                return f"{parts[0]}.{parts[1]}"

        return None

    def validate(self) -> None:
        """Validate the parsed request.

        Raises:
            WebConsoleError: If request is invalid
        """
        if not self.method:
            raise WebConsoleError(
                message="HTTP method is required",
                http_status=400,
                error_code="MISSING_METHOD",
            )

        if not self.path:
            raise WebConsoleError(
                message="Request path is required",
                http_status=400,
                error_code="MISSING_PATH",
            )

        # Validate execution requests have a route
        if self.path.startswith("/exec") and not self.route:
            raise WebConsoleError(
                message="Execution request must have a route",
                http_status=400,
                error_code="MISSING_ROUTE",
                context={"path": self.path},
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary representation.

        Returns:
            Dictionary with request information
        """
        return {
            "method": self.method,
            "path": self.path,
            "route": self.route,
            "payload": self.payload,
            "query_params": self.query_params,
        }


__all__ = [
    'WebRequest',
]
