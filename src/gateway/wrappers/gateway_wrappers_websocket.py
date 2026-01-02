"""
gateway_wrappers_websocket.py - WEBSOCKET Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for WEBSOCKET interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation


def websocket_connect(url: str, **kwargs) -> Dict[str, Any]:
    """Connect to WebSocket."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', url=url, **kwargs)


def websocket_send(connection_id: str, message: Any, **kwargs) -> None:
    """Send WebSocket message."""
    execute_operation(GatewayInterface.WEBSOCKET, 'send', connection_id=connection_id, message=message, **kwargs)


def websocket_receive(connection_id: str, **kwargs) -> Any:
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', connection_id=connection_id, **kwargs)


def websocket_close(connection_id: str, **kwargs) -> None:
    """Close WebSocket connection."""
    execute_operation(GatewayInterface.WEBSOCKET, 'close', connection_id=connection_id, **kwargs)


def websocket_request(url: str, message: Any, timeout: Optional[float] = None, **kwargs) -> Any:
    """Make WebSocket request (connect, send, receive, close)."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', url=url, message=message, timeout=timeout, **kwargs)


def websocket_get_stats() -> Dict[str, Any]:
    """Get WebSocket manager statistics."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'get_stats')


def websocket_reset() -> Dict[str, Any]:
    """Reset WebSocket manager state."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'reset')


__all__ = [
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    'websocket_get_stats',
    'websocket_reset',
]
