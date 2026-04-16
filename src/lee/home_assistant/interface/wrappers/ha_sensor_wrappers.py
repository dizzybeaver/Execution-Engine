"""ha_sensor_wrappers.py
Version: 2026-03-18_1
Purpose: Sensor interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Sensor router.
External modules MUST use execute_sensor_operation() instead of importing directly.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if sensor core is available
try:
    from lee.home_assistant.ha_sensor.ha_sensor_core import (
        get_device_class_units_impl,
        get_numeric_device_classes_impl,
        get_state_impl,
        get_value_impl,
        list_sensors_impl,
    )
    _SENSOR_AVAILABLE = True
    _SENSOR_IMPORT_ERROR = None
except ImportError as e:
    _SENSOR_AVAILABLE = False
    _SENSOR_IMPORT_ERROR = str(e)


def get_device_class_units(device_class: str, ha_config: Optional[dict[str, Any]] = None,
                           oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get convertible units for a sensor device class."""
    correlation_id = generate_correlation_id("ha")

    if not _SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_device_class_units FAILED - Sensor core unavailable",
                         error=_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_class_units START", device_class=device_class)

    try:
        result = get_device_class_units_impl(device_class=device_class,
                                            ha_config=ha_config,
                                            correlation_id=correlation_id,
                                            **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_device_class_units COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_device_class_units FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_DEVICE_CLASS_UNITS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_device_class_units FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_DEVICE_CLASS_UNITS_FAILED",
        }


def get_numeric_device_classes(ha_config: Optional[dict[str, Any]] = None,
                               oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get list of numeric sensor device classes."""
    correlation_id = generate_correlation_id("ha")

    if not _SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_numeric_device_classes FAILED - Sensor core unavailable",
                         error=_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_numeric_device_classes START")

    try:
        result = get_numeric_device_classes_impl(ha_config=ha_config,
                                                correlation_id=correlation_id,
                                                **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_numeric_device_classes COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_numeric_device_classes FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_NUMERIC_DEVICE_CLASSES_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_numeric_device_classes FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_NUMERIC_DEVICE_CLASSES_FAILED",
        }


def get_value(entity_id: str, ha_config: Optional[dict[str, Any]] = None,
             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get sensor value (state only)."""
    correlation_id = generate_correlation_id("ha")

    if not _SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_value FAILED - Sensor core unavailable",
                         error=_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_value START", entity_id=entity_id)

    try:
        result = get_value_impl(entity_id=entity_id,
                               ha_config=ha_config,
                               correlation_id=correlation_id,
                               **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_value COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_value FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_VALUE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_value FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_VALUE_FAILED",
        }


def get_state(entity_id: str, ha_config: Optional[dict[str, Any]] = None,
             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get sensor state with attributes."""
    correlation_id = generate_correlation_id("ha")

    if not _SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state FAILED - Sensor core unavailable",
                         error=_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Sensor core not available",
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


def list_sensors(ha_config: Optional[dict[str, Any]] = None,
                oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """List all sensor entities."""
    correlation_id = generate_correlation_id("ha")

    if not _SENSOR_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_sensors FAILED - Sensor core unavailable",
                         error=_SENSOR_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Sensor core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="list_sensors START")

    try:
        result = list_sensors_impl(ha_config=ha_config,
                                  correlation_id=correlation_id,
                                  **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_sensors COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_sensors FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_SENSORS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_sensors FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "LIST_SENSORS_FAILED",
        }
