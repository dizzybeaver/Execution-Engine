"""ha_sensor_core.py - Sensor Interface Core Implementation

Version: 2025-12-22_1
Description: Core implementations for Sensor integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


# ===== CORE IMPLEMENTATIONS =====


def get_device_class_units_impl(  # pylint: disable=too-many-return-statements
    device_class: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get convertible units for a sensor device class.

    Retrieves the list of units that a sensor device class can convert between.
    For example, a temperature sensor might support celsius, fahrenheit, and kelvin.

    Args:
        device_class: Sensor device class name (e.g., "temperature", "humidity")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and convertible units list
    """
    if not ha_config:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration required"
        }

    if not device_class:
        return missing_parameter("device_class")

    result = ha_execute_operation(
        HAGatewayInterface.WEBSOCKET,
        "execute_command",
        command_type="sensor/device_class_convertible_units",
        command_params={
            "device_class": device_class
        },
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        return {
            "success": True,
            "device_class": device_class,
            "units": result.get("result", {}).get("units", [])
        }

    return {
        "success": False,
        "error_code": result.get("error_code", "UNKNOWN_ERROR"),
        "error_message": result.get("error_message", "Failed to get device class units")
    }


def get_numeric_device_classes_impl(  # pylint: disable=too-many-return-statements
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get list of numeric sensor device classes.

    Retrieves all sensor device classes that support numeric values.
    This is useful for identifying which sensors can be used in calculations and graphs.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and numeric device class list
    """
    if not ha_config:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration required"
        }

    try:
        # Execute WebSocket command through WEBSOCKET interface
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="sensor/numeric_device_classes",
            command_params={},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "numeric_device_classes": result.get("result", {}).get("numeric_device_classes", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get numeric device classes")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting numeric device classes: {exc!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting numeric device classes: {exc!s}"
        }
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting numeric device classes: {exc!s}"
        }


def get_value_impl(  # pylint: disable=too-many-return-statements
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get sensor value (state only).

    Retrieves just the state value of a sensor entity.
    For full state with attributes, use get_state_impl.

    Args:
        entity_id: Sensor entity ID (e.g., "sensor.temperature_2f4f")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and sensor value
    """
    if not entity_id:
        return missing_parameter("entity_id")

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_state",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            state = result.get("result", {})
            return {
                "success": True,
                "entity_id": entity_id,
                "value": state.get("state"),
                "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
            }
        return result

    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting sensor value: {exc!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting sensor value: {exc!s}"
        }
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting sensor value: {exc!s}"
        }


def get_state_impl(  # pylint: disable=too-many-return-statements
    entity_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get sensor state with attributes.

    Retrieves full state including attributes like unit_of_measurement,
    device_class, friendly_name, etc.

    Args:
        entity_id: Sensor entity ID (e.g., "sensor.temperature_2f4f")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and full sensor state
    """
    if not entity_id:
        return missing_parameter("entity_id")

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_state",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            state = result.get("result", {})
            return {
                "success": True,
                "entity_id": entity_id,
                "state": state.get("state"),
                "attributes": state.get("attributes", {}),
                "last_changed": state.get("last_changed"),
                "last_updated": state.get("last_updated"),
                "context": state.get("context")
            }
        return result

    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting sensor state: {exc!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting sensor state: {exc!s}"
        }
    except Exception:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception getting sensor state"
        }


def list_sensors_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all sensor entities.

    Retrieves all sensors in the system, optionally filtered by device_class.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and list of sensors
    """
    return list_devices_impl("sensor", ha_config, correlation_id)


# ===== EXPORTS =====

__all__ = [
    "get_device_class_units_impl",
    "get_numeric_device_classes_impl",
    "get_value_impl",
    "get_state_impl",
    "list_sensors_impl",
]
