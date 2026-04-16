"""http_validation.py

Version: 2026-03-26_1
Purpose: HTTP security validation utilities
License: Apache 2.0

Provides security validation for HTTP operations including CRLF injection prevention.
"""

import os
from typing import Any, Optional

# Security: Translation table for single-pass CRLF removal (faster than chained replace)
_CRLF_REMOVE_TRANS = str.maketrans({'\r': None, '\n': None})

# Debug tracing support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"


def validate_headers(headers: Optional[dict[str, Any]]) -> bool:
    """Validate HTTP headers for CRLF injection prevention.

    Checks that header values do not contain carriage return or linefeed
    characters, which could lead to CRLF injection attacks.

        headers: Dictionary of HTTP headers to validate
        True if headers are safe, False if CRLF sequences detected

    CRLF injection occurs when attacker-controlled data contains \\r\\n characters,
    allowing injection of arbitrary headers or request smuggling.
    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Validating {len(headers) if headers else 0} headers for CRLF injection",
                         scope='HTTP_VALIDATION')
        execute_operation(GatewayInterface.DEBUG, 'timing',
                         operation_name='validate_headers',
                         scope='HTTP_VALIDATION')

    if not headers:
        return True

    for key, value in headers.items():
        if not isinstance(key, str):
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Header key not a string: {type(key)}",
                                 scope='HTTP_VALIDATION')
            return False
        if not isinstance(value, (str, bytes, bytearray)):
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Header value not valid type: {type(value)}",
                                 scope='HTTP_VALIDATION')
            return False

        # Check for CRLF sequences in header names and values
        key_str = key if isinstance(key, str) else key.decode('utf-8', errors='replace')
        value_str = value if isinstance(value, str) else value.decode('utf-8', errors='replace')

        if '\r' in key_str or '\n' in key_str:
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"CRLF detected in header key: {key_str}",
                                 scope='HTTP_VALIDATION')
            return False
        if '\r' in value_str or '\n' in value_str:
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"CRLF detected in header value for key: {key_str}",
                                 scope='HTTP_VALIDATION')
            return False

    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message="All headers validated successfully",
                         scope='HTTP_VALIDATION')

    return True


def sanitize_headers(headers: dict[str, Any]) -> dict[str, str]:
    """Sanitize HTTP headers by removing CRLF sequences.

    Removes any CRLF sequences from header keys and values to prevent
    CRLF injection attacks while preserving as much data as possible.

        headers: Dictionary of HTTP headers to sanitize
        Sanitized dictionary with CRLF sequences removed

    >>> sanitize_headers({'X-Custom': 'value\\r\\nInjected'})
    {'X-Custom': 'valueInjected'}
    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Sanitizing {len(headers) if headers else 0} headers",
                         scope='HTTP_VALIDATION')
        execute_operation(GatewayInterface.DEBUG, 'timing',
                         operation_name='sanitize_headers',
                         scope='HTTP_VALIDATION')

    if not headers:
        return {}

    sanitized = {}
    for key, value in headers.items():
        # Convert to string if needed
        key_str = key if isinstance(key, str) else str(key)
        value_str = value if isinstance(value, str) else str(value)

        # Remove CRLF sequences (single-pass translation)
        safe_key = key_str.translate(_CRLF_REMOVE_TRANS)
        safe_value = value_str.translate(_CRLF_REMOVE_TRANS)

        if _DEBUG_ENABLED and (safe_key != key_str or safe_value != value_str):
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"Sanitized header: {key_str} -> {safe_key}",
                             scope='HTTP_VALIDATION')

        sanitized[safe_key] = safe_value

    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Sanitized {len(sanitized)} headers",
                         scope='HTTP_VALIDATION')

    return sanitized


__all__ = [
    "validate_headers",
    "sanitize_headers",
]
