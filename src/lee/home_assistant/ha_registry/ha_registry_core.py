"""ha_registry_core.py - Home Assistant Registry Core Implementation
Version: 1.0.0
Date: 2026-03-15
Description: Core functions for Home Assistant registries (area, device, entity, category)

This module provides core implementations for interacting with Home Assistant
registries via HTTP API. All operations use the LEE gateway for HTTP calls.

Architecture:
- Registry operations route through HA gateway
- HTTP calls use gateway.execute_operation(GatewayInterface.HTTP_CLIENT, ...)
- Follows SUGA-ISP pattern for all gateway access

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation

# ===== CORE ENABLED FLAG =====

HA_REGISTRY_ENABLED = True


def _get_registry_config() -> dict[str, Any]:
    """Get registry configuration from HAConfig with mode-aware defaults."""
    try:
        from lee.home_assistant.ha_config import get_ha_config
        from lee.home_assistant.ha_deployment_mode import DeploymentMode, get_deployment_mode

        config = get_ha_config()
        mode = get_deployment_mode()

        # Use mode-aware timeout for Lambda deployments
        if mode == DeploymentMode.LAMBDA:
            timeout = 3.0  # Fast timeout for Lambda
        else:
            timeout = config.REGISTRY_TIMEOUT if config.REGISTRY_TIMEOUT is not None else 30

        return {
            "enabled": config.REGISTRY_ENABLED if config.REGISTRY_ENABLED is not None else True,
            "timeout": timeout,
            "source": config.source if config else "defaults"
        }
    except (ImportError, AttributeError, KeyError, TypeError, ValueError, RuntimeError):
        # Fallback to hardcoded defaults if config unavailable
        from lee.home_assistant.ha_deployment_mode import DeploymentMode, get_deployment_mode
        mode = get_deployment_mode()
        timeout = 3.0 if mode == DeploymentMode.LAMBDA else 30
        return {
            "enabled": True,
            "timeout": timeout,
            "source": "fallback"
        }


# FIX: Lazy-load registry config to ensure Lambda environment is fully initialized
# Module-level import happens before Lambda context is ready, causing
# deployment mode detection to fail and default to LOCAL mode (30s timeout)
# By lazy-loading, we ensure AWS_LAMBDA_FUNCTION_NAME is set before detection
_registry_config_cache = None

def _get_registry_config_cached() -> dict[str, Any]:
    """Get cached registry config or load it on first access."""
    global _registry_config_cache
    if _registry_config_cache is None:
        _registry_config_cache = _get_registry_config()
    return _registry_config_cache

# Backward compatibility: old code expects 'registry_config' as a module variable
# We make it a property that calls the lazy loader
class _RegistryConfigProxy(dict):
    """Proxy that lazily loads registry config on first access."""
    def __init__(self):
        super().__init__()
        self._loaded = False

    def __getitem__(self, key):
        if not self._loaded:
            self.update(_get_registry_config_cached())
            self._loaded = True
        return super().__getitem__(key)

    def get(self, key, default=None):
        if not self._loaded:
            self.update(_get_registry_config_cached())
            self._loaded = True
        return super().get(key, default)

registry_config = _RegistryConfigProxy()


# ===== AREA REGISTRY OPERATIONS =====


def list_areas_impl(ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """List all areas from Home Assistant area registry.

        ha_config: Home Assistant configuration (URL, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with areas list or error

    HTTP Endpoint: GET /api/config/areas

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_areas called")

        # Make HTTP GET request to Home Assistant
        url = f"{ha_config.get('url')}/api/config/areas"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="list_areas completed",
                            area_count=len(response.get("data", [])))
            return {
                "success": True,
                "areas": response.get("data", []),
                "count": len(response.get("data", [])),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_areas failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_AREAS_FAILED",
        }


