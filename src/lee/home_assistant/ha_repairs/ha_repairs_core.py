"""ha_repairs_core.py - Home Assistant Repairs Core Implementations
Version: 2025-12-22_1
Description: Core implementations for system repairs and issue management

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

# ===== REPAIRS MANAGEMENT IMPLEMENTATIONS =====
from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
)


def list_issues_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """List all known repair issues.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters

    Returns:
        Dict with success status and list of issues
    """
    if ha_config is None:
        return {
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "list_issues",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Listing repair issues",
        corr_id=corr_id,
    )

    try:
        # Use WebSocket command: repairs/list_issues
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="repairs/list_issues",
            ha_config=ha_config,
            correlation_id=corr_id,
        )

        if result.get("success"):
            issues = result.get("result", [])
            return {
                "success": True,
                "issues": issues,
                "count": len(issues),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to list issues"),
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to list repair issues (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to list repair issues (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "correlation_id": corr_id,
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        ha_log_error(
            message="Failed to list repair issues",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception: {str(e)}",
            "correlation_id": corr_id,
        }


def get_issue_data_impl(
    domain: str,
    issue_id: str,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get detailed data for a specific repair issue.

    Args:
        domain: The domain of the issue
        issue_id: The issue ID to get data for
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters

    Returns:
        Dict with success status and issue data
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_issue_data",
        }

    if not domain:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "domain is required",
            "operation": "get_issue_data",
        }

    if not issue_id:
        return {
            "success": False,
            "error_message": "issue_id is required",
            "operation": "get_issue_data",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting repair issue data",
        corr_id=corr_id,
        domain=domain,
        issue_id=issue_id,
    )

    try:
        # Use WebSocket command: repairs/get_issue_data
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="repairs/get_issue_data",
            ha_config=ha_config,
            request_data={
                "domain": domain,
                "issue_id": issue_id,
            },
            correlation_id=corr_id,
        )

        if result.get("success"):
            issue_data = result.get("result", {})
            return {
                "success": True,
                "issue": issue_data,
                "domain": domain,
                "issue_id": issue_id,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get issue data"),
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to get repair issue data (validation error)",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get repair issue data (network error)",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        ha_log_error(
            message="Failed to get repair issue data",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }


def ignore_issue_impl(
    domain: str,
    issue_id: str,
    ignore: bool,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Ignore or unignore a repair issue.

    Args:
        domain: The domain of the issue
        issue_id: The issue ID to ignore/unignore
        ignore: True to ignore, False to unignore
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **_kwargs: Additional parameters

    Returns:
        Dict with success status and ignore result
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "ignore_issue",
        }

    if not domain:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "domain is required",
            "operation": "ignore_issue",
        }

    if not issue_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "operation": "ignore_issue",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Ignoring/unignoring repair issue",
        corr_id=corr_id,
        domain=domain,
        issue_id=issue_id,
        ignore=ignore,
    )

    try:
        # Use proper gateway pattern via ha_repairs_ignore_issue
        # pylint: disable=import-outside-toplevel
        from lee.home_assistant import ha_gateway

        result = ha_gateway.ha_repairs_ignore_issue(
            domain=domain,
            issue_id=issue_id,
            ignore=ignore,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "ignored": ignore,
                "domain": domain,
                "issue_id": issue_id,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to ignore issue"),
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to ignore/unignore repair issue (validation error)",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to ignore/unignore repair issue (network error)",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        ha_log_error(
            message="Failed to ignore/unignore repair issue",
            corr_id=corr_id,
            domain=domain,
            issue_id=issue_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Exception: {str(e)}",
            "domain": domain,
            "issue_id": issue_id,
            "correlation_id": corr_id,
        }
