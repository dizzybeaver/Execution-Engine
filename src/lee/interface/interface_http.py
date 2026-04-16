# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interfaces/interface_http.py
Version: 2026-04-11_2
Purpose: HTTP interface router with Static DDS
License: Apache 2.0
"""

from typing import Any

from lee.interface.interface_common import validate_module_available
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.network.http_operations')
def _import_http():
    from lee.network.http_operations import (
        configure_retry_implementation,
        get_state_implementation,
        get_statistics_implementation,
        http_delete_implementation,
        http_get_implementation,
        http_post_implementation,
        http_put_implementation,
        http_request_implementation,
        http_reset_implementation,
        reset_state_implementation,
    )
    return {
        'configure_retry': configure_retry_implementation,
        'get_state': get_state_implementation,
        'get_statistics': get_statistics_implementation,
        'http_delete': http_delete_implementation,
        'http_get': http_get_implementation,
        'http_post': http_post_implementation,
        'http_put': http_put_implementation,
        'http_request': http_request_implementation,
        'http_reset': http_reset_implementation,
        'reset_state': reset_state_implementation,
    }


_http_funcs = _import_http()
_HTTP_AVAILABLE = _import_http.__dict__.get('_HTTP_AVAILABLE', False)
_HTTP_IMPORT_ERROR = _import_http.__dict__.get('_HTTP_IMPORT_ERROR', None)

if _HTTP_AVAILABLE:
    configure_retry_implementation = _http_funcs['configure_retry']
    get_state_implementation = _http_funcs['get_state']
    get_statistics_implementation = _http_funcs['get_statistics']
    http_delete_implementation = _http_funcs['http_delete']
    http_get_implementation = _http_funcs['http_get']
    http_post_implementation = _http_funcs['http_post']
    http_put_implementation = _http_funcs['http_put']
    http_request_implementation = _http_funcs['http_request']
    http_reset_implementation = _http_funcs['http_reset']
    reset_state_implementation = _http_funcs['reset_state']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        return {"success": False, "error": "HTTP module unavailable"}

    configure_retry_implementation = _stub_unavailable
    get_state_implementation = _stub_unavailable
    get_statistics_implementation = _stub_unavailable
    http_delete_implementation = _stub_unavailable
    http_get_implementation = _stub_unavailable
    http_post_implementation = _stub_unavailable
    http_put_implementation = _stub_unavailable
    http_request_implementation = _stub_unavailable
    http_reset_implementation = _stub_unavailable
    reset_state_implementation = _stub_unavailable


def _validate_url_param(kwargs: dict[str, Any], operation: str) -> None:
    """Validate url parameter exists and is string."""
    if "url" not in kwargs:
        raise ValueError(f"http.{operation} requires 'url' parameter")
    if not isinstance(kwargs["url"], str):
        raise TypeError(
            f"http.{operation} 'url' must be str, got {type(kwargs['url']).__name__}",
        )


def _validate_request_params(kwargs: dict[str, Any]) -> None:
    """Validate request operation parameters."""
    if "url" not in kwargs:
        raise ValueError("http.request requires 'url' parameter")
    if "method" not in kwargs:
        raise ValueError("http.request requires 'method' parameter")
    if not isinstance(kwargs["url"], str):
        raise TypeError(
            f"http.request 'url' must be str, got {type(kwargs['url']).__name__}",
        )
    if not isinstance(kwargs["method"], str):
        raise TypeError(
            f"http.request 'method' must be str, got {type(kwargs['method']).__name__}",
        )


# Wrapper functions to replace lambda tuple-trick
def _request_wrapper(**kwargs) -> Any:
    """Wrapper for request operation with validation."""
    _validate_request_params(kwargs)
    return http_request_implementation(**kwargs)


def _get_wrapper(**kwargs) -> Any:
    """Wrapper for get operation with validation."""
    _validate_url_param(kwargs, "get")
    return http_get_implementation(**kwargs)


def _post_wrapper(**kwargs) -> Any:
    """Wrapper for post operation with validation."""
    _validate_url_param(kwargs, "post")
    return http_post_implementation(**kwargs)


def _put_wrapper(**kwargs) -> Any:
    """Wrapper for put operation with validation."""
    _validate_url_param(kwargs, "put")
    return http_put_implementation(**kwargs)


def _delete_wrapper(**kwargs) -> Any:
    """Wrapper for delete operation with validation."""
    _validate_url_param(kwargs, "delete")
    return http_delete_implementation(**kwargs)


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for HTTP operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category (read/write/delete/admin)
    - description: Human-readable description
    """
    return {
        "request": {
            "func": _request_wrapper,
            "category": "write",
            "description": "Execute HTTP request with custom method",
        },
        "get": {
            "func": _get_wrapper,
            "category": "read",
            "description": "Execute HTTP GET request",
        },
        "post": {
            "func": _post_wrapper,
            "category": "write",
            "description": "Execute HTTP POST request",
        },
        "put": {
            "func": _put_wrapper,
            "category": "write",
            "description": "Execute HTTP PUT request",
        },
        "delete": {
            "func": _delete_wrapper,
            "category": "delete",
            "description": "Execute HTTP DELETE request",
        },
        "reset": {
            "func": http_reset_implementation,
            "category": "delete",
            "description": "Reset HTTP client statistics",
        },
        "get_state": {
            "func": get_state_implementation,
            "category": "read",
            "description": "Get HTTP client state and statistics",
        },
        "reset_state": {
            "func": reset_state_implementation,
            "category": "delete",
            "description": "Reset HTTP client state",
        },
        "configure_retry": {
            "func": configure_retry_implementation,
            "category": "admin",
            "description": "Configure retry policy",
        },
        "get_statistics": {
            "func": get_statistics_implementation,
            "category": "read",
            "description": "Get HTTP request statistics",
        },
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _HTTP_AVAILABLE else {}


def execute_http_operation(operation: str, **kwargs) -> Any:
    """Route HTTP operation requests using enhanced dispatch dictionary pattern.

    Args:
        operation: HTTP operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If HTTP interface unavailable
        ValueError: If operation unknown or parameters invalid

    """
    validate_module_available("http", _HTTP_AVAILABLE, _HTTP_IMPORT_ERROR)

    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown HTTP operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}",
        )

    entry = _OPERATION_DISPATCH[operation]
    func = entry["func"]
    return func(**kwargs)


__all__ = ["execute_http_operation"]
