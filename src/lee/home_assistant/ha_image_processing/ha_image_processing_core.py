# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-10 - Refactor to use ha_device_base functions and remove obsolete code


"""ha_image_processing_core.py - Core Implementation for Image Processing Interface

Version: 2026-04-10_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import list_devices_impl, turn_on_device_impl
from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils.error_response_factory import missing_parameter


# ===== CORE IMPLEMENTATIONS =====


def list_image_processing_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all image processing entities.

    Args:
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and image processing entities list
    """
    result = list_devices_impl("image_processing", ha_config, correlation_id, **_kwargs)

    if result.get("success"):
        return {
            "success": True,
            "image_processors": result.get("image_processing", []),
            "count": result.get("count", 0)
        }

    return result


def scan_image_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Trigger image scan.

    Args:
        entity_id: Image processing entity ID
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    result = turn_on_device_impl(
        "image_processing",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        service="scan",
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Image scan completed successfully"

    return result


def get_scan_results_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Get detection results from image scan.

    Args:
        entity_id: Image processing entity ID
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and scan results
    """
    if not entity_id:
        return missing_parameter("entity_id")

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "get_states",
            entity_id=entity_id,
            ha_config=ha_config,
            correlation_id=correlation_id
        )

        if result.get("success"):
            all_states = result.get("result", [])
            if all_states and len(all_states) > 0:
                state = all_states[0]
                attributes = state.get("attributes", {})
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "scan_results": {
                        "matches": attributes.get("matches", []),
                        "total_matches": attributes.get("total_matches", 0),
                        "last_scan": attributes.get("last_scan"),
                    }
                }

            return {
                "success": False,
                "error_code": "IMAGE_PROCESSOR_NOT_FOUND",
                "error_message": f"Image processor {entity_id} not found"
            }

        return {
            "success": False,
            "error_code": result.get("error_code", "UNKNOWN_ERROR"),
            "error_message": result.get("error_message", "Failed to get scan results")
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error getting scan results: {e!s}"
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error getting scan results: {e!s}"
        }
    except Exception:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": "Unexpected error getting scan results"
        }


def clear_scan_results_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Clear cached scan results.

    Args:
        entity_id: Image processing entity ID
        ha_config: Home Assistant configuration (url, token)
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    result = turn_on_device_impl(
        "image_processing",
        entity_id=entity_id,
        ha_config=ha_config,
        correlation_id=correlation_id,
        service="clear_scan",
        **_kwargs
    )

    if result.get("success"):
        result["message"] = "Scan results cleared successfully"

    return result


# ===== EXPORTS =====

__all__ = [
    "list_image_processing_impl",
    "scan_image_impl",
    "get_scan_results_impl",
    "clear_scan_results_impl",
]
