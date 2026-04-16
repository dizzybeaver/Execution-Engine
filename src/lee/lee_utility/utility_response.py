"""utility_response.py - Response Formatting (Internal)
Version: 2025.10.18.01 - RECURSION FIX
Description: Response formatting methods for success/error responses and Lambda responses

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import logging
import os
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.lee_utility.utility_types import (
    DEFAULT_HEADERS_DICT,
    DEFAULT_HEADERS_JSON,
    EMPTY_DATA,
    ERROR_WITH_CODE,
    ERROR_WITH_CORRELATION,
    LAMBDA_RESPONSE,
    SUCCESS_TEMPLATE,
    SUCCESS_WITH_CORRELATION,
)

logger = logging.getLogger(__name__)

# Runtime configuration
_USE_TEMPLATES = os.environ.get("USE_JSON_TEMPLATES", "true").lower() == "true"


# ===== HELPER FUNCTIONS =====

def _sanitize_for_json(obj: Any, max_depth: int = 10) -> Any:
    """Sanitize object for JSON serialization.
    Converts tuples to lists, removes non-JSON-serializable keys.
    """
    if max_depth <= 0:
        return str(obj)[:100]  # Prevent infinite recursion

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item, max_depth - 1) for item in obj]

    if isinstance(obj, dict):
        sanitized = {}
        for key, value in obj.items():
            # Convert tuple keys to strings
            if isinstance(key, tuple) or not isinstance(key, (str, int, float, bool)):
                key = str(key)

            sanitized[key] = _sanitize_for_json(value, max_depth - 1)
        return sanitized

    # For other types, convert to string
    return str(obj)


def _safe_json_dumps(obj: Any) -> str:
    """Safely convert object to JSON string using gateway."""
    try:
        # First attempt normal JSON serialization via gateway
        return execute_operation(GatewayInterface.UTILITY, "json_dumps", obj=obj)
    except (TypeError, ValueError):
        # If that fails, sanitize and try again
        try:
            sanitized = _sanitize_for_json(obj)
            return execute_operation(GatewayInterface.UTILITY, "json_dumps", obj=sanitized)
        except (AttributeError, KeyError, RuntimeError) as inner_e:
            # Last resort: return string representation
            logger.error("JSON serialization failed even after sanitization: %s", inner_e)
            return execute_operation(
                GatewayInterface.UTILITY,
                "json_dumps",
                obj={"error": "Serialization failed", "details": str(obj)[:200]},
            )


# ===== RESPONSE FORMATTING =====

class ResponseFormatter:
    """Response formatting utilities for Lambda and API responses."""

    @staticmethod
    def format_response_fast(status_code: int, body: Any,
                           headers: Optional[str] = None) -> dict:
        """Fast Lambda response formatting using template."""
        try:
            # Use safe JSON dumps to handle problematic data
            body_json = body if isinstance(body, str) else _safe_json_dumps(body)
            headers_json = headers or DEFAULT_HEADERS_JSON

            json_str = LAMBDA_RESPONSE % (status_code, body_json, headers_json)
            return execute_operation(GatewayInterface.UTILITY, "json_loads", json_string=json_str)
        except (ValueError, TypeError, KeyError) as e:
            logger.error("Fast response formatting error: %s", e)
            # CRITICAL FIX: Use _format_response_fallback instead of recursing
            return ResponseFormatter._format_response_fallback(status_code, body)

    @staticmethod
    def _format_response_fallback(status_code: int, body: Any) -> dict:
        """Fallback response formatter that NEVER calls format_response_fast.
        Breaks the recursion cycle.
        """
        try:
            # Sanitize body for JSON
            sanitized_body = _sanitize_for_json(body)

            return {
                "statusCode": status_code,
                "body": _safe_json_dumps(sanitized_body),
                "headers": DEFAULT_HEADERS_DICT,
            }
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error("Fallback response formatting error: %s", e)
            # Absolute last resort - hardcoded safe response
            return {
                "statusCode": 500,
                "body": '{"error": "Response formatting failed completely"}',
                "headers": DEFAULT_HEADERS_DICT,
            }

    @staticmethod
    def format_response(status_code: int, body: Any, headers: Optional[dict] = None) -> dict:
        """Format Lambda response (standard path)."""
        # Use fast path only if headers are default/None AND templates enabled
        if _USE_TEMPLATES and (headers is None or headers == DEFAULT_HEADERS_DICT):
            return ResponseFormatter.format_response_fast(status_code, body)

        try:
            # Sanitize body for JSON
            sanitized_body = _sanitize_for_json(body)

            return {
                "statusCode": status_code,
                "body": _safe_json_dumps(sanitized_body),
                "headers": headers or DEFAULT_HEADERS_DICT,
            }
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error("Response formatting error: %s", e)
            # Use fallback instead of recursing
            return ResponseFormatter._format_response_fallback(status_code, body)

    @staticmethod
    def create_success_response(message: str, data: Any = None,
                               correlation_id: Optional[str] = None) -> dict[str, Any]:
        """Create success response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = execute_operation(GatewayInterface.UTILITY, "get_timestamp")
                # Sanitize data before JSON conversion
                sanitized_data = _sanitize_for_json(data) if data is not None else None
                data_json = _safe_json_dumps(sanitized_data) if sanitized_data is not None else EMPTY_DATA

                if correlation_id:
                    json_str = SUCCESS_WITH_CORRELATION % (message, timestamp, data_json, correlation_id)
                else:
                    json_str = SUCCESS_TEMPLATE % (message, timestamp, data_json)

                return execute_operation(GatewayInterface.UTILITY, "json_loads", json_string=json_str)

            # Standard path
            response = {
                "success": True,
                "message": message,
                "timestamp": execute_operation(GatewayInterface.UTILITY, "get_timestamp"),
            }

            if data is not None:
                response["data"] = _sanitize_for_json(data)

            if correlation_id:
                response["correlation_id"] = correlation_id

            return response

        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error("Success response creation error: %s", e)
            return {
                "success": True,
                "message": message,
                "timestamp": execute_operation(GatewayInterface.UTILITY, "get_timestamp"),
            }

    @staticmethod
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                             details: Any = None, correlation_id: Optional[str] = None) -> dict[str, Any]:
        """Create error response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = execute_operation(GatewayInterface.UTILITY, "get_timestamp")
                # Sanitize details before JSON conversion
                sanitized_details = _sanitize_for_json(details) if details is not None else None
                details_json = _safe_json_dumps(sanitized_details) if sanitized_details is not None else EMPTY_DATA

                if correlation_id:
                    json_str = ERROR_WITH_CORRELATION % (message, error_code, timestamp, details_json, correlation_id)
                else:
                    json_str = ERROR_WITH_CODE % (message, error_code, timestamp, details_json)

                return execute_operation(GatewayInterface.UTILITY, "json_loads", json_string=json_str)

            # Standard path
            response = {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": execute_operation(GatewayInterface.UTILITY, "get_timestamp"),
            }

            if details is not None:
                response["details"] = _sanitize_for_json(details)

            if correlation_id:
                response["correlation_id"] = correlation_id

            return response

        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error("Error response creation error: %s", e)
            return {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": execute_operation(GatewayInterface.UTILITY, "get_timestamp"),
            }


# ===== SINGLETON INSTANCE =====

_RESPONSE_FORMATTER = ResponseFormatter()


# ===== PUBLIC FUNCTIONS =====

def format_response_fast(status_code: int, body: Any,
                        headers: Optional[str] = None) -> dict:
    """Fast Lambda response formatting using template."""
    return _RESPONSE_FORMATTER.format_response_fast(status_code, body, headers)


def format_response(status_code: int, body: Any, headers: Optional[dict] = None) -> dict:
    """Format Lambda response."""
    return _RESPONSE_FORMATTER.format_response(status_code, body, headers)


def create_success_response(message: str, data: Any = None,
                           correlation_id: Optional[str] = None) -> dict[str, Any]:
    """Create success response."""
    return _RESPONSE_FORMATTER.create_success_response(message, data, correlation_id)


def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                         details: Any = None, correlation_id: Optional[str] = None) -> dict[str, Any]:
    """Create error response."""
    return _RESPONSE_FORMATTER.create_error_response(message, error_code, details, correlation_id)


# ===== MODULE EXPORTS =====

__all__ = [
    "ResponseFormatter",
    "create_error_response",
    "create_success_response",
    "format_response",
    "format_response_fast",
]

# EOF
