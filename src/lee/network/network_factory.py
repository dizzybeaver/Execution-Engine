# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-08 - Add LEE_DEBUG tracing

"""network/network_factory.py

Factory for creating HTTP and WebSocket clients with various
authentication options and Home Assistant integration.
"""

import os
from collections.abc import Callable
from typing import Optional

from lee.network.http_auth import basic_auth, bearer_token, no_auth
from lee.network.http_core import HttpClient
from lee.network.ws_core import WebSocketClient

# Debug tracing support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"

AuthType = str  # "none", "basic", "bearer", "custom"


# HTTP auth dispatch handlers (O(1) lookup)
def _http_auth_none(_username, _password, _token, _custom_auth_factory):
    """Handler for none auth type."""
    return no_auth()


def _http_auth_basic(username, password, _token, _custom_auth_factory):
    """Handler for basic auth type."""
    return basic_auth(username, password)


def _http_auth_bearer(_username, _password, token, _custom_auth_factory):
    """Handler for bearer auth type."""
    return bearer_token(token)


def _http_auth_custom(_username, _password, _token, custom_auth_factory):
    """Handler for custom auth type."""
    return custom_auth_factory


# Dispatch dictionary for HTTP auth types (O(1) lookup)
_HTTP_AUTH_DISPATCH = {
    "none": _http_auth_none,
    "basic": _http_auth_basic,
    "bearer": _http_auth_bearer,
    "custom": _http_auth_custom,
}


# WebSocket auth dispatch handlers (O(1) lookup)
def _ws_auth_none(_username, _password, _token, _custom_auth_factory):
    """Handler for none auth type."""
    return no_auth()


def _ws_auth_basic(username, password, _token, _custom_auth_factory):
    """Handler for basic auth type."""
    if username is None or password is None:
        raise ValueError("username/password required for basic auth")
    return basic_auth(username, password)


def _ws_auth_bearer(_username, _password, token, _custom_auth_factory):
    """Handler for bearer auth type."""
    if token is None:
        raise ValueError("token required for bearer auth")
    return bearer_token(token)


def _ws_auth_custom(_username, _password, _token, custom_auth_factory):
    """Handler for custom auth type."""
    if custom_auth_factory is None:
        raise ValueError("custom_auth_factory required for custom auth")
    return custom_auth_factory


# Dispatch dictionary for WebSocket auth types (O(1) lookup)
_WS_AUTH_DISPATCH = {
    "none": _ws_auth_none,
    "basic": _ws_auth_basic,
    "bearer": _ws_auth_bearer,
    "custom": _ws_auth_custom,
}


def create_http_client(  # pylint: disable=too-many-arguments
    base_url: Optional[str] = None,
    *,
    timeout: float = 10.0,
    proxy: Optional[str] = None,
    verify_ssl: bool = True,
    headers: Optional[dict[str, str]] = None,
    auth_type: AuthType = "none",
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    custom_auth_factory: Optional[Callable[[], dict[str, str]]] = None,
    max_retries: int = 2,
    backoff_factor: float = 0.5,
    max_redirects: int = 5,
) -> HttpClient:
    """Create HTTP client with specified authentication.

    Args:
        base_url: Base URL for requests
        timeout: Request timeout in seconds
        proxy: Proxy URL (e.g., "http://proxyhost:8080")
        verify_ssl: Whether to verify SSL certificates
        headers: Default headers to include with every request
        auth_type: Authentication type ("none", "basic", "bearer", "custom")
        username: Username for basic auth
        password: Password for basic auth
        token: Token for bearer auth
        custom_auth_factory: Custom auth header factory
        max_retries: Maximum retry attempts for failed requests
        backoff_factor: Exponential backoff multiplier
        max_redirects: Maximum redirect count

    Returns:
        HttpClient instance

    Example:
        client = create_http_client(
            "https://api.example.com",
            auth_type="bearer",
            token="MY_TOKEN"
        )
        response = client.get("/endpoint")

    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=(
                f"Creating HTTP client: auth_type={auth_type}, "
                f"base_url={base_url}, timeout={timeout}"
            ),
            scope='NETWORK_FACTORY'
        )
        execute_operation(
            GatewayInterface.DEBUG, 'timing',
            operation_name='create_http_client',
            scope='NETWORK_FACTORY'
        )

    handler = _HTTP_AUTH_DISPATCH.get(auth_type)
    if handler is None:
        if _DEBUG_ENABLED:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"Unknown auth_type: {auth_type}",
                scope='NETWORK_FACTORY'
            )
        raise ValueError(f"Unknown auth_type: {auth_type}")

    auth_factory = handler(username, password, token, custom_auth_factory)

    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="HTTP client created successfully",
            scope='NETWORK_FACTORY'
        )

    return HttpClient(
        base_url=base_url,
        timeout=timeout,
        proxy=proxy,
        verify_ssl=verify_ssl,
        default_headers=headers or {},
        auth_header_factory=auth_factory,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        max_redirects=max_redirects,
    )


def create_websocket_client(  # pylint: disable=too-many-arguments
    url: str,
    *,
    timeout: float = 10.0,
    proxy: Optional[str] = None,
    verify_ssl: bool = True,
    headers: Optional[dict[str, str]] = None,
    subprotocols: Optional[list] = None,
    auth_type: AuthType = "none",
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    custom_auth_factory: Optional[Callable[[], dict[str, str]]] = None,
) -> WebSocketClient:
    """Create WebSocket client with specified authentication.

    Args:
        url: WebSocket URL (ws:// or wss://)
        timeout: Connection timeout in seconds
        proxy: Proxy URL (e.g., "http://proxyhost:8080")
        verify_ssl: Whether to verify SSL certificates
        headers: Additional headers to include in handshake
        subprotocols: List of requested subprotocols
        auth_type: Authentication type ("none", "basic", "bearer", "custom")
        username: Username for basic auth
        password: Password for basic auth
        token: Token for bearer auth
        custom_auth_factory: Custom auth header factory

    Returns:
        WebSocketClient instance

    Example:
        ws = create_websocket_client(
            "wss://echo.websocket.events",
            auth_type="bearer",
            token="MY_TOKEN"
        )
        ws.connect()
        ws.send_text("hello")
        print(ws.recv())
        ws.close()

    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message=(
                f"Creating WebSocket client: auth_type={auth_type}, "
                f"url={url}, timeout={timeout}"
            ),
            scope='NETWORK_FACTORY'
        )
        execute_operation(
            GatewayInterface.DEBUG, 'timing',
            operation_name='create_websocket_client',
            scope='NETWORK_FACTORY'
        )

    headers = headers or {}
    subprotocols = subprotocols or []

    handler = _WS_AUTH_DISPATCH.get(auth_type)
    if handler is None:
        if _DEBUG_ENABLED:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"Unknown auth_type: {auth_type}",
                scope='NETWORK_FACTORY'
            )
        raise ValueError(f"Unknown auth_type: {auth_type}")

    auth_factory = handler(username, password, token, custom_auth_factory)

    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.DEBUG, 'log',
            message="WebSocket client created successfully",
            scope='NETWORK_FACTORY'
        )

    return WebSocketClient(
        url,
        timeout=timeout,
        headers=headers,
        subprotocols=subprotocols,
        verify_ssl=verify_ssl,
        proxy=proxy,
        auth_header_factory=auth_factory,
    )


__all__ = [
    "AuthType",
    "create_http_client",
    "create_websocket_client",
]
