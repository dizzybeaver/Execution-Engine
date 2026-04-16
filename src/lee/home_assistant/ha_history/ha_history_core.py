# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-07 - Fixed pylint issues


"""ha_history_core.py - Home Assistant History Core Implementations
Version: 2025-12-22_1
Description: Core implementations for historical data access operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
)
from lee.home_assistant.utils import missing_parameter

# ===== HISTORY MANAGEMENT IMPLEMENTATIONS =====


# pylint: disable=too-many-arguments,too-many-positional-arguments
def get_history_during_period_impl(
    start_time: str,
    entity_ids: list[str],
    end_time: str = None,
    include_start_time_state: bool = True,
    significant_changes_only: bool = True,
    minimal_response: bool = False,
    no_attributes: bool = False,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Get historical state changes during a specific time period.

        start_time: Start time for history query (ISO 8601 format, required)
        entity_ids: List of entity IDs to query (required)
        end_time: End time for history query (ISO 8601 format, optional)
        include_start_time_state: Include state at start time (default True)
        significant_changes_only: Only return significant state changes (default True)
        minimal_response: Return minimal response format (default False)
        no_attributes: Exclude attributes from response (default False)
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status and history data
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_history_during_period",
        }

    if not start_time:
        return missing_parameter("start_time")

    if not entity_ids:
        return missing_parameter("entity_ids")

    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting history during period",
        corr_id=corr_id,
        start_time=start_time,
        end_time=end_time,
        entity_ids=entity_ids,
    )

    try:
        # Use WebSocket command: history/history_during_period
        request_data = {
            "start_time": start_time,
            "entity_ids": entity_ids,
            "include_start_time_state": include_start_time_state,
            "significant_changes_only": significant_changes_only,
            "minimal_response": minimal_response,
            "no_attributes": no_attributes,
        }

        if end_time is not None:
            request_data["end_time"] = end_time

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="history/history_during_period",
            ha_config=ha_config,
            request_data=request_data,
            correlation_id=corr_id,
        )

        if result.get("success"):
            history_data = result.get("result", {})
            return {
                "success": True,
                "history": history_data,
                "start_time": start_time,
                "end_time": end_time,
                "entity_ids": entity_ids,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get(
                "error_message", "Failed to get history during period"
            ),
            "start_time": start_time,
            "entity_ids": entity_ids,
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Network error getting history during period",
            corr_id=corr_id,
            start_time=start_time,
            end_time=end_time,
            entity_ids=entity_ids,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "start_time": start_time,
            "entity_ids": entity_ids,
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Data error getting history during period",
            corr_id=corr_id,
            start_time=start_time,
            end_time=end_time,
            entity_ids=entity_ids,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {str(e)}",
            "start_time": start_time,
            "entity_ids": entity_ids,
            "correlation_id": corr_id,
        }
    # pylint: disable=broad-exception-caught
    except Exception as e:
        ha_log_error(
            message="Unexpected error getting history during period",
            corr_id=corr_id,
            start_time=start_time,
            end_time=end_time,
            entity_ids=entity_ids,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {str(e)}",
            "start_time": start_time,
            "entity_ids": entity_ids,
            "correlation_id": corr_id,
        }
