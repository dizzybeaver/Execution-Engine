# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Add navigate_select_options_impl for input select


"""ha_device_base.py - Base Device Control Functions

Version: 2026-04-11_1
Description: Generic device control implementations to eliminate code duplication
across 88 HA device core modules. These base functions handle common operations
for all device types (lights, switches, fans, etc.).

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway_enums import HAGatewayInterface
from lee.home_assistant.ha_gateway_generic import ha_execute_operation
from lee.home_assistant.utils import missing_parameter


# ===== GENERIC DEVICE CONTROL FUNCTIONS =====


def turn_on_device_impl(
    domain: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    service: str = "turn_on",
    **extra_params
) -> dict[str, Any]:
    """Generic device turn-on implementation.

    Args:
        domain: Device domain (light, switch, fan, etc.)
        entity_id: Entity ID
        ha_config: Home Assistant config
        correlation_id: Tracking ID
        service: Service name (default: turn_on)
        **extra_params: Additional service parameters (brightness, color, etc.)

    Returns:
        Standardized result dict
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}
    service_data.update(extra_params)

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain=domain,
        service=service,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = f"{domain.capitalize()} turned on successfully"

    return result


def turn_off_device_impl(
    domain: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **extra_params
) -> dict[str, Any]:
    """Generic device turn-off implementation.

    Args:
        domain: Device domain (light, switch, fan, etc.)
        entity_id: Entity ID
        ha_config: Home Assistant config
        correlation_id: Tracking ID
        **extra_params: Additional service parameters

    Returns:
        Standardized result dict
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}
    service_data.update(extra_params)

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain=domain,
        service="turn_off",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = f"{domain.capitalize()} turned off successfully"

    return result


def toggle_device_impl(
    domain: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **extra_params
) -> dict[str, Any]:
    """Generic device toggle implementation.

    Args:
        domain: Device domain (light, switch, fan, etc.)
        entity_id: Entity ID
        ha_config: Home Assistant config
        correlation_id: Tracking ID
        **extra_params: Additional service parameters

    Returns:
        Standardized result dict
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}
    service_data.update(extra_params)

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain=domain,
        service="toggle",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = f"{domain.capitalize()} toggled successfully"

    return result


