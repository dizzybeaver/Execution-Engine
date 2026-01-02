"""
interface/interface_websocket.py
Version: 2025-12-13_1
Purpose: WebSocket client interface router with import protection
License: Apache 2.0
"""

from typing import Any, Dict, Callable

# Import protection
try:
    import websocket
    _WEBSOCKET_AVAILABLE = True
    _WEBSOCKET_IMPORT_ERROR = None
except ImportError as e:
    _WEBSOCKET_AVAILABLE = False
    _WEBSOCKET_IMPORT_ERROR = str(e)


def _validate_url_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate url parameter exists."""
    if 'url' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'url' parameter")


def _validate_connection_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate connection parameter exists."""
    if 'connection' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'connection' parameter")


def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter exists."""
    if 'message' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'message' parameter")


def _validate_send_params(kwargs: Dict[str, Any]) -> None:
    """Validate send operation parameters."""
    _validate_connection_param(kwargs, 'send')
    _validate_message_param(kwargs, 'send')


def _validate_request_params(kwargs: Dict[str, Any]) -> None:
    """Validate request operation parameters."""
    _validate_url_param(kwargs, 'request')
    _validate_message_param(kwargs, 'request')


def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build WebSocket operation dispatch dictionary."""
    return {
        'connect': lambda **kwargs: (
            _validate_url_param(kwargs, 'connect'),
            websocket.websocket_connect_implementation(**kwargs)
        )[1],
        
        'send': lambda **kwargs: (
            _validate_send_params(kwargs),
            websocket.websocket_send_implementation(**kwargs)
        )[1],
        
        'receive': lambda **kwargs: (
            _validate_connection_param(kwargs, 'receive'),
            websocket.websocket_receive_implementation(**kwargs)
        )[1],
        
        'close': lambda **kwargs: (
            _validate_connection_param(kwargs, 'close'),
            websocket.websocket_close_implementation(**kwargs)
        )[1],
        
        'request': lambda **kwargs: (
            _validate_request_params(kwargs),
            websocket.websocket_request_implementation(**kwargs)
        )[1],
        
        'get_stats': lambda **kwargs: websocket.websocket_get_stats_implementation(**kwargs),
        
        'reset': lambda **kwargs: websocket.websocket_reset_implementation(**kwargs),
    }


_OPERATION_DISPATCH: Dict[str, Callable] = _build_dispatch_dict()


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket CLIENT operation requests to internal implementations.
    
    Args:
        operation: WebSocket operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If WebSocket interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    if not _WEBSOCKET_AVAILABLE:
        raise RuntimeError(
            f"WebSocket interface unavailable: {_WEBSOCKET_IMPORT_ERROR}"
        )
    
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_websocket_operation']
