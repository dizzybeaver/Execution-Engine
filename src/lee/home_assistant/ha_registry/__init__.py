"""ha_registry - Home Assistant Registry Interface

Provides registry management for Home Assistant:
- Area Registry
- Device Registry
- Entity Registry
- Category Registry

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from lee.home_assistant.ha_registry.ha_registry_core import (
    HA_REGISTRY_ENABLED,
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

__all__ = [
    # Core flags
    "HA_REGISTRY_ENABLED",

    # Area registry
    "list_areas_impl",
    "get_area_impl",
    "create_area_impl",
    "update_area_impl",
    "delete_area_impl",

    # Device registry
    "list_devices_impl",
    "get_device_impl",
    "update_device_impl",
    "delete_device_impl",

    # Entity registry
    "list_entities_impl",
    "get_entity_impl",
    "update_entity_impl",
    "remove_entity_impl",

    # Category registry
    "list_categories_impl",
]