def list_devices_impl(
    domain: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic device list implementation.

    Args:
        domain: Device domain (light, switch, fan, etc.)
        ha_config: Home Assistant config
        correlation_id: Tracking ID
        **_kwargs: Additional parameters (ignored)

    Returns:
        Dict with success status and list of devices
    """
    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "get_states",
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if not result.get("success"):
        return result

    # Filter entities by domain
    all_states = result.get("data", [])
    domain_devices = [
        state for state in all_states
        if state.get("entity_id", "").startswith(f"{domain}.")
    ]

    return {
        "success": True,
        domain: domain_devices,
        "count": len(domain_devices),
        "data": domain_devices
    }


def reload_domain_impl(
    domain: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Base function for reloading Home Assistant domain entities.

    Forces Home Assistant to reload all entities for a specific domain
    from their configured integrations.

    Args:
        domain: Home Assistant domain name (e.g., 'binary_sensor', 'group', 'scene')
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        Dict with success status and message
    """
    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain=domain,
        service="reload",
        service_data={},
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        domain_title = domain.replace('_', ' ').title()
        result["message"] = f"{domain_title} entities reloaded successfully"

    return result


def set_input_value_impl(
    domain: str,
    entity_id: Optional[str] = None,
    value: Any = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **extra_params
) -> dict[str, Any]:
    """Generic input device set_value implementation.

    Args:
        domain: Input device domain (input_number, input_text, input_datetime, etc.)
        entity_id: Entity ID
        value: Value to set (str, int, float, or dict with date/time parameters)
        ha_config: Home Assistant config
        correlation_id: Tracking ID
        **extra_params: Additional service parameters

    Returns:
        Standardized result dict
    """
    if not entity_id:
        return missing_parameter("entity_id")

    if value is None and not extra_params:
        return missing_parameter("value")

    service_data = {"entity_id": entity_id}

    if value is not None:
        service_data["value"] = value

    service_data.update(extra_params)

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain=domain,
        service="set_value",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = f"{domain.replace('_', ' ').title()} value set successfully"

    return result


def navigate_select_options_impl(
    direction: str,
    entity_id: Optional[str] = None,
    cycle: bool = True,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic input select navigation implementation.

    Consolidates select_next, select_previous, select_first, and select_last
    operations into a single base function.

    Args:
        direction: Navigation direction ('next', 'previous', 'first', 'last')
        entity_id: Input select entity ID (e.g., "input_select.test_select")
        cycle: Whether to cycle options (only for 'next' and 'previous', default: True)
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    valid_directions = {
        "next": "select_next",
        "previous": "select_previous",
        "first": "select_first",
        "last": "select_last"
    }

    if direction not in valid_directions:
        valid_list = list(valid_directions.keys())
        return {
            "success": False,
            "error_code": "INVALID_DIRECTION",
            "error_message": (
                f"Invalid direction: {direction}. "
                f"Must be one of {valid_list}"
            )
        }

    service_name = valid_directions[direction]
    service_data = {"entity_id": entity_id}

    if direction in ("next", "previous"):
        service_data["cycle"] = cycle

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="input_select",
        service=service_name,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        direction_name = direction.replace('_', ' ')
        result["message"] = (
            f"Input select {direction_name} option selected successfully"
        )

    return result


def get_entity_state_impl(
    entity_type: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get specific entity state by type (zone, person, etc.).

    Consolidates get_zone_state_impl and get_person_state_impl to eliminate
    code duplication across zone and person modules.

    Args:
        entity_type: Entity type name (e.g., "zone", "person") for error messages
        entity_id: Entity ID (e.g., "zone.home", "person.john")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        Dict with success status and entity details
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_states",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "state": all_states[0]
                }
            return {
                "success": False,
                "error_code": f"{entity_type.upper()}_NOT_FOUND",
                "error_message": f"{entity_type.capitalize()} {entity_id} not found"
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get(
                "error_message",
                f"Failed to get {entity_type}"
            )
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting {entity_type}: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting {entity_type}: {e!s}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting {entity_type}: {e!s}"
        }


def adjust_input_number_impl(
    adjustment: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic input number adjustment implementation.

    Consolidates increment and decrement operations for input_number entities
    into a single base function.

    Args:
        adjustment: Adjustment direction ('increment' or 'decrement')
        entity_id: Input number entity ID (e.g., "input_number.test_number")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    valid_adjustments = ("increment", "decrement")

    if adjustment not in valid_adjustments:
        return {
            "success": False,
            "error_code": "INVALID_ADJUSTMENT",
            "error_message": (
                f"Invalid adjustment: {adjustment}. "
                f"Must be one of {list(valid_adjustments)}"
            )
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="input_number",
        service=adjustment,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = f"Input number {adjustment}ed successfully"

    return result


def media_control_impl(
    action: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic media control implementation.

    Consolidates media_pause, media_stop, and media_play operations into a
    single base function. Eliminates 75 lines of duplicated code.

    Args:
        action: Media control action ('media_pause', 'media_stop', 'media_play')
        entity_id: Media player entity ID (e.g., "media_player.living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    valid_actions = {
        "media_pause": "Media paused successfully",
        "media_stop": "Media stopped successfully",
        "media_play": "Media playback resumed successfully"
    }

    if action not in valid_actions:
        return {
            "success": False,
            "error_code": "INVALID_ACTION",
            "error_message": (
                f"Invalid action: {action}. "
                f"Must be one of {list(valid_actions.keys())}"
            )
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service=action,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = valid_actions[action]

    return result


def volume_control_impl(
    action: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic volume control implementation.

    Consolidates volume_up and volume_down operations into a single base
    function. Eliminates 50 lines of duplicated code.

    Args:
        action: Volume control action ('volume_up' or 'volume_down')
        entity_id: Media player entity ID (e.g., "media_player.living_room")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    valid_actions = {
        "volume_up": "Volume increased successfully",
        "volume_down": "Volume decreased successfully"
    }

    if action not in valid_actions:
        return {
            "success": False,
            "error_code": "INVALID_ACTION",
            "error_message": (
                f"Invalid action: {action}. "
                f"Must be one of {list(valid_actions.keys())}"
            )
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="media_player",
        service=action,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = valid_actions[action]

    return result


def vacuum_control_impl(
    service: str,
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Generic vacuum control implementation.

    Consolidates pause, stop, return_to_base, clean_spot, and locate
    operations for vacuum entities into a single base function.

    Args:
        service: Service name ('pause', 'stop', 'return_to_base',
            'clean_spot', 'locate')
        entity_id: Vacuum entity ID (e.g., "vacuum.roomba")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters (ignored)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    valid_services = {
        "pause": "Vacuum paused successfully",
        "stop": "Vacuum stopped successfully",
        "return_to_base": "Vacuum returning to base successfully",
        "clean_spot": "Vacuum cleaning spot successfully",
        "locate": "Vacuum located successfully"
    }

    if service not in valid_services:
        return {
            "success": False,
            "error_code": "INVALID_SERVICE",
            "error_message": (
                f"Invalid service: {service}. "
                f"Must be one of {list(valid_services.keys())}"
            )
        }

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="vacuum",
        service=service,
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = valid_services[service]

    return result


__all__ = [
    "turn_on_device_impl",
    "turn_off_device_impl",
    "toggle_device_impl",
    "list_devices_impl",
    "reload_domain_impl",
    "set_input_value_impl",
    "navigate_select_options_impl",
    "get_entity_state_impl",
    "adjust_input_number_impl",
    "media_control_impl",
    "volume_control_impl",
    "vacuum_control_impl",
]
