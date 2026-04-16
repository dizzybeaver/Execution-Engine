"""ha_input_button_core.py - Core Implementation for Input Button Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl, reload_domain_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter

# ===== LIST INPUT BUTTONS =====

def list_input_buttons_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_button entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - input_buttons: list of input_button entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return list_devices_impl("input_button", ha_config, correlation_id)


# ===== PRESS INPUT BUTTON =====

def press_input_button_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Press input_button entity.

    Args:
        entity_id: Input button entity ID (e.g., "input_button.test_button")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="input_button",
        service="press",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Input button pressed successfully"

    return result


# ===== RELOAD INPUT BUTTONS =====

def reload_input_buttons_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_button configurations.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return reload_domain_impl("input_button", ha_config, correlation_id)
