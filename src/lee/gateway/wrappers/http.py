"""HTTP Wrapper Functions

Direct access to HTTP operations (8 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import http

    # GET request
    response = http.get(url='https://api.example.com/data')

    # POST request
    response = http.post(url='https://api.example.com/data', json={'key': 'value'})

    # PUT request
    response = http.put(url='https://api.example.com/data', data='content')

    # DELETE request
    response = http.delete(url='https://api.example.com/data')

    # Get HTTP state
    state = http.get_state()

    # Generic request
    response = http.request(method='GET', url='https://api.example.com')
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def http_get(url: str, **kwargs: Any) -> dict[str, Any]:
    """HTTP GET request.

    Args:
        url: URL to request
        **kwargs: Additional HTTP options

    Returns:
        Response dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get', url=url, **kwargs)


def http_post(url: str, **kwargs: Any) -> dict[str, Any]:
    """HTTP POST request.

    Args:
        url: URL to request
        **kwargs: Additional HTTP options (json, data, etc.)

    Returns:
        Response dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'post', url=url, **kwargs)


def http_put(url: str, **kwargs: Any) -> dict[str, Any]:
    """HTTP PUT request.

    Args:
        url: URL to request
        **kwargs: Additional HTTP options

    Returns:
        Response dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'put', url=url, **kwargs)


def http_delete(url: str, **kwargs: Any) -> dict[str, Any]:
    """HTTP DELETE request.

    Args:
        url: URL to request
        **kwargs: Additional HTTP options

    Returns:
        Response dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'delete', url=url, **kwargs)


def http_request(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    """Generic HTTP request.

    Args:
        method: HTTP method
        url: URL to request
        **kwargs: Additional HTTP options

    Returns:
        Response dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'request', method=method, url=url, **kwargs)


def http_get_state(**kwargs: Any) -> dict[str, Any]:
    """Get HTTP client state.

    Args:
        **kwargs: Additional options

    Returns:
        State dictionary
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get_state', **kwargs)


def http_set_state(state: dict[str, Any], **kwargs: Any) -> None:
    """Set HTTP client state.

    Args:
        state: State dictionary
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.HTTP_CLIENT, 'set_state', state=state, **kwargs)


# Convenience aliases without http_ prefix
get = http_get
post = http_post
put = http_put
delete = http_delete
request = http_request


__all__ = [
    'http_delete',
    'http_get',
    'http_get_state',
    'http_post',
    'http_put',
    'http_request',
    'http_set_state',
    # Convenience aliases
    'get',
    'post',
    'put',
    'delete',
    'request',
]
