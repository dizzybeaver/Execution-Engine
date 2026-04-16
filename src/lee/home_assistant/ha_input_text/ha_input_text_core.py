"""ha_input_text_core.py - Core Implementation for Input Text Interface

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

# ===== LIST INPUT TEXTS =====

def list_input_texts_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all input_text entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - input_texts: list of input_text entities
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    return list_devices_impl("input_text", ha_config, correlation_id)


# ===== SET VALUE INPUT TEXT =====

def set_value_input_text_impl(
    entity_id: Optional[str] = None,
    value: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set input_text value.

    Args:
        entity_id: Input text entity ID (e.g., "input_text.test_text")
        value: Text value to set
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
        domain="input_text",
        entity_id=entity_id,
        value=value,
        ha_config=ha_config,
        correlation_id=correlation_id
    )


# ===== RELOAD INPUT TEXTS =====

def reload_input_texts_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Reload input_text configurations.

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
    return reload_domain_impl("input_text", ha_config, correlation_id)
