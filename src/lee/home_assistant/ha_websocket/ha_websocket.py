"""ha_websocket.py - WebSocket Operations (Compatibility Layer)
Version: 3.0.0
Description: WebSocket communication with debug tracing and timing metrics

REFACTORED: Split from 498 lines into multiple files to meet AWS Lambda 350-line limit.
This file now serves as a compatibility layer importing from split modules.

Split modules:
- ha_websocket_core.py: Core WebSocket operations (connect, send, receive, close, auth, request)
- ha_websocket_entities.py: Entity registry operations
- ha_websocket_utils.py: Utility functions and helpers

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

# Import gateway operations
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import core WebSocket operations
from lee.home_assistant.ha_websocket.ha_websocket_connection import (
    close_websocket_connection,
    establish_websocket_connection,
)
from lee.home_assistant.ha_websocket.ha_websocket_messaging import (
    authenticate_websocket,
    receive_websocket_message,
    send_websocket_message,
)

# Constants
WEBSOCKET_ENABLED = True
WEBSOCKET_TIMEOUT = 10
WEBSOCKET_CACHE_TTL = 300

__all__ = [
    "WEBSOCKET_CACHE_TTL",
    "WEBSOCKET_ENABLED",
    "WEBSOCKET_TIMEOUT",
    "close_connection",
    "establish_connection",
    "receive_message",
    "send_message",
    "websocket_auth",
]

# ===== SUGA-ISP COMPLIANT DEBUG FUNCTIONS =====


def establish_connection(url: str, timeout: int = 10):
    """Legacy compatibility wrapper for establish_websocket_connection."""
    correlation_id = generate_correlation_id("ws")
    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="establish_connection LEGACY_WRAPPER", url=url[:50])
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    return establish_websocket_connection(url, timeout)

def send_message(connection: Any, message: dict):
    """Legacy compatibility wrapper for send_websocket_message."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_message LEGACY_WRAPPER")
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    return send_websocket_message(connection, message)

def receive_message(connection: Any, timeout: int = 10):
    """Legacy compatibility wrapper for receive_websocket_message."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="receive_message LEGACY_WRAPPER", timeout=timeout)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    return receive_websocket_message(connection, timeout)

def close_connection(connection: Any):
    """Legacy compatibility wrapper for close_websocket_connection."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="close_connection LEGACY_WRAPPER")
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    return close_websocket_connection(connection)

def websocket_auth(connection: Any, access_token: str):
    """Legacy compatibility wrapper for authenticate_websocket."""
    correlation_id = generate_correlation_id("ws")
    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="websocket_auth LEGACY_WRAPPER", has_token=bool(access_token))
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    return authenticate_websocket(connection, access_token)

# Add legacy wrappers to exports
__all__.extend([
    "WEBSOCKET_CACHE_TTL",
    "WEBSOCKET_ENABLED",
    "WEBSOCKET_TIMEOUT",
    "close_connection",
    "establish_connection",
    "receive_message",
    "send_message",
    "websocket_auth",
])

# EOF
