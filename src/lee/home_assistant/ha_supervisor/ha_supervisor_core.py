"""ha_supervisor_core.py - Home Assistant Supervisor Core Implementations
Version: 2025-12-22_1
Description: Core implementations for supervisor management operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

# ===== SUPERVISOR INFO IMPLEMENTATIONS =====
from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
)
from lee.home_assistant.ha_protocol_utils import convert_to_websocket_url


def _convert_to_websocket_url(http_url: str) -> str:
    """Convert HTTP URL to WebSocket URL.

    Args:
        http_url: HTTP URL (e.g., http://10.10.10.5:8123)

    Returns:
        WebSocket URL (e.g., ws://10.10.10.5:8123/api/websocket)
    """
    if not http_url:
        return http_url

    # Convert HTTP protocol to WebSocket protocol
    ws_url = convert_to_websocket_url(http_url)

    # Add WebSocket endpoint if not present
    if not ws_url.endswith("/api/websocket"):
        ws_url = ws_url.rstrip("/") + "/api/websocket"

    return ws_url


def get_supervisor_info_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get supervisor information.

        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status and supervisor info
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_supervisor_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting supervisor info",
        corr_id=corr_id,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": "/supervisor/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

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
                "supervisor": info,
                "version": info.get("version"),
                "version_latest": info.get("version_latest"),
                "auto_update": info.get("auto_update"),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get supervisor info"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get supervisor info (network error)",
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
            message="Failed to get supervisor info (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }


def get_host_info_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get host information.
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status and host info
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_host_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting host info",
        corr_id=corr_id,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": "/host/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

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
                "host": info,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get host info"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get host info (network error)",
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
            message="Failed to get host info (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }


def get_core_info_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get Home Assistant Core information.

        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status and core info
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_core_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting core info",
        corr_id=corr_id,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": "/core/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

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
                "core": info,
                "version": info.get("version"),
                "version_latest": info.get("version_latest"),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get core info"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get core info (network error)",
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
            message="Failed to get core info (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }


def get_os_info_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get Operating System information.

        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

        Dict with success status and OS info
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_os_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting OS info",
        corr_id=corr_id,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": "/os/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

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
                "os": info,
                "version": info.get("version"),
                "version_latest": info.get("version_latest"),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get OS info"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get OS info (network error)",
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
            message="Failed to get OS info (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }


# ===== ADDON MANAGEMENT IMPLEMENTATIONS =====


def list_addons_impl(
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """List all available add-ons.

        ha_config: Home Assistant configuration dict with url and token
        **kwargs: Additional parameters

        Dict with success status and add-ons list
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "list_addons",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Listing add-ons",
        corr_id=corr_id,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": "/supervisor/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            supervisor_info = result.get("result", {})
            addons = supervisor_info.get("addons", [])
            return {
                "success": True,
                "addons": addons,
                "count": len(addons),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to list add-ons"),
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to list add-ons (network error)",
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
            message="Failed to list add-ons (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": corr_id,
        }


def get_addon_info_impl(
    addon_slug: str,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Get add-on information.

        addon_slug: The add-on slug/identifier
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking

        Dict with success status and add-on info
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "get_addon_info",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Getting add-on info",
        corr_id=corr_id,
        addon_slug=addon_slug,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": f"/addons/{addon_slug}/info",
            "method": "get",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

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
                "addon": info,
                "addon_slug": addon_slug,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to get add-on info"),
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to get add-on info (network error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to get add-on info (validation error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }


def start_addon_impl(
    addon_slug: str,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Start an add-on.

    Args:
        addon_slug: The add-on slug/identifier
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Dict with success status and operation result
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "start_addon",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Starting add-on",
        corr_id=corr_id,
        addon_slug=addon_slug,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": f"/addons/{addon_slug}/start",
            "method": "post",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "addon_slug": addon_slug,
                "started": True,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to start add-on"),
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to start add-on (network error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to start add-on (validation error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }


def stop_addon_impl(
    addon_slug: str,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Stop an add-on.

    Args:
        addon_slug: The add-on slug/identifier
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Dict with success status and operation result
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "stop_addon",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Stopping add-on",
        corr_id=corr_id,
        addon_slug=addon_slug,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": f"/addons/{addon_slug}/stop",
            "method": "post",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "addon_slug": addon_slug,
                "stopped": True,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to stop add-on"),
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to stop add-on (network error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to stop add-on (validation error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }


def restart_addon_impl(
    addon_slug: str,
    ha_config: dict[str, Any] = None,
    correlation_id: str = None,
    **_kwargs
) -> dict[str, Any]:
    """Restart an add-on.

    Args:
        addon_slug: The add-on slug/identifier
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Dict with success status and operation result
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "restart_addon",
        }


    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Restarting add-on",
        corr_id=corr_id,
        addon_slug=addon_slug,
    )

    try:
        # Construct WebSocket message for supervisor API
        ws_message = {
            "type": "supervisor/api",
            "endpoint": f"/addons/{addon_slug}/restart",
            "method": "post",
        }

        # Convert HTTP URL to WebSocket URL
        ws_url = _convert_to_websocket_url(ha_config.get("url"))

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            url=ws_url,
            message=ws_message,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "addon_slug": addon_slug,
                "restarted": True,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to restart add-on"),
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to restart add-on (network error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
            message="Failed to restart add-on (validation error)",
            corr_id=corr_id,
            addon_slug=addon_slug,
            error=str(e),
        )
        return {
            "success": False,
            "error_message": f"Validation error: {e}",
            "error_code": "VALIDATION_ERROR",
            "addon_slug": addon_slug,
            "correlation_id": corr_id,
        }
