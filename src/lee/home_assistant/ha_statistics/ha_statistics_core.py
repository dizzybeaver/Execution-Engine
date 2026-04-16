"""ha_statistics_core.py - Statistics Interface Core Implementation

Version: 2026-04-10_1
Description: Core implementations for long-term statistics analytics

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""
# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to remove obsolete code and update imports


from collections.abc import Sequence
from typing import Any, Optional


from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)


# ===== CORE IMPLEMENTATIONS =====


def list_statistic_ids_impl(  # pylint: disable=too-many-return-statements
    statistic_type: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all available statistic IDs.

    Args:
        statistic_type: Filter by statistic type ("mean" or "sum")
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and list of statistic IDs
    """
    try:
        # Build request parameters
        request_params = {}
        if statistic_type:
            request_params["statistic_type"] = statistic_type

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/list_statistic_ids",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_ids": result.get("result", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to list statistic IDs")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error listing statistic IDs: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error listing statistic IDs: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception listing statistic IDs: {e!s}"
        }


def get_statistic_during_period_impl(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-return-statements
    statistic_id: str,
    start_time: str,
    end_time: Optional[str] = None,
    period: str = "hour",
    units: Optional[dict[str, str]] = None,
    types: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get statistics for a single statistic_id during a time period.

    Args:
        statistic_id: The statistic ID to query
        start_time: Start time in ISO format
        end_time: End time in ISO format (optional)
        period: Statistic period ("5minute", "hour", "day", "week", "month", "year")
        units: Unit conversion dictionary
        types: List of statistic types to return ("mean", "min", "max", "sum", "state", "change", "last_reset")
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and statistic data
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    if not start_time:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "start_time is required"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_id": statistic_id,
            "start_time": start_time,
            "period": period
        }

        if end_time:
            request_params["end_time"] = end_time

        if units:
            request_params["units"] = units

        if types:
            request_params["types"] = types

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/statistic_during_period",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "data": result.get("result", {})
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get statistic data")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting statistic data: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting statistic data: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting statistic data: {e!s}"
        }


def get_statistics_during_period_impl(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-return-statements
    statistic_ids: list[str],
    start_time: str,
    end_time: Optional[str] = None,
    period: str = "hour",
    units: Optional[dict[str, str]] = None,
    types: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get statistics for multiple statistic_ids during a time period.

    Args:
        statistic_ids: List of statistic IDs to query
        start_time: Start time in ISO format
        end_time: End time in ISO format (optional)
        period: Statistic period ("5minute", "hour", "day", "week", "month", "year")
        units: Unit conversion dictionary
        types: List of statistic types to return
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and statistics data for all requested IDs
    """
    if not statistic_ids or not isinstance(statistic_ids, Sequence):
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_ids must be a non-empty list"
        }

    if not start_time:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "start_time is required"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_ids": statistic_ids,
            "start_time": start_time,
            "period": period
        }

        if end_time:
            request_params["end_time"] = end_time

        if units:
            request_params["units"] = units

        if types:
            request_params["types"] = types

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/statistics_during_period",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_ids": statistic_ids,
                "data": result.get("result", {})
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get statistics data")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting statistics data: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting statistics data: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting statistics data: {e!s}"
        }


def get_statistics_metadata_impl(  # pylint: disable=too-many-return-statements
    statistic_ids: Optional[list[str]] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get metadata for statistics.

    Args:
        statistic_ids: List of statistic IDs to get metadata for (optional, returns all if None)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and statistics metadata
    """
    try:
        # Build request parameters
        request_params = {}
        if statistic_ids:
            request_params["statistic_ids"] = statistic_ids

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/get_statistics_metadata",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "metadata": result.get("result", {})
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get statistics metadata")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting statistics metadata: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting statistics metadata: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception getting statistics metadata: {e!s}"
        }


def update_statistics_metadata_impl(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-return-statements
    statistic_id: str,
    unit_of_measurement: Optional[str] = None,
    has_mean: Optional[bool] = None,
    has_sum: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Update metadata for a statistic.

    Args:
        statistic_id: The statistic ID to update
        unit_of_measurement: New unit of measurement
        has_mean: Whether this statistic has mean statistics
        has_sum: Whether this statistic has sum statistics
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    try:
        # Build request parameters
        request_params = {"statistic_id": statistic_id}

        if unit_of_measurement is not None:
            request_params["unit_of_measurement"] = unit_of_measurement

        if has_mean is not None:
            request_params["has_mean"] = has_mean

        if has_sum is not None:
            request_params["has_sum"] = has_sum

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/update_statistics_metadata",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "updated": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to update statistics metadata")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error updating statistics metadata: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error updating statistics metadata: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception updating statistics metadata: {e!s}"
        }


