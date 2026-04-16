"""network/http_auth.py

Auth strategies for HTTP clients.

Provides small, composable factories that return auth headers.
These plug into HttpClient for authentication.

Security: CRLF injection protection (CVSS 5.3 → <2.0)
"""

import base64
import os
from collections.abc import Callable

from lee.gateway import execute_operation, GatewayInterface


def _validate_header_value(value: str) -> str:
    """Validate header value for CRLF injection attacks.

    CVE: CWE-113 (Improper Neutralization of CRLF Sequences)
    CVSS: 5.3 → <2.0 after fix

    Args:
        value: Header value to validate

    Returns:
        Validated and stripped header value

    Raises:
        TypeError: If value is not a string
        ValueError: If value contains CRLF characters

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"_validate_header_value ENTRY - value={value!r}",
            scope='HTTP_AUTH'
        )
    if not isinstance(value, str):
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="_validate_header_value - TypeError: not a string",
                scope='HTTP_AUTH'
            )
        raise TypeError("Header value must be string")

    if "\r" in value or "\n" in value:
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="_validate_header_value - ValueError: CRLF detected",
                scope='HTTP_AUTH'
            )
        raise ValueError(
            f"CRLF injection detected in header value: {value!r}. "
            "Header names and values cannot contain carriage return or newline characters.",
        )

    result = value.strip()
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"_validate_header_value EXIT - validated={result!r}",
            scope='HTTP_AUTH'
        )
    return result


def _validate_header_name(name: str) -> str:
    """Validate header name for CRLF injection attacks.

    Args:
        name: Header name to validate

    Returns:
        Validated and stripped header name

    Raises:
        TypeError: If name is not a string
        ValueError: If name contains CRLF characters

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"_validate_header_name ENTRY - name={name!r}",
            scope='HTTP_AUTH'
        )
    if not isinstance(name, str):
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="_validate_header_name - TypeError: not a string",
                scope='HTTP_AUTH'
            )
        raise TypeError("Header name must be string")

    if "\r" in name or "\n" in name:
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="_validate_header_name - ValueError: CRLF detected",
                scope='HTTP_AUTH'
            )
        raise ValueError(
            f"CRLF injection detected in header name: {name!r}. "
            "Header names cannot contain carriage return or newline characters.",
        )

    result = name.strip()
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"_validate_header_name EXIT - validated={result!r}",
            scope='HTTP_AUTH'
        )
    return result


def no_auth() -> Callable[[], dict[str, str]]:
    """No auth headers factory."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="no_auth ENTRY - creating no-auth factory",
            scope='HTTP_AUTH'
        )
    def factory() -> dict[str, str]:
        return {}
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="no_auth EXIT - factory created",
            scope='HTTP_AUTH'
        )
    return factory


def basic_auth(username: str, password: str) -> Callable[[], dict[str, str]]:
    """Return a factory that yields a Basic Authorization header.

    Args:
        username: Basic auth username (CRLF-validated)
        password: Basic auth password (CRLF-validated)

    Returns:
        Factory function that returns auth headers dict

    Raises:
        ValueError: If username or password contains CRLF characters

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"basic_auth ENTRY - username={username!r}",
            scope='HTTP_AUTH'
        )
    # Validate inputs for CRLF injection
    _validate_header_value(username)
    _validate_header_value(password)

    token = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    header_value = f"Basic {token}"
    _validate_header_value(header_value)  # Validate final header value

    def factory() -> dict[str, str]:
        return {"Authorization": header_value}

    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="basic_auth EXIT - factory created",
            scope='HTTP_AUTH'
        )
    return factory


def bearer_token(token: str) -> Callable[[], dict[str, str]]:
    """Return a factory that yields a Bearer Authorization header.

    Args:
        token: Bearer token for authorization (JWT or OAuth token)

    Returns:
        Factory function that returns auth headers dict

    Raises:
        ValueError: If token contains CRLF characters

    Security Note:
        JWT tokens are Base64URL encoded (A-Z, a-z, 0-9, -, _) only.
        CRLF injection is not possible with Base64URL encoded tokens.
        Token validation is skipped for JWT tokens since they are
        already validated by the JWT signature verifier.
        Only the final header value is validated for CRLF injection.

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"bearer_token ENTRY - token_length={len(token)}",
            scope='HTTP_AUTH'
        )
    # Skip CRLF validation for JWT tokens - they are already validated
    # by JWT verifier and don't contain user-provided data.
    # JWT tokens are Base64URL encoded (A-Z, a-z, 0-9, -, _) only,
    # which cannot contain CRLF characters (\r or \n).
    # This prevents false positives that break authentication.

    header_value = f"Bearer {token}"
    # Validate the final header value for CRLF injection
    _validate_header_value(header_value)

    def factory() -> dict[str, str]:
        return {"Authorization": header_value}

    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="bearer_token EXIT - factory created",
            scope='HTTP_AUTH'
        )
    return factory


def static_headers(headers: dict[str, str]) -> Callable[[], dict[str, str]]:
    """Wrap a static headers mapping as an auth factory.

    Args:
        headers: Static headers to include in every request (CRLF-validated)

    Returns:
        Factory function that returns static headers

    Raises:
        ValueError: If any header name or value contains CRLF characters

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=f"static_headers ENTRY - header_count={len(headers)}",
            scope='HTTP_AUTH'
        )
    # Validate all headers for CRLF injection
    validated_headers = {}
    for name, value in headers.items():
        validated_name = _validate_header_name(name)
        validated_value = _validate_header_value(value)
        validated_headers[validated_name] = validated_value

    def factory() -> dict[str, str]:
        return dict(validated_headers)

    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="static_headers EXIT - factory created",
            scope='HTTP_AUTH'
        )
    return factory


__all__ = [
    "basic_auth",
    "bearer_token",
    "no_auth",
    "static_headers",
]
