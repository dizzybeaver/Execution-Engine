# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_energy_core.py - Home Assistant Energy Core Implementations
Version: 2025-12-22_1
Description: Core implementations for energy management operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Any

# ===== ENERGY MANAGEMENT IMPLEMENTATIONS =====
from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
)
from lee.lee_security import InputSanitizer, SanitizeLevel


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def _convert_to_websocket_url(http_url: str) -> str:
    """Convert HTTP URL to WebSocket URL.

    Args:
        http_url: HTTP URL (e.g., http://10.10.10.5:8123)

    Returns:
        WebSocket URL (e.g., ws://10.10.10.5:8123/api/websocket)
    """
    if not http_url:
        return http_url

    # Convert protocol (single check, faster than chained replace)
    # Import shared utility for protocol conversion
    from lee.home_assistant.ha_protocol_utils import convert_to_websocket_url  # pylint: disable=import-outside-toplevel

    # Convert HTTP protocol to WebSocket protocol
    ws_url = convert_to_websocket_url(http_url)

    if not ws_url.endswith("/api/websocket"):
        ws_url = ws_url.rstrip("/") + "/api/websocket"

    return ws_url


def get_energy_preferences_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Get energy preferences.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and energy preferences
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_energy_preferences",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting energy preferences",
        corr_id=corr_id,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/preferences",
        }

        if _is_debug_mode():
            print(f"[ENERGY DEBUG] Calling WebSocket with url={ws_url}")

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            preferences = result.get("result", {})
            return {
                "success": True,
                "preferences": preferences,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get energy preferences"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get energy preferences (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to get energy preferences (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to get energy preferences",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def save_energy_preferences_impl(  # pylint: disable=too-many-arguments
    energy_sources: list[dict[str, Any]] = None,
    device_consumption: list[dict[str, Any]] = None,
    device_consumption_water: list[dict[str, Any]] = None,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Save energy preferences.

    Args:
        energy_sources: List of energy source configurations
        device_consumption: List of device consumption configurations
        device_consumption_water: List of water device consumption configurations
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and updated preferences
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "save_energy_preferences",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Saving energy preferences",
        corr_id=corr_id,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        request_data = {}
        if energy_sources is not None:
            request_data["energy_sources"] = energy_sources
        if device_consumption is not None:
            request_data["device_consumption"] = device_consumption
        if device_consumption_water is not None:
            request_data["device_consumption_water"] = device_consumption_water

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/preferences",
            "method": "post",
            "data": request_data,
        }

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            preferences = result.get("result", {})
            return {
                "success": True,
                "preferences": preferences,
                "saved": True,
                "correlation_id": corr_id,
            }
        else:
            return {
                "success": False,
                "error_message": result.get("error_message", "Failed to save energy preferences"),
                "correlation_id": corr_id,
            }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to save energy preferences (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to save energy preferences (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to save energy preferences",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def get_energy_info_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Get energy information.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and energy information
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_energy_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting energy info",
        corr_id=corr_id,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/info",
        }

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            info = result.get("result", {})
            return {
                "success": True,
                "info": info,
                "correlation_id": corr_id,
            }
        else:
            return {
                "success": False,
                "error_message": result.get("error_message", "Failed to get energy info"),
                "correlation_id": corr_id,
            }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get energy info (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to get energy info (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to get energy info",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def validate_energy_config_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Validate energy configuration.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and validation results
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "validate_energy_config",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Validating energy configuration",
        corr_id=corr_id,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/config/validate",
        }

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            validation = result.get("result", {})
            return {
                "success": True,
                "validation": validation,
                "correlation_id": corr_id,
            }
        else:
            return {
                "success": False,
                "error_message": result.get("error_message", "Failed to validate energy config"),
                "correlation_id": corr_id,
            }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to validate energy config (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to validate energy config (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to validate energy config",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def get_solar_forecast_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Get solar forecast.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and solar forecast data
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_solar_forecast",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting solar forecast",
        corr_id=corr_id,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/solar_forecast",
        }

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            forecast = result.get("result", {})
            return {
                "success": True,
                "forecast": forecast,
                "correlation_id": corr_id,
            }
        else:
            return {
                "success": False,
                "error_message": result.get("error_message", "Failed to get solar forecast"),
                "correlation_id": corr_id,
            }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get solar forecast (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to get solar forecast (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to get solar forecast",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def get_fossil_energy_consumption_impl(  # pylint: disable=too-many-arguments,too-many-return-statements
    start_time: str,
    end_time: str,
    energy_statistic_ids: list[str],
    co2_statistic_id: str,
    period: str = "hour",
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    _kwargs=None
) -> dict[str, Any]:
    """Get fossil fuel energy consumption.

    Args:
        start_time: Start time (ISO format string)
        end_time: End time (ISO format string)
        energy_statistic_ids: List of energy statistic IDs
        co2_statistic_id: CO2 statistic ID
        period: Period for aggregation (5minute, hour, day, month)
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        _kwargs: Additional parameters (unused)

    Returns:
        Dict with success status and fossil energy consumption data
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_fossil_energy_consumption",
        }

    if not start_time or not start_time.strip() or not end_time or not end_time.strip():
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "start_time and end_time are required and cannot be empty",
            "operation": "get_fossil_energy_consumption",
        }

    if not energy_statistic_ids or not co2_statistic_id or not co2_statistic_id.strip():
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "energy_statistic_ids and co2_statistic_id are required and cannot be empty",
            "operation": "get_fossil_energy_consumption",
        }

    if period not in ["5minute", "hour", "day", "month"]:
        return {
            "success": False,
            "error_code": "INVALID_PARAMETER",
            "error_message": "period must be one of: 5minute, hour, day, month",
            "operation": "get_fossil_energy_consumption",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting fossil energy consumption",
        corr_id=corr_id,
        start_time=start_time,
        end_time=end_time,
    )

    try:
        raw_url = ha_config.get("url", "")
        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        sanitized_url = sanitizer.sanitize_url(raw_url)
        ws_url = _convert_to_websocket_url(sanitized_url)

        request_data = {
            "start_time": start_time,
            "end_time": end_time,
            "energy_statistic_ids": energy_statistic_ids,
            "co2_statistic_id": co2_statistic_id,
            "period": period,
        }

        ws_message = {
            "type": "energy",
            "endpoint": "/energy/fossil_energy_consumption",
            "method": "get",
            "data": request_data,
        }

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            consumption = result.get("result", {})
            return {
                "success": True,
                "consumption": consumption,
                "period": period,
                "correlation_id": corr_id,
            }
        else:
            return {
                "success": False,
                "error_message": result.get("error_message", "Failed to get fossil energy consumption"),
                "correlation_id": corr_id,
            }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get fossil energy consumption (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to get fossil energy consumption (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }
    except Exception as e:
        ha_log_error(
            message="Failed to get fossil energy consumption",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }
