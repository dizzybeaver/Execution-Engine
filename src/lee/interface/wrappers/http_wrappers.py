"""gateway/wrappers/gateway_wrappers_http_client.py
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Fixed: 2026-03-17 (Remove self-referential gateway calls)
Purpose: HTTP_CLIENT interface wrappers
License: Apache 2.0

CHANGES:
- 2026.04.11: Consolidated with base_wrapper, removed duplicate patterns
- 2026.03.17: Fixed self-referential gateway calls (call implementations directly)
- 2025.12.13_1: Fixed import path from gateway_core (not gateway.gateway_core)
"""

from typing import Any

from lee.network.http_operations import (
    get_state_implementation,
    http_delete_implementation,
    http_get_implementation,
    http_post_implementation,
    http_put_implementation,
    http_request_implementation,
    http_reset_implementation,
    reset_state_implementation,
)


def http_request(method: str, url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP request with specified method.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Target URL
        **kwargs: Additional parameters (headers, json, body, timeout, correlation_id)

    Returns:
        Dict with success status, data, and metadata

    """
    return http_request_implementation(method=method, url=url, **kwargs)


def http_get(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP GET request.

    Args:
        url: Target URL
        **kwargs: Additional parameters (headers, timeout, correlation_id)

    Returns:
        Dict with success status, data, and metadata

    """
    return http_get_implementation(url=url, **kwargs)


def http_post(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP POST request.

    Args:
        url: Target URL
        **kwargs: Additional parameters (json, body, headers, timeout, correlation_id)

    Returns:
        Dict with success status, data, and metadata

    """
    return http_post_implementation(url=url, **kwargs)


def http_put(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP PUT request.

    Args:
        url: Target URL
        **kwargs: Additional parameters (json, body, headers, timeout, correlation_id)

    Returns:
        Dict with success status, data, and metadata

    """
    return http_put_implementation(url=url, **kwargs)


def http_delete(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP DELETE request.

    Args:
        url: Target URL
        **kwargs: Additional parameters (headers, timeout, correlation_id)

    Returns:
        Dict with success status, data, and metadata

    """
    return http_delete_implementation(url=url, **kwargs)


def http_reset() -> dict[str, Any]:
    """Reset HTTP client state.

    Resets:
    - Connection pool (closes all connections)
    - Statistics counters
    - Rate limiter state

    Returns:
        Dict with success status and reset confirmation

    """
    return http_reset_implementation()


def http_get_state(**kwargs) -> dict[str, Any]:
    """Get HTTP client state.

    Returns:
        Dict with client state information

    """
    return get_state_implementation(**kwargs)


def http_reset_state(**kwargs) -> dict[str, Any]:
    """Reset HTTP client state (legacy operation).

    Returns:
        Dict with reset status

    """
    return reset_state_implementation(**kwargs)


__all__ = [
    "http_delete",
    "http_get",
    "http_get_state",
    "http_post",
    "http_put",
    "http_request",
    "http_reset",
    "http_reset_state",
]