def change_statistics_unit_impl(  # pylint: disable=too-many-return-statements
    statistic_id: str,
    new_unit: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Change the unit of a statistic.

    Args:
        statistic_id: The statistic ID to change units for
        new_unit: The new unit of measurement
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    if not new_unit:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "new_unit is required"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_id": statistic_id,
            "new_unit": new_unit
        }

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/change_statistics_unit",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "new_unit": new_unit,
                "changed": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to change statistics unit")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error changing statistics unit: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error changing statistics unit: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception changing statistics unit: {e!s}"
        }


def clear_statistics_impl(  # pylint: disable=too-many-return-statements
    statistic_id: str,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Clear all statistics for a statistic_id.

    Args:
        statistic_id: The statistic ID to clear statistics for
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    try:
        # Build request parameters
        request_params = {"statistic_id": statistic_id}

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/clear_statistics",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "cleared": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to clear statistics")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error clearing statistics: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error clearing statistics: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception clearing statistics: {e!s}"
        }


def adjust_sum_statistics_impl(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-return-statements
    statistic_id: str,
    start_time: str,
    end_time: str,
    adjustment: float,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Adjust sum statistics for a period.

    Args:
        statistic_id: The statistic ID to adjust
        start_time: Start time in ISO format
        end_time: End time in ISO format
        adjustment: Adjustment value to add/subtract from sum statistics
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    if not start_time or not end_time:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "start_time and end_time are required"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_id": statistic_id,
            "start_time": start_time,
            "end_time": end_time,
            "adjustment": adjustment
        }

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/adjust_sum_statistics",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "adjusted": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to adjust sum statistics")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error adjusting sum statistics: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error adjusting sum statistics: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception adjusting sum statistics: {e!s}"
        }


def import_statistics_impl(  # pylint: disable=too-many-return-statements
    statistic_id: str,
    statistics: list[dict[str, Any]],
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Import external statistics.

    Args:
        statistic_id: The statistic ID to import data for
        statistics: List of statistic data to import
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    if not statistics or not isinstance(statistics, Sequence):
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistics must be a non-empty list"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_id": statistic_id,
            "statistics": statistics
        }

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/import_statistics",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "imported": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to import statistics")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error importing statistics: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error importing statistics: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception importing statistics: {e!s}"
        }


def validate_statistics_impl(  # pylint: disable=too-many-return-statements
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Validate statistics and find issues.

    Args:
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and validation issues
    """
    try:
        # Execute WebSocket command (no params needed)
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/validate_statistics",
            params={},
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "issues": result.get("result", [])
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to validate statistics")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error validating statistics: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error validating statistics: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception validating statistics: {e!s}"
        }


def update_statistics_issues_impl(  # pylint: disable=too-many-return-statements
    statistic_id: str,
    issues: list[dict[str, Any]],
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Update validation issues for statistics.

    Args:
        statistic_id: The statistic ID to update issues for
        issues: List of issue data to update
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not statistic_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "statistic_id is required"
        }

    if not issues or not isinstance(issues, Sequence):
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "issues must be a non-empty list"
        }

    try:
        # Build request parameters
        request_params = {
            "statistic_id": statistic_id,
            "issues": issues
        }

        # Execute WebSocket command
        result = ha_execute_operation(
            HAGatewayInterface.WEBSOCKET,
            "execute_command",
            command_type="recorder/update_statistics_issues",
            params=request_params,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            return {
                "success": True,
                "statistic_id": statistic_id,
                "updated": True
            }
        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to update statistics issues")
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error updating statistics issues: {e!s}"
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error updating statistics issues: {e!s}"
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception updating statistics issues: {e!s}"
        }


# ===== EXPORTS =====

__all__ = [
    "adjust_sum_statistics_impl",
    "change_statistics_unit_impl",
    "clear_statistics_impl",
    "get_statistic_during_period_impl",
    "get_statistics_during_period_impl",
    "get_statistics_metadata_impl",
    "import_statistics_impl",
    "list_statistic_ids_impl",
    "update_statistics_issues_impl",
    "update_statistics_metadata_impl",
    "validate_statistics_impl",
]
