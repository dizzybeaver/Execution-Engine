"""ha_script_core.py - Script Interface Core Implementation

Version: 2025-12-22_1
Description: Core implementations for script execution

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import turn_on_device_impl
from lee.home_assistant.utils import missing_parameter


# ===== CORE IMPLEMENTATIONS =====


def run_script_impl(  # pylint: disable=too-many-return-statements
    entity_id: str,
    variables: Optional[dict[str, Any]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Run a script.

    Scripts are reusable sequences of actions that can be triggered manually
    or by automation. Examples include morning routines, away mode sequences,
    or custom action sequences.

    Args:
        entity_id: Script entity ID to run (e.g., "script.morning_routine")
        variables: Optional variables to pass to the script
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and operation result
    """
    if not ha_config:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration required"
        }

    if not entity_id:
        return missing_parameter("entity_id")

    if variables:
        kwargs["variables"] = variables

    result = turn_on_device_impl(
        "script",
        entity_id,
        ha_config,
        correlation_id,
        **kwargs
    )

    if result.get("success"):
        return {
            "success": True,
            "entity_id": entity_id,
            "executed": True
        }
    return {
        "success": False,
        "error_code": result.get("error_code", "UNKNOWN_ERROR"),
        "error_message": result.get("error_message", "Failed to run script")
    }


# ===== EXPORTS =====

__all__ = [
    "run_script_impl",
]
