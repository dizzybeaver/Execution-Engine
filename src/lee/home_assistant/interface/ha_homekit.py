"""ha_homekit.py - Apple HomeKit Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _HomekitRouter(BaseFallbackRouter):
    """Router for Apple HomeKit interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="HomeKit",
            import_path="lee.home_assistant.ha_homekit.ha_homekit_core",
            function_names=[
                "reset_accessory_impl",
                "unpair_impl",
            ]
        )


_homekit_router = _HomekitRouter()


def execute_homekit_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Apple HomeKit interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _homekit_router.execute(operation, **kwargs)
