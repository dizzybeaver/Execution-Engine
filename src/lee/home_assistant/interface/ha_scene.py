"""ha_scene.py - Router for Scene Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _SceneRouter(BaseFallbackRouter):
    """Router for Scene interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Scene",
            import_path="lee.home_assistant.ha_scene.ha_scene_core",
            function_names=[]
        )


_ha_scene_router = _SceneRouter()


def execute_ha_scene_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Scene interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_scene_router.execute(operation, **kwargs)


def list_ha_scene_operations() -> list[str]:
    """List all available Scene operations.

    Returns:
        List of operation names
    """
    return _ha_scene_router.list_operations()


__all__ = [
    "execute_ha_scene_operation",
    "list_ha_scene_operations",
]