def get_area_impl(area_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get area by ID from Home Assistant area registry.

        area_id: Area ID to retrieve
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with area data or error

    HTTP Endpoint: GET /api/config/areas/{area_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="get_area called", area_id=area_id)

        url = f"{ha_config.get('url')}/api/config/areas/{area_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="get_area completed", area_id=area_id)
            return {
                "success": True,
                "area": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_AREA_FAILED",
        }


def create_area_impl(name: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None,
                     icon: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """Create new area in Home Assistant area registry.

        name: Area name
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        icon: Optional icon for area
        **kwargs: Additional parameters (floor_id, picture, etc.)

        Dict with created area data or error

    HTTP Endpoint: POST /api/config/areas

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="create_area called", area_name=name)

        url = f"{ha_config.get('url')}/api/config/areas"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        data = {"name": name}
        if icon:
            data["icon"] = icon

        # Add optional parameters
        if "floor_id" in kwargs:
            data["floor_id"] = kwargs["floor_id"]
        if "picture" in kwargs:
            data["picture"] = kwargs["picture"]

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "post",
            url=url,
            headers=headers,
            json=data,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="create_area completed",
                            area_id=response.get("data", {}).get("area_id"))
            return {
                "success": True,
                "area": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="create_area failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "CREATE_AREA_FAILED",
        }


def update_area_impl(area_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None,
                     name: Optional[str] = None, icon: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """Update area in Home Assistant area registry.

        area_id: Area ID to update
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        name: New name (optional)
        icon: New icon (optional)
        **kwargs: Additional parameters

        Dict with updated area data or error

    HTTP Endpoint: POST /api/config/areas/{area_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="update_area called", area_id=area_id)

        url = f"{ha_config.get('url')}/api/config/areas/{area_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        data = {}
        if name is not None:
            data["name"] = name
        if icon is not None:
            data["icon"] = icon

        # Add optional parameters
        if "floor_id" in kwargs:
            data["floor_id"] = kwargs["floor_id"]
        if "picture" in kwargs:
            data["picture"] = kwargs["picture"]

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "post",
            url=url,
            headers=headers,
            json=data,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="update_area completed", area_id=area_id)
            return {
                "success": True,
                "area": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "UPDATE_AREA_FAILED",
        }


def delete_area_impl(area_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Delete area from Home Assistant area registry.

        area_id: Area ID to delete
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status or error

    HTTP Endpoint: DELETE /api/config/areas/{area_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="delete_area called", area_id=area_id)

        url = f"{ha_config.get('url')}/api/config/areas/{area_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "delete",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="delete_area completed", area_id=area_id)
            return {
                "success": True,
                "area_id": area_id,
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="delete_area failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "error": str(e),
            "error_code": "DELETE_AREA_FAILED",
        }


# ===== DEVICE REGISTRY OPERATIONS =====


def list_devices_impl(ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """List all devices from Home Assistant device registry.

        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with devices list or error

    HTTP Endpoint: GET /api/config/devices

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_devices called")

        url = f"{ha_config.get('url')}/api/config/devices"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="list_devices completed",
                            device_count=len(response.get("data", [])))
            return {
                "success": True,
                "devices": response.get("data", []),
                "count": len(response.get("data", [])),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_devices failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_DEVICES_FAILED",
        }


def get_device_impl(device_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get device by ID from Home Assistant device registry.

        device_id: Device ID to retrieve
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with device data or error

    HTTP Endpoint: GET /api/config/devices/{device_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="get_device called", device_id=device_id)

        url = f"{ha_config.get('url')}/api/config/devices/{device_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="get_device completed", device_id=device_id)
            return {
                "success": True,
                "device": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="get_device failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_DEVICE_FAILED",
        }


def update_device_impl(device_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None,
                      area_id: Optional[str] = None, name_by_user: Optional[str] = None, **_kwargs) -> dict[str, Any]:
    """Update device in Home Assistant device registry.

        device_id: Device ID to update
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        area_id: New area ID (optional)
        name_by_user: New custom name (optional)
        **kwargs: Additional parameters

        Dict with updated device data or error

    HTTP Endpoint: POST /api/config/devices/{device_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="update_device called", device_id=device_id)

        url = f"{ha_config.get('url')}/api/config/devices/{device_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        data = {}
        if area_id is not None:
            data["area_id"] = area_id
        if name_by_user is not None:
            data["name_by_user"] = name_by_user

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "post",
            url=url,
            headers=headers,
            json=data,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="update_device completed", device_id=device_id)
            return {
                "success": True,
                "device": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="update_device failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error_code": "UPDATE_DEVICE_FAILED",
        }


def delete_device_impl(device_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Delete device from Home Assistant device registry.

        device_id: Device ID to delete
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status or error

    HTTP Endpoint: DELETE /api/config/devices/{device_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="delete_device called", device_id=device_id)

        url = f"{ha_config.get('url')}/api/config/devices/{device_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "delete",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="delete_device completed", device_id=device_id)
            return {
                "success": True,
                "device_id": device_id,
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="delete_device failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "DELETE_DEVICE_FAILED",
        }

# ===== ENTITY REGISTRY OPERATIONS =====


def list_entities_impl(ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """List all entities from Home Assistant entity registry.

        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with entities list or error

    HTTP Endpoint: GET /api/config/entities

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_entities called")

        url = f"{ha_config.get('url')}/api/config/entities"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="list_entities completed",
                            entity_count=len(response.get("data", [])))
            return {
                "success": True,
                "entities": response.get("data", []),
                "count": len(response.get("data", [])),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_entities failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_ENTITIES_FAILED",
        }


def get_entity_impl(entity_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get entity by ID from Home Assistant entity registry.

        entity_id: Entity ID to retrieve
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with entity data or error

    HTTP Endpoint: GET /api/config/entities/{entity_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="get_entity called", entity_id=entity_id)

        url = f"{ha_config.get('url')}/api/config/entities/{entity_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="get_entity completed", entity_id=entity_id)
            return {
                "success": True,
                "entity": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="get_entity failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_ENTITY_FAILED",
        }


def update_entity_impl(entity_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None,
                      area_id: Optional[str] = None, name: Optional[str] = None, icon: Optional[str] = None, **kwargs) -> dict[str, Any]:  # pylint: disable=R0913,R0917
    """Update entity in Home Assistant entity registry.

        entity_id: Entity ID to update
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        area_id: New area ID (optional)
        name: New name (optional)
        icon: New icon (optional)
        **kwargs: Additional parameters

        Dict with updated entity data or error

    HTTP Endpoint: POST /api/config/entities/{entity_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="update_entity called", entity_id=entity_id)

        url = f"{ha_config.get('url')}/api/config/entities/{entity_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        data = {}
        if area_id is not None:
            data["area_id"] = area_id
        if name is not None:
            data["name"] = name
        if icon is not None:
            data["icon"] = icon

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "post",
            url=url,
            headers=headers,
            json=data,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="update_entity completed", entity_id=entity_id)
            return {
                "success": True,
                "entity": response.get("data"),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="update_entity failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "UPDATE_ENTITY_FAILED",
        }

def remove_entity_impl(entity_id: str, ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Remove entity from Home Assistant entity registry.

        entity_id: Entity ID to remove
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status or error

    HTTP Endpoint: DELETE /api/config/entities/{entity_id}

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="remove_entity called", entity_id=entity_id)

        url = f"{ha_config.get('url')}/api/config/entities/{entity_id}"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "delete",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="remove_entity completed", entity_id=entity_id)
            return {
                "success": True,
                "entity_id": entity_id,
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="remove_entity failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "REMOVE_ENTITY_FAILED",
        }


# ===== CATEGORY REGISTRY OPERATIONS =====

def list_categories_impl(ha_config: Optional[dict[str, Any]] = None, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """List all categories from Home Assistant category registry.

        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with categories list or error

    HTTP Endpoint: GET /api/config/categories

    """

    if ha_config is None:
        return {
            "success": False,
            "error": "Home Assistant configuration required",
            "error_code": "CONFIG_REQUIRED",
        }

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_categories called")

        url = f"{ha_config.get('url')}/api/config/categories"
        headers = {
            "Authorization": f"Bearer {ha_config.get('token')}",
            "Content-Type": "application/json",
        }

        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            "get",
            url=url,
            headers=headers,
            timeout=registry_config["timeout"],
        )

        if response.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_REGISTRY",
                            message="list_categories completed",
                            category_count=len(response.get("data", [])))
            return {
                "success": True,
                "categories": response.get("data", []),
                "count": len(response.get("data", [])),
            }
        return {
            "success": False,
            "error": response.get("error", "Unknown error"),
            "error_code": "HTTP_REQUEST_FAILED",
        }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_REGISTRY",
                        message="list_categories failed",
                        error_type=type(e).__name__, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_CATEGORIES_FAILED",
        }


# ===== EXPORTS =====

__all__ = [
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

# EOF
