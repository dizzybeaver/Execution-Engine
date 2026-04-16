"""ha_weather_wrappers.py
Version: 2026-03-18_1
Purpose: Weather interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Weather router.
External modules MUST use execute_weather_operation() instead of importing directly.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if weather core is available
try:
    from lee.home_assistant.ha_weather.ha_weather_core import (
        get_forecast_impl,
        get_forecasts_impl,
        get_state_impl,
        get_weather_impl,
        list_weather_entities_impl,
    )
    _WEATHER_AVAILABLE = True
    _WEATHER_IMPORT_ERROR = None
except ImportError as e:
    _WEATHER_AVAILABLE = False
    _WEATHER_IMPORT_ERROR = str(e)


def list_weather_entities(ha_config: Optional[dict[str, Any]] = None,
                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """List all weather entities."""
    correlation_id = generate_correlation_id("ha")

    if not _WEATHER_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_weather_entities FAILED - Weather core unavailable",
                         error=_WEATHER_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Weather core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="list_weather_entities START")

    try:
        result = list_weather_entities_impl(ha_config=ha_config,
                                           correlation_id=correlation_id,
                                           **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_weather_entities COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_weather_entities FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_WEATHER_ENTITIES_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="list_weather_entities FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "LIST_WEATHER_ENTITIES_FAILED",
        }


def get_forecast(entity_id: str, forecast_type: str,
                ha_config: Optional[dict[str, Any]] = None,
                oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get weather forecast."""
    correlation_id = generate_correlation_id("ha")

    if not _WEATHER_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecast FAILED - Weather core unavailable",
                         error=_WEATHER_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Weather core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_forecast START", entity_id=entity_id,
                     forecast_type=forecast_type)

    try:
        result = get_forecast_impl(entity_id=entity_id,
                                  forecast_type=forecast_type,
                                  ha_config=ha_config,
                                  correlation_id=correlation_id,
                                  **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecast COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecast FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_FORECAST_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecast FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_FORECAST_FAILED",
        }


def get_forecasts(entity_id: str,
                 ha_config: Optional[dict[str, Any]] = None,
                 oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get multiple weather forecasts."""
    correlation_id = generate_correlation_id("ha")

    if not _WEATHER_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecasts FAILED - Weather core unavailable",
                         error=_WEATHER_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Weather core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_forecasts START", entity_id=entity_id)

    try:
        result = get_forecasts_impl(entity_id=entity_id,
                                   ha_config=ha_config,
                                   correlation_id=correlation_id,
                                   **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecasts COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecasts FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_FORECASTS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_forecasts FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_FORECASTS_FAILED",
        }


def get_weather(entity_id: str,
               ha_config: Optional[dict[str, Any]] = None,
               oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get current weather data."""
    correlation_id = generate_correlation_id("ha")

    if not _WEATHER_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_weather FAILED - Weather core unavailable",
                         error=_WEATHER_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Weather core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_weather START", entity_id=entity_id)

    try:
        result = get_weather_impl(entity_id=entity_id,
                                 ha_config=ha_config,
                                 correlation_id=correlation_id,
                                 **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_weather COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_weather FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_WEATHER_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_weather FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_WEATHER_FAILED",
        }


def get_state(entity_id: str,
             ha_config: Optional[dict[str, Any]] = None,
             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get weather entity state with all attributes."""
    correlation_id = generate_correlation_id("ha")

    if not _WEATHER_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_state FAILED - Weather core unavailable",
                         error=_WEATHER_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Weather core not available",
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
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
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
