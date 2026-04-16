"""ha_device_management.py
Version: 2026-04-11
Purpose: Device and entity management operations
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Devices router.
External modules MUST use execute_devices_operation() instead of importing directly.
"""

from typing import Any

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import helper functions from device_helpers module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.device_helpers import (
    _core_unavailable_error,
    _log_complete,
    _log_error,
    _DEVICES_AVAILABLE,
)

# Import protection - only work if devices core is available
try:
    pass
except ImportError:
    pass  # Already handled in device_helpers


# ===== Device Management Wrappers =====


def get_all_entities(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all entities."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_all_entities")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_all_entities START", has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_all_entities_impl,
        )
        result = get_all_entities_impl(oauth_token, **kwargs)
        _log_complete(correlation_id, "get_all_entities", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_all_entities", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_all_entities", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_all_entities", e)

    except Exception as e:
        return _log_error(correlation_id, "get_all_entities", e)


def get_entity_attributes(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get attributes for a specific entity."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_entity_attributes")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_entity_attributes START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_entity_attributes_impl,
        )
        result = get_entity_attributes_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_entity_attributes", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_entity_attributes", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_entity_attributes", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_entity_attributes", e)

    except Exception as e:
        return _log_error(correlation_id, "get_entity_attributes", e)


def get_entity_capabilities(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get capabilities for a specific entity."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_entity_capabilities")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_entity_capabilities START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_entity_capabilities_impl,
        )
        result = get_entity_capabilities_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_entity_capabilities", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_entity_capabilities", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_entity_capabilities", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_entity_capabilities", e)

    except Exception as e:
        return _log_error(correlation_id, "get_entity_capabilities", e)


def get_device_info(device_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get device information."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_device_info")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_info START", device_id=device_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_device_info_impl,
        )
        result = get_device_info_impl(device_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_device_info", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_device_info", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_device_info", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_device_info", e)

    except Exception as e:
        return _log_error(correlation_id, "get_device_info", e)


def get_device_registry(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all devices from registry."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_device_registry")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_registry START", has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_device_registry_impl,
        )
        result = get_device_registry_impl(oauth_token, **kwargs)
        _log_complete(correlation_id, "get_device_registry", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_device_registry", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_device_registry", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_device_registry", e)

    except Exception as e:
        return _log_error(correlation_id, "get_device_registry", e)


def get_area_devices(area_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all devices in an area."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_area_devices")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_area_devices START", area_id=area_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_area_devices_impl,
        )
        result = get_area_devices_impl(area_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_area_devices", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_area_devices", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_area_devices", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_area_devices", e)

    except Exception as e:
        return _log_error(correlation_id, "get_area_devices", e)


def get_entity_registry(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all entities from registry."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_entity_registry")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_entity_registry START", has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_entity_registry_impl,
        )
        result = get_entity_registry_impl(oauth_token, **kwargs)
        _log_complete(correlation_id, "get_entity_registry", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_entity_registry", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_entity_registry", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_entity_registry", e)

    except Exception as e:
        return _log_error(correlation_id, "get_entity_registry", e)


def update_entity_registry(entity_id: str, area_id: str = None, name: str = None,
                           icon: str = None, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Update entity in registry."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "update_entity_registry")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="update_entity_registry START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            update_entity_registry_impl,
        )
        result = update_entity_registry_impl(entity_id, area_id, name, icon, oauth_token, **kwargs)
        _log_complete(correlation_id, "update_entity_registry", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "update_entity_registry", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "update_entity_registry", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "update_entity_registry", e)

    except Exception as e:
        return _log_error(correlation_id, "update_entity_registry", e)


def remove_entity_registry(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Remove entity from registry."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "remove_entity_registry")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="remove_entity_registry START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            remove_entity_registry_impl,
        )
        result = remove_entity_registry_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "remove_entity_registry", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "remove_entity_registry", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "remove_entity_registry", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "remove_entity_registry", e)

    except Exception as e:
        return _log_error(correlation_id, "remove_entity_registry", e)


def get_device_by_id(device_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get device by ID."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_device_by_id")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_by_id START", device_id=device_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_device_by_id_impl,
        )
        result = get_device_by_id_impl(device_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_device_by_id", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_device_by_id", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_device_by_id", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_device_by_id", e)

    except Exception as e:
        return _log_error(correlation_id, "get_device_by_id", e)


def get_device_by_name(name: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get device by name."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_device_by_name")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_by_name START", name=name, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_device_by_name_impl,
        )
        result = get_device_by_name_impl(name, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_device_by_name", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_device_by_name", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_device_by_name", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_device_by_name", e)

    except Exception as e:
        return _log_error(correlation_id, "get_device_by_name", e)


def get_devices_by_area(area_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all devices in an area."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_devices_by_area")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_devices_by_area START", area_id=area_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_devices_by_area_impl,
        )
        result = get_devices_by_area_impl(area_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_devices_by_area", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_devices_by_area", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_devices_by_area", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_devices_by_area", e)

    except Exception as e:
        return _log_error(correlation_id, "get_devices_by_area", e)


def get_area_by_id(area_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get area by ID."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_area_by_id")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_area_by_id START", area_id=area_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_area_by_id_impl,
        )
        result = get_area_by_id_impl(area_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_area_by_id", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_area_by_id", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_area_by_id", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_area_by_id", e)

    except Exception as e:
        return _log_error(correlation_id, "get_area_by_id", e)


def get_all_areas(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all areas."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_all_areas")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_all_areas START", has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_all_areas_impl,
        )
        result = get_all_areas_impl(oauth_token, **kwargs)
        _log_complete(correlation_id, "get_all_areas", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_all_areas", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_all_areas", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_all_areas", e)

    except Exception as e:
        return _log_error(correlation_id, "get_all_areas", e)


def get_floor_info(floor_id: str = None, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get floor information."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_floor_info")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_floor_info START", floor_id=floor_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_floor_info_impl,
        )
        result = get_floor_info_impl(floor_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_floor_info", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_floor_info", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_floor_info", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_floor_info", e)

    except Exception as e:
        return _log_error(correlation_id, "get_floor_info", e)


