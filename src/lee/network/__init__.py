"""network/__init__.py
Unified networking module - HTTP and WebSocket with gateway operations

Version: 2.0.0 (2026-03-07)
Changes: Unified from http_client/ and websocket/, added security fixes
"""

import os

# Debug tracing support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"

if _DEBUG_ENABLED:
    from lee.gateway import execute_operation, GatewayInterface
    execute_operation(GatewayInterface.DEBUG, 'log',
                     message="Initializing network module",
                     scope='NETWORK_INIT')

# Core implementations (unchanged)
from lee.network.http_auth import basic_auth, bearer_token, no_auth, static_headers
from lee.network.http_core import (  # pylint: disable=redefined-builtin
    ConnectionError,
    HttpClient,
    HTTPError,
    HttpResponse,
    Timeout,
)

if _DEBUG_ENABLED:
    from lee.gateway import execute_operation, GatewayInterface
    execute_operation(GatewayInterface.DEBUG, 'log',
                     message="Imported HTTP core modules",
                     scope='NETWORK_INIT')

# NEW: Gateway operations
from lee.network.http_operations import (
    configure_retry_implementation,
    get_http_circuit_state,
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

if _DEBUG_ENABLED:
    from lee.gateway import execute_operation, GatewayInterface
    execute_operation(GatewayInterface.DEBUG, 'log',
                     message="Imported HTTP gateway operations",
                     scope='NETWORK_INIT')

# NEW: SSRF protection
from lee.network.ssrf_protect import is_url_safe, validate_url
from lee.network.ws_core import WebSocketClient, WebSocketClosed, WebSocketError
from lee.network.ws_operations import (
    websocket_close_implementation,
    websocket_connect_implementation,
    websocket_get_stats_implementation,
    websocket_receive_implementation,
    websocket_request_implementation,
    websocket_reset_implementation,
    websocket_send_implementation,
)

if _DEBUG_ENABLED:
    from lee.gateway import execute_operation, GatewayInterface
    execute_operation(GatewayInterface.DEBUG, 'log',
                     message="Imported WebSocket modules and SSRF protection",
                     scope='NETWORK_INIT')

__all__ = [
    # Core HTTP
    "HttpClient",
    "HttpResponse",
    "HTTPError",
    "Timeout",
    "ConnectionError",
    # HTTP Auth
    "no_auth",
    "basic_auth",
    "bearer_token",
    "static_headers",
    # Core WebSocket
    "WebSocketClient",
    "WebSocketError",
    "WebSocketClosed",
    # Gateway HTTP operations
    "http_request_implementation",
    "http_get_implementation",
    "http_post_implementation",
    "http_put_implementation",
    "http_delete_implementation",
    "http_reset_implementation",
    "get_state_implementation",
    "reset_state_implementation",
    "configure_retry_implementation",
    "get_statistics_implementation",
    "get_http_circuit_state",
    # Gateway WebSocket operations
    "websocket_connect_implementation",
    "websocket_send_implementation",
    "websocket_receive_implementation",
    "websocket_close_implementation",
    "websocket_request_implementation",
    "websocket_get_stats_implementation",
    "websocket_reset_implementation",
    # SSRF protection
    "validate_url",
    "is_url_safe",
]
