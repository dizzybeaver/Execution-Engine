"""
Web Response Module - EE Web Domain Gateway

This module provides HTTP response building for the Web domain gateway.
It handles JSON serialization, status codes, and response formatting.

Architecture Layer: Layer 1 - Domain Gateway Infrastructure
Part of: Web Domain Gateway (gateway.web)

Based on: D:\\Code\\Project\\Gateway\\Web\\web_response.py
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from EE.web.web_common import WebConsoleError


@dataclass
class WebResponse:
    """HTTP response for the EE Web Console.

    This dataclass represents an HTTP response with status code,
    body, and headers. It provides methods for serialization to
    HTTP format.

    Attributes:
        status: HTTP status code (200, 400, 500, etc.)
        body: Response body as dictionary (will be JSON serialized)
        headers: Optional additional HTTP headers

    Example:
        >>> response = success_response({"data": "value"})
        >>> print(response.status)  # 200
        >>> print(response.to_http())  # b'{"data": "value"}'
    """

    status: int
    body: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None

    def to_http(self) -> bytes:
        """Convert response to HTTP body bytes.

        Serializes the body dictionary to JSON with proper formatting.

        Returns:
            Response body as bytes (UTF-8 encoded JSON)

        Example:
            >>> response = WebResponse(status=200, body={"key": "value"})
            >>> body_bytes = response.to_http()
            >>> isinstance(body_bytes, bytes)
            True
        """
        return json.dumps(self.body, indent=2, ensure_ascii=False).encode("utf-8")

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary representation.

        Returns:
            Dictionary with response information including status and body
        """
        return {
            "status": self.status,
            "body": self.body,
            "headers": self.headers or {},
        }

    def is_success(self) -> bool:
        """Check if response indicates success.

        Returns:
            True if status code is 2xx
        """
        return 200 <= self.status < 300

    def is_error(self) -> bool:
        """Check if response indicates error.

        Returns:
            True if status code is 4xx or 5xx
        """
        return self.status >= 400


def success_response(
    body: Dict[str, Any],
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> WebResponse:
    """Create a successful HTTP response.

    Args:
        body: Response body as dictionary
        status: HTTP status code (default: 200)
        headers: Optional additional HTTP headers

    Returns:
        WebResponse object with success status

    Example:
        >>> response = success_response({"result": "success"})
        >>> assert response.status == 200
        >>> assert response.body == {"result": "success"}
    """
    return WebResponse(
        status=status,
        body=body,
        headers=headers,
    )


def error_response(
    message: str,
    status: int = 400,
    error_code: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> WebResponse:
    """Create an error HTTP response.

    Args:
        message: Error message
        status: HTTP status code (default: 400)
        error_code: Optional error code for categorization
        context: Optional error context

    Returns:
        WebResponse object with error status and formatted error body

    Example:
        >>> response = error_response("Invalid input", status=400)
        >>> assert response.status == 400
        >>> assert "error" in response.body
    """
    error_body = {
        "error": message,
    }

    if error_code:
        error_body["error_code"] = error_code

    if context:
        error_body["context"] = context

    return WebResponse(
        status=status,
        body=error_body,
    )


def not_found_response(
    resource_type: str,
    resource_id: str,
    available_resources: Optional[list] = None,
) -> WebResponse:
    """Create a not found error response.

    Args:
        resource_type: Type of resource (e.g., "route", "domain")
        resource_id: ID of the resource that was not found
        available_resources: Optional list of available resources

    Returns:
        WebResponse object with 404 status

    Example:
        >>> response = not_found_response("route", "unknown.route")
        >>> assert response.status == 404
        >>> assert "not found" in response.body["error"].lower()
    """
    message = f"{resource_type.capitalize()} not found: {resource_id}"

    context = {
        "resource_type": resource_type,
        "resource_id": resource_id,
    }

    if available_resources:
        context["available_resources"] = available_resources

    return error_response(
        message=message,
        status=404,
        error_code="NOT_FOUND",
        context=context,
    )


def validation_error_response(
    field_name: str,
    message: str,
    validation_errors: Optional[Dict[str, Any]] = None,
) -> WebResponse:
    """Create a validation error response.

    Args:
        field_name: Name of the field that failed validation
        message: Validation error message
        validation_errors: Optional dictionary of validation errors

    Returns:
        WebResponse object with 422 status

    Example:
        >>> response = validation_error_response("email", "Invalid email format")
        >>> assert response.status == 422
        >>> assert response.body["error_code"] == "VALIDATION_ERROR"
    """
    context = {
        "field_name": field_name,
    }

    if validation_errors:
        context["validation_errors"] = validation_errors

    return error_response(
        message=message,
        status=422,
        error_code="VALIDATION_ERROR",
        context=context,
    )


def server_error_response(
    message: str,
    original_error: Optional[Exception] = None,
) -> WebResponse:
    """Create a server error response.

    Args:
        message: Error message
        original_error: Optional original exception

    Returns:
        WebResponse object with 500 status

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     response = server_error_response("Operation failed", e)
    """
    context = {}

    if original_error:
        context["original_error_type"] = type(original_error).__name__
        context["original_error_message"] = str(original_error)

    return error_response(
        message=message,
        status=500,
        error_code="INTERNAL_SERVER_ERROR",
        context=context,
    )


__all__ = [
    'WebResponse',
    'success_response',
    'error_response',
    'not_found_response',
    'validation_error_response',
    'server_error_response',
]
