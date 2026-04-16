# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor list function to use ha_device_base


"""ha_input_select_core.py - Core Implementation for Input Select Interface

Version: 2026-04-11_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    navigate_select_options_impl,
    reload_domain_impl,
)
from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)
from lee.home_assistant.utils.error_response_factory import (
    missing_parameter,
)


# ===== LIST INPUT SELECTS =====

def list_input_selects_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_select entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - input_selects: list of input_select entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    result = list_devices_impl("input_select", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "input_selects": result.get("input_select", []),
            "count": result.get("count", 0)
        }

    return result


# ===== SELECT NAVIGATION OPTIONS =====

def select_next_option_impl(
    entity_id: Optional[str] = None,
    cycle: bool = True,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Select next option in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
        cycle: Whether to cycle to first option after last (default: True)
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
    return navigate_select_options_impl(
        direction="next",
        entity_id=entity_id,
        cycle=cycle,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


def select_previous_option_impl(
    entity_id: Optional[str] = None,
    cycle: bool = True,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Select previous option in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
        cycle: Whether to cycle to last option after first (default: True)
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
    return navigate_select_options_impl(
        direction="previous",
        entity_id=entity_id,
        cycle=cycle,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


def select_first_option_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Select first option in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
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
    return navigate_select_options_impl(
        direction="first",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


def select_last_option_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Select last option in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
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
    return navigate_select_options_impl(
        direction="last",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


# ===== SELECT OPTION =====

def select_option_impl(
    entity_id: Optional[str] = None,
    option: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Select specific option in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
        option: Option name to select
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

    if not option:
        return missing_parameter("option")

    service_data = {"entity_id": entity_id, "option": option}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="input_select",
        service="select_option",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Input select option selected successfully"

    return result


# ===== SET OPTIONS =====

def set_options_impl(
    entity_id: Optional[str] = None,
    options: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set available options in input_select.

    Args:
        entity_id: Input select entity ID (e.g., "input_select.test_select")
        options: List of option strings
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

    if not options:
        return missing_parameter("options")

    service_data = {"entity_id": entity_id, "options": options}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="input_select",
        service="set_options",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Input select options set successfully"

    return result


# ===== RELOAD INPUT SELECTS =====

def reload_input_selects_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_select configurations.

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
    return reload_domain_impl("input_select", ha_config, correlation_id)
