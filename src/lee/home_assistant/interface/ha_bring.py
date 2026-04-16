"""ha_bring.py - Bring Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BringRouter(BaseFallbackRouter):
    """Router for Bring operations."""

    def __init__(self):
        super().__init__(
            interface_name="Bring",
            import_path="lee.home_assistant.ha_bring.ha_bring_core",
            function_names=[
                "send_message_impl",
                "send_reaction_impl",
            ]
        )


_bring_router = _BringRouter()


def execute_bring_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Bring operation using dispatch dictionary.

    Args:
        operation: Operation name from BRING_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _bring_router.execute(operation, **kwargs)
