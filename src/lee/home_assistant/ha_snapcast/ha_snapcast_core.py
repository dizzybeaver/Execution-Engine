"""ha_snapcast_core.py - Snapcast Multiroom Audio Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def snapshot_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Snapshot Snapcast client state.

    Args:
        entity_id: Snapcast media player entity ID (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="snapcast",
            service="snapshot",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {e}",
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": str(e),
        }


def restore_impl(entity_id=None, ha_config=None, correlation_id=None, **kwargs):
    """Restore Snapcast client state.

    Args:
        entity_id: Snapcast media player entity ID (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required",
        }

    service_data = {"entity_id": entity_id}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="snapcast",
            service="restore",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {e}",
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": str(e),
        }


def set_latency_impl(
    entity_id=None, latency=None, ha_config=None, correlation_id=None, **kwargs
):
    """Set Snapcast client latency.

    Args:
        entity_id: Snapcast media player entity ID (required)
        latency: Latency in ms 1-1000 (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entity_id or latency is None:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and latency are required",
        }

    service_data = {"entity_id": entity_id, "latency": latency}

    try:
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="snapcast",
            service="set_latency",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {e}",
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": str(e),
        }
