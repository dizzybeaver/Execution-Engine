"""ha_assist.py - Assist Interface Router
Version: 2026-04-01_6
Description: Router for Assist operations

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import internal wrappers (SUGA-ISP: Interface owns its own helpers)
try:
    from lee.home_assistant.interface.wrappers.ha_assist_wrappers import (
        get_response as _get_response_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_assist_wrappers import (
        handle_pipeline as _handle_pipeline_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_assist_wrappers import (
        process_conversation as _process_conversation_impl,
    )
    from lee.home_assistant.interface.wrappers.ha_assist_wrappers import (
        send_message as _send_message_impl,
    )
    _ASSIST_AVAILABLE = True
except ImportError:
    _ASSIST_AVAILABLE = False

    # Create stub implementations
    def _send_message_impl(**kwargs):
        return {"success": False, "error": "Assist not available"}

    def _get_response_impl(**kwargs):
        return {"success": False, "error": "Assist not available"}

    def _process_conversation_impl(**kwargs):
        return {"success": False, "error": "Assist not available"}

    def _handle_pipeline_impl(**kwargs):
        return {"success": False, "error": "Assist not available"}

# Dispatch dictionary for O(1) operation routing
_ASSIST_DISPATCH = {
    "send_message": _send_message_impl,
    "get_response": _get_response_impl,
    "process_conversation": _process_conversation_impl,
    "handle_pipeline": _handle_pipeline_impl,
}


class _AssistRouter(BaseSimpleDispatchRouter):
    """Router for Assist interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Assist",
            core_module=DummyModule(),
            dispatch_map=_ASSIST_DISPATCH
        )


_assist_router = _AssistRouter()


def execute_assist_operation(operation: str, **kwargs) -> Any:
    """Execute Assist operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Assist operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Assist implementation
    """
    return _assist_router.execute(operation, **kwargs)


__all__ = ["execute_assist_operation"]
