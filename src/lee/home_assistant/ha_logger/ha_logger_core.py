# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


"""ha_logger_core.py - Logger Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for Logger integration

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


# ===== CORE IMPLEMENTATIONS =====


def get_log_info_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get logger information for all Home Assistant integrations.

    Retrieves the current log level settings for all loaded integrations
    and discovered config flows.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and logger information
    """
    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="logger/log_info",
            command_params={},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "loggers": result.get("result", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get log info")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting log info: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting log info: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception getting log info"
        }


def set_integration_log_level_impl(
    integration: str,
    level: str,
    persistence: bool = False,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set log level for a specific integration.

    Changes the logging verbosity for a specific Home Assistant integration.
    Log levels: critical, error, warning, info, debug

    Args:
        integration: Integration domain name (e.g., "light", "sensor")
        level: Log level (critical, error, warning, info, debug)
        persistence: Whether to make setting persistent across restarts
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and confirmation data
    """
    if not integration:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "integration is required"
        }

    if not level:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "level is required"
        }

    valid_levels = ["critical", "error", "warning", "info", "debug"]
    if level not in valid_levels:
        return {
            "success": False,
            "error_code": "INVALID_PARAMETER",
            "error_message": f"Invalid log level. Valid levels: {', '.join(valid_levels)}"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="logger/integration_log_level",
            command_params={
                "integration": integration,
                "level": level,
                "persistence": persistence
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "integration": integration,
                "level": level,
                "persistence": persistence,
                "log_level_updated": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to set integration log level")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error setting integration log level: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error setting integration log level: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception setting integration log level"
        }


def set_module_log_level_impl(
    module: str,
    level: str,
    persistence: bool = False,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Set log level for a specific module.

    Changes the logging verbosity for a specific Python module.
    This allows fine-grained control over logging for specific components.

    Args:
        module: Python module name (e.g., "homeassistant.components")
        level: Log level (critical, error, warning, info, debug)
        persistence: Whether to make setting persistent across restarts
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and confirmation data
    """
    if not module:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "module is required"
        }

    if not level:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "level is required"
        }

    valid_levels = ["critical", "error", "warning", "info", "debug"]
    if level not in valid_levels:
        return {
            "success": False,
            "error_code": "INVALID_PARAMETER",
            "error_message": f"Invalid log level. Valid levels: {', '.join(valid_levels)}"
        }

    try:
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="logger/log_level",
            command_params={
                "module": module,
                "level": level,
                "persistence": persistence
            },
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "module": module,
                "level": level,
                "persistence": persistence,
                "log_level_updated": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to set module log level")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error setting module log level: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error setting module log level: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Exception setting module log level"
        }


# ===== EXPORTS =====

__all__ = [
    "get_log_info_impl",
    "set_integration_log_level_impl",
    "set_module_log_level_impl",
]
