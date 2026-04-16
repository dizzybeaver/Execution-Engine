"""ha_alexa.py - Router for Alexa Interface

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_alexa_wrappers import (
        handle_control as _handle_control_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_alexa_wrappers import (
        handle_discovery as _handle_discovery_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_alexa_wrappers import (
        process_directive as _process_directive_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_alexa_wrappers import (
        handle_accept_grant as _handle_accept_grant_impl,
    )
    _ALEXA_AVAILABLE = True
except ImportError:
    _ALEXA_AVAILABLE = False

    # Create stub implementations
    def _process_directive_impl(**kwargs):
        return {"success": False, "error": "ALEXA not available"}

    def _handle_discovery_impl(**kwargs):
        return {"success": False, "error": "ALEXA not available"}

    def _handle_control_impl(**kwargs):
        return {"success": False, "error": "ALEXA not available"}

    def _handle_accept_grant_impl(**kwargs):
        return {"success": False, "error": "ALEXA not available"}

# Dispatch dictionary for O(1) operation routing
_ALEXA_DISPATCH = {
    "process_directive": _process_directive_impl,
    "discovery": _handle_discovery_impl,
    "handle_discovery": _handle_discovery_impl,
    "handle_control": _handle_control_impl,
    "accept_grant": _handle_accept_grant_impl,
}


class _AlexaRouter(BaseSimpleDispatchRouter):
    """Router for Alexa interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Alexa",
            core_module=DummyModule(),
            dispatch_map=_ALEXA_DISPATCH
        )


_alexa_router = _AlexaRouter()


def execute_alexa_operation(operation: str, **kwargs) -> Any:
    """Execute Alexa operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Alexa operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Alexa implementation
    """
    return _alexa_router.execute(operation, **kwargs)


def list_alexa_operations() -> list[str]:
    """List all available Alexa operations."""
    return _alexa_router.dispatch_map.keys()


__all__ = [
    "execute_alexa_operation",
    "list_alexa_operations",
    "_ALEXA_AVAILABLE"
]
