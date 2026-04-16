"""ha_input_datetime_core.py - Core Implementation for Input DateTime Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import (
    list_devices_impl,
    reload_domain_impl,
    set_input_value_impl,
)

# ===== LIST INPUT DATETIMES =====

def list_input_datetimes_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_datetime entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - input_datetimes: list of input_datetime entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return list_devices_impl("input_datetime", ha_config, correlation_id)


# ===== SET DATETIME =====

def set_datetime_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Set input_datetime value.

    Args:
        entity_id: Input datetime entity ID (e.g., "input_datetime.test_datetime")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters (date, time, datetime, timestamp)

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return set_input_value_impl(
        domain="input_datetime",
        entity_id=entity_id,
        value=None,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs
    )


# ===== RELOAD INPUT DATETIMES =====

def reload_input_datetimes_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_datetime configurations.

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
    return reload_domain_impl("input_datetime", ha_config, correlation_id)
