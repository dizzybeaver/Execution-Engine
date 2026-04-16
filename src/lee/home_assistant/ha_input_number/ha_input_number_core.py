"""ha_input_number_core.py - Core Implementation for Input Number Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    adjust_input_number_impl,
    list_devices_impl,
    reload_domain_impl,
    set_input_value_impl,
)

# ===== LIST INPUT NUMBERS =====

def list_input_numbers_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_number entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - input_numbers: list of input_number entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return list_devices_impl("input_number", ha_config, correlation_id)


# ===== DECREMENT INPUT NUMBER =====

def decrement_input_number_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Decrement input_number value.

    Args:
        entity_id: Input number entity ID (e.g., "input_number.test_number")
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
    return adjust_input_number_impl(
        adjustment="decrement",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


# ===== INCREMENT INPUT NUMBER =====

def increment_input_number_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Increment input_number value.

    Args:
        entity_id: Input number entity ID (e.g., "input_number.test_number")
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
    return adjust_input_number_impl(
        adjustment="increment",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


# ===== SET VALUE INPUT NUMBER =====

def set_value_input_number_impl(
    entity_id: Optional[str] = None,
    value: float | Optional[int] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set input_number value.

    Args:
        entity_id: Input number entity ID (e.g., "input_number.test_number")
        value: Numeric value to set
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
    return set_input_value_impl(
        domain="input_number",
        entity_id=entity_id,
        value=value,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


# ===== RELOAD INPUT NUMBERS =====

def reload_input_numbers_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_number configurations.

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
    return reload_domain_impl("input_number", ha_config, correlation_id)
