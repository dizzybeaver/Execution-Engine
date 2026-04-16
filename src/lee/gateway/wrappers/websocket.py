# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-23 - Created WebSocket wrapper module (7 operations)

"""WebSocket Wrapper Functions

Direct access to WebSocket operations through gateway.
All functions execute via execute_operation(GatewayInterface.WEBSOCKET, ...) internally.

Usage:
    from lee.gateway.wrappers import websocket

    # Connect to WebSocket
    result = websocket.connect(url='wss://example.com/ws')

    # Send message
    result = websocket.send(connection='conn1', message='Hello')

    # Receive message
    result = websocket.receive(connection='conn1')
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


# Connection Management
def connect(**kwargs: Any) -> dict[str, Any]:
    """Establish WebSocket connection.

    Args:
        **kwargs: Connection parameters (url, timeout, headers, etc.)

    Returns:
        Connection result with connection ID
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', **kwargs)


def close(**kwargs: Any) -> dict[str, Any]:
    """Close WebSocket connection.

    Args:
        **kwargs: Close parameters (connection, code, reason, etc.)

    Returns:
        Close operation result
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'close', **kwargs)


# Message Operations
def send(**kwargs: Any) -> dict[str, Any]:
    """Send message through WebSocket connection.

    Args:
        **kwargs: Message parameters (connection, message, etc.)

    Returns:
        Send operation result
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'send', **kwargs)


def receive(**kwargs: Any) -> dict[str, Any]:
    """Receive message from WebSocket connection.

    Args:
        **kwargs: Receive parameters (connection, timeout, etc.)

    Returns:
        Received message data
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', **kwargs)


def request(**kwargs: Any) -> dict[str, Any]:
    """Execute WebSocket request-response.

    Args:
        **kwargs: Request parameters (url, message, timeout, etc.)

    Returns:
        Request response data
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', **kwargs)


# Statistics and Management
def get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get WebSocket connection statistics.

    Args:
        **kwargs: Optional filter parameters

    Returns:
        WebSocket statistics including connection counts, message counts, etc.
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'get_stats', **kwargs)


def reset(**kwargs: Any) -> dict[str, Any]:
    """Reset WebSocket connection statistics.

    Args:
        **kwargs: Optional reset parameters

    Returns:
        Reset operation result
    """
    return execute_operation(GatewayInterface.WEBSOCKET, 'reset', **kwargs)


__all__ = [
    # Connection Management
    'connect',
    'close',

    # Message Operations
    'send',
    'receive',
    'request',

    # Statistics and Management
    'get_stats',
    'reset',
]
