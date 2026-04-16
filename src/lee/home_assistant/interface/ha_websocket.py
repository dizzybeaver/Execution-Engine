"""ha_websocket.py - Websocket Interface Router
Version: 2026-04-01_6
Description: Router for Websocket operations

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        authenticate_websocket as _authenticate_websocket_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        close_websocket_connection as _close_websocket_connection_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        establish_websocket_connection as _establish_websocket_connection_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        get_websocket_status as _get_websocket_status_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        receive_websocket_message as _receive_websocket_message_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        send_websocket_message as _send_websocket_message_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
        websocket_request as _websocket_request_impl,
    )
    _WEBSOCKET_AVAILABLE = True
except ImportError:
    _WEBSOCKET_AVAILABLE = False

    # Create stub implementations
    def _establish_websocket_connection_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _close_websocket_connection_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _authenticate_websocket_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _send_websocket_message_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _receive_websocket_message_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _websocket_request_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

    def _get_websocket_status_impl(**kwargs):
        return {"success": False, "error": "Websocket not available"}

# Dispatch dictionary for O(1) operation routing
_WEBSOCKET_DISPATCH = {
    "establish_websocket_connection": _establish_websocket_connection_impl,
    "close_websocket_connection": _close_websocket_connection_impl,
    "authenticate_websocket": _authenticate_websocket_impl,
    "send_websocket_message": _send_websocket_message_impl,
    "receive_websocket_message": _receive_websocket_message_impl,
    "websocket_request": _websocket_request_impl,
    "get_websocket_status": _get_websocket_status_impl,
}


class _WebsocketRouter(BaseSimpleDispatchRouter):
    """Router for Websocket interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Websocket",
            core_module=DummyModule(),
            dispatch_map=_WEBSOCKET_DISPATCH
        )


_websocket_router = _WebsocketRouter()


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """Execute Websocket operation via dispatch.

    Args:
        operation: The Websocket operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Websocket implementation
    """
    return _websocket_router.execute(operation, **kwargs)


def list_websocket_operations() -> list[str]:
    """List all available Websocket operations."""
    return _websocket_router.dispatch_map.keys()


__all__ = [
    "execute_websocket_operation",
    "list_websocket_operations",
    "_WEBSOCKET_AVAILABLE"
]
