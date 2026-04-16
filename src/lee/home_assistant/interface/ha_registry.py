"""ha_registry.py - Router for Registry Interface

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

# Import actual registry implementation
from lee.home_assistant.ha_registry import (
    create_area_impl,
    delete_area_impl,
    delete_device_impl,
    get_area_impl,
    get_device_impl,
    get_entity_impl,
    list_areas_impl,
    list_categories_impl,
    list_devices_impl,
    list_entities_impl,
    remove_entity_impl,
    update_area_impl,
    update_device_impl,
    update_entity_impl,
)
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Dispatch dictionary for O(1) operation routing
_REGISTRY_DISPATCH = {
    # Area registry operations (5)
    "list_areas": list_areas_impl,
    "get_area": get_area_impl,
    "create_area": create_area_impl,
    "update_area": update_area_impl,
    "delete_area": delete_area_impl,

    # Device registry operations (4)
    "list_devices": list_devices_impl,
    "get_device": get_device_impl,
    "update_device": update_device_impl,
    "delete_device": delete_device_impl,

    # Entity registry operations (4)
    "list_entities": list_entities_impl,
    "get_entity": get_entity_impl,
    "update_entity": update_entity_impl,
    "remove_entity": remove_entity_impl,

    # Category registry operations (1)
    "list_categories": list_categories_impl,
}


class _RegistryRouter(BaseSimpleDispatchRouter):
    """Router for Registry interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Registry",
            core_module=DummyModule(),
            dispatch_map=_REGISTRY_DISPATCH
        )


_registry_router = _RegistryRouter()


def execute_registry_operation(operation: str, **kwargs) -> Any:
    """Execute Registry operation via dispatch.

    Args:
        operation: The Registry operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Registry implementation
    """
    return _registry_router.execute(operation, **kwargs)


def list_registry_operations() -> list[str]:
    """List all available Registry operations."""
    return _registry_router.dispatch_map.keys()


__all__ = [
    "execute_registry_operation",
    "list_registry_operations",
]
