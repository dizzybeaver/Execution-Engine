# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_websocket.py
Version: 2026-04-11_2
Purpose: WebSocket client interface router with Static DDS
License: Apache 2.0
"""

from typing import Any

from lee.utils.graceful_import import graceful_import


@graceful_import('lee.network')
def _import_websocket():
    from lee.network import ws_operations
    return {'ws_operations': ws_operations}


_websocket_funcs = _import_websocket()
_WEBSOCKET_AVAILABLE = _import_websocket.__dict__.get(
    '_WEBSOCKET_AVAILABLE',
    False
)
_WEBSOCKET_IMPORT_ERROR = _import_websocket.__dict__.get(
    '_WEBSOCKET_IMPORT_ERROR',
    None
)

if _WEBSOCKET_AVAILABLE:
    ws_operations = _websocket_funcs['ws_operations']
else:
    ws_operations = None


def _validate_url_param(kwargs: dict[str, Any], operation: str) -> None:
    """Validate url parameter exists."""
    if "url" not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'url' parameter")


def _validate_connection_param(kwargs: dict[str, Any], operation: str) -> None:
    """Validate connection parameter exists."""
    if "connection" not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'connection' parameter")


def _validate_message_param(kwargs: dict[str, Any], operation: str) -> None:
    """Validate message parameter exists."""
    if "message" not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'message' parameter")


def _validate_send_params(kwargs: dict[str, Any]) -> None:
    """Validate send operation parameters."""
    _validate_connection_param(kwargs, "send")
    _validate_message_param(kwargs, "send")


def _validate_request_params(kwargs: dict[str, Any]) -> None:
    """Validate request operation parameters."""
    _validate_url_param(kwargs, "request")
    _validate_message_param(kwargs, "request")


# Wrapper functions to replace lambda tuple-trick
def _connect_wrapper(**kwargs) -> Any:
    """Wrapper for connect operation with validation."""
    _validate_url_param(kwargs, "connect")
    return ws_operations.websocket_connect_implementation(**kwargs)


def _send_wrapper(**kwargs) -> Any:
    """Wrapper for send operation with validation."""
    _validate_send_params(kwargs)
    return ws_operations.websocket_send_implementation(**kwargs)


def _receive_wrapper(**kwargs) -> Any:
    """Wrapper for receive operation with validation."""
    _validate_connection_param(kwargs, "receive")
    return ws_operations.websocket_receive_implementation(**kwargs)


def _close_wrapper(**kwargs) -> Any:
    """Wrapper for close operation with validation."""
    _validate_connection_param(kwargs, "close")
    return ws_operations.websocket_close_implementation(**kwargs)


def _request_wrapper(**kwargs) -> Any:
    """Wrapper for request operation with validation."""
    _validate_request_params(kwargs)
    return ws_operations.websocket_request_implementation(**kwargs)


def _call_ws_command_wrapper(**kwargs) -> Any:
    """Wrapper for call_ws_command operation with validation."""
    _validate_request_params(kwargs)
    return ws_operations.websocket_request_implementation(**kwargs)


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build Static Dispatch Dictionary for WebSocket operations.

    Each entry contains:
    - func: Handler function
    - category: Operation category (read/write/delete/admin)
    - description: Human-readable description
    """
    return {
        "connect": {
            "func": _connect_wrapper,
            "category": "write",
            "description": "Establish WebSocket connection",
        },
        "send": {
            "func": _send_wrapper,
            "category": "write",
            "description": "Send message through WebSocket connection",
        },
        "receive": {
            "func": _receive_wrapper,
            "category": "read",
            "description": "Receive message from WebSocket connection",
        },
        "close": {
            "func": _close_wrapper,
            "category": "delete",
            "description": "Close WebSocket connection",
        },
        "request": {
            "func": _request_wrapper,
            "category": "write",
            "description": "Execute WebSocket request-response",
        },
        "get_stats": {
            "func": ws_operations.websocket_get_stats_implementation,
            "category": "read",
            "description": "Get WebSocket connection statistics",
        },
        "reset": {
            "func": ws_operations.websocket_reset_implementation,
            "category": "delete",
            "description": "Reset WebSocket connection statistics",
        },
        "call_ws_command": {
            "func": _call_ws_command_wrapper,
            "category": "write",
            "description": "Execute WebSocket command (alias for request operation)",
        },
    }


_OPERATION_DISPATCH: dict[str, dict[str, Any]] = (
    _build_dispatch_dict() if _WEBSOCKET_AVAILABLE else {}
)


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """Route WebSocket CLIENT operation using enhanced dispatch pattern.

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
            f"WebSocket interface unavailable: {_WEBSOCKET_IMPORT_ERROR}",
        )

    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid: {', '.join(_OPERATION_DISPATCH.keys())}",
        )

    entry = _OPERATION_DISPATCH[operation]
    func = entry["func"]
    return func(**kwargs)


__all__ = ["execute_websocket_operation"]
