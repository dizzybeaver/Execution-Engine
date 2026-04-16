# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract HTTP handlers from ha_interconnect.py

"""http_handlers.py - HTTP Method Dispatch Handlers
Version: 2025-03-02_1
Purpose: HTTP method handlers for Home Assistant API calls

This module provides O(1) dispatch for HTTP methods.

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

from typing import Any


def _http_method_get(http, endpoint: str, _data: Any, **kwargs) -> Any:
    """Handler for GET requests."""
    return http.get(endpoint, **kwargs)


def _http_method_post(http, endpoint: str, data: Any, **kwargs) -> Any:
    """Handler for POST requests."""
    return http.post(endpoint, data=data, **kwargs)


def _http_method_put(http, endpoint: str, data: Any, **kwargs) -> Any:
    """Handler for PUT requests."""
    return http.put(endpoint, data=data, **kwargs)


def _http_method_delete(http, endpoint: str, _data: Any, **_kwargs) -> Any:
    """Handler for DELETE requests."""
    return http.delete(endpoint)


# Dispatch dictionary for HTTP methods (O(1) lookup)
HTTP_METHOD_HANDLERS = {
    "GET": _http_method_get,
    "POST": _http_method_post,
    "PUT": _http_method_put,
    "DELETE": _http_method_delete,
}


__all__ = [
    "HTTP_METHOD_HANDLERS",
    "_http_method_get",
    "_http_method_post",
    "_http_method_put",
    "_http_method_delete",
]
