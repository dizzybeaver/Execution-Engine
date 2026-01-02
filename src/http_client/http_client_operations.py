"""
http_client/http_client_operations.py
Version: 2025-12-10_1
Purpose: HTTP client gateway operation implementations
License: Apache 2.0
"""

from typing import Dict, Any

from http_client.http_client_manager import get_http_client_manager


def _make_http_request(method: str, url: str, correlation_id: str = None,
                      **kwargs) -> Dict[str, Any]:
    """Execute HTTP request via singleton."""
    client = get_http_client_manager()
    return client.make_request(method, url, correlation_id, **kwargs)


def http_request_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP request."""
    method = kwargs.pop('method', 'GET')
    url = kwargs.pop('url', '')
    correlation_id = kwargs.pop('correlation_id', None)
    return _make_http_request(method, url, correlation_id, **kwargs)


def http_get_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP GET."""
    url = kwargs.pop('url', '')
    correlation_id = kwargs.pop('correlation_id', None)
    return _make_http_request('GET', url, correlation_id, **kwargs)


def http_post_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP POST."""
    url = kwargs.pop('url', '')
    correlation_id = kwargs.pop('correlation_id', None)
    return _make_http_request('POST', url, correlation_id, **kwargs)


def http_put_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP PUT."""
    url = kwargs.pop('url', '')
    correlation_id = kwargs.pop('correlation_id', None)
    return _make_http_request('PUT', url, correlation_id, **kwargs)


def http_delete_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP DELETE."""
    url = kwargs.pop('url', '')
    correlation_id = kwargs.pop('correlation_id', None)
    return _make_http_request('DELETE', url, correlation_id, **kwargs)


def http_reset_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP client reset."""
    client = get_http_client_manager()
    success = client.reset()
    return {
        'success': success,
        'message': 'HTTP client reset successful' if success else 'HTTP client reset failed'
    }


def get_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for get state."""
    from http_client.http_client_state import get_client_state
    return get_client_state(**kwargs)


def reset_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for reset state."""
    from http_client.http_client_state import reset_client_state
    return reset_client_state(**kwargs)


__all__ = [
    'http_request_implementation',
    'http_get_implementation',
    'http_post_implementation',
    'http_put_implementation',
    'http_delete_implementation',
    'http_reset_implementation',
    'get_state_implementation',
    'reset_state_implementation',
]
