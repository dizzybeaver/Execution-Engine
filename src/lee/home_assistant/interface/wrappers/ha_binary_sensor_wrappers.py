"""ha_binary_sensor_wrappers.py
Version: 2026-03-18_1
Purpose: Binary Sensor interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Binary Sensor router.
External modules MUST use execute_binary_sensor_operation() instead of importing directly.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if binary_sensor core is available
try:
    from lee.home_assistant.ha_binary_sensor.ha_binary_sensor_core import (
        get_state_impl,
        list_binary_sensors_impl,
        reload_binary_sensors_impl,
    )
    _BINARY_SENSOR_AVAILABLE = True
    _BINARY_SENSOR_IMPORT_ERROR = None
except ImportError as e:
    _BINARY_SENSOR_AVAILABLE = False
    _BINARY_SENSOR_IMPORT_ERROR = str(e)


def list_binary_sensors(ha_config: Optional[dict[str, Any]] = None,
                       oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """List all binary sensor entities."""
    correlation_id = generate_correlation_id("ha")

    if not _BINARY_SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_binary_sensors FAILED - Binary Sensor core unavailable",
                         error=_BINARY_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Binary Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="list_binary_sensors START")

    try:
        result = list_binary_sensors_impl(ha_config=ha_config,
                                         correlation_id=correlation_id,
                                         **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_binary_sensors COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_binary_sensors FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_BINARY_SENSORS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_binary_sensors FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "LIST_BINARY_SENSORS_FAILED",
        }


def reload_binary_sensors(ha_config: Optional[dict[str, Any]] = None,
                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Reload all binary sensors."""
    correlation_id = generate_correlation_id("ha")

    if not _BINARY_SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="reload_binary_sensors FAILED - Binary Sensor core unavailable",
                         error=_BINARY_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Binary Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="reload_binary_sensors START")

    try:
        result = reload_binary_sensors_impl(ha_config=ha_config,
                                           correlation_id=correlation_id,
                                           **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="reload_binary_sensors COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="reload_binary_sensors FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "RELOAD_BINARY_SENSORS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="reload_binary_sensors FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "RELOAD_BINARY_SENSORS_FAILED",
        }


def get_state(entity_id: str, ha_config: Optional[dict[str, Any]] = None,
             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get binary sensor state with attributes."""
    correlation_id = generate_correlation_id("ha")

    if not _BINARY_SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state FAILED - Binary Sensor core unavailable",
                         error=_BINARY_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Binary Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_state START", entity_id=entity_id)

    try:
        result = get_state_impl(entity_id=entity_id,
                               ha_config=ha_config,
                               correlation_id=correlation_id,
                               **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_STATE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_STATE_FAILED",
        }
