"""ha_service_calls.py
Version: 2026-04-11
Purpose: Service call operations (turn_on, turn_off, toggle, etc.)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Devices router.
External modules MUST use execute_devices_operation() instead of importing directly.
"""

from typing import Any

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import helper functions from device_helpers module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.device_helpers import (
    _core_unavailable_error,
    _log_complete,
    _log_error,
    _DEVICES_AVAILABLE,
)

# Import protection - only work if devices core is available
try:
    pass
except ImportError:
    pass  # Already handled in device_helpers


# ===== Service Call Wrappers =====


def batch_call(calls: list, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Execute multiple service calls in batch."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "batch_call")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="batch_call START", call_count=len(calls), has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            batch_call_impl,
        )
        result = batch_call_impl(calls, oauth_token, **kwargs)
        _log_complete(correlation_id, "batch_call", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "batch_call", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "batch_call", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "batch_call", e)

    except Exception as e:
        return _log_error(correlation_id, "batch_call", e)


def async_call_service(domain: str, service: str, entity_id: str = None,
                       service_data: dict = None, oauth_token: str = None,
                       **kwargs) -> dict[str, Any]:
    """Call HA service asynchronously."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "async_call_service")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="async_call_service START", domain=domain, service=service,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            async_call_service_impl,
        )
        result = async_call_service_impl(domain, service, entity_id, service_data, oauth_token, **kwargs)
        _log_complete(correlation_id, "async_call_service", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "async_call_service", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "async_call_service", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "async_call_service", e)

    except Exception as e:
        return _log_error(correlation_id, "async_call_service", e)


def turn_on(entity_id: str, brightness: int = None, color: str = None,
             transition: float = None, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Turn on a device."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "turn_on")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="turn_on START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import turn_on_impl
        result = turn_on_impl(entity_id, brightness, color, transition, oauth_token, **kwargs)
        _log_complete(correlation_id, "turn_on", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "turn_on", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "turn_on", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "turn_on", e)

    except Exception as e:
        return _log_error(correlation_id, "turn_on", e)


def turn_off(entity_id: str, transition: float = None, oauth_token: str = None,
             **kwargs) -> dict[str, Any]:
    """Turn off a device."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "turn_off")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="turn_off START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import turn_off_impl
        result = turn_off_impl(entity_id, transition, oauth_token, **kwargs)
        _log_complete(correlation_id, "turn_off", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "turn_off", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "turn_off", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "turn_off", e)

    except Exception as e:
        return _log_error(correlation_id, "turn_off", e)


def toggle(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Toggle a device state."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "toggle")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="toggle START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import toggle_impl
        result = toggle_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "toggle", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "toggle", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "toggle", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "toggle", e)

    except Exception as e:
        return _log_error(correlation_id, "toggle", e)


def set_value(entity_id: str, value: Any, attribute: str = None, oauth_token: str = None,
              **kwargs) -> dict[str, Any]:
    """Set a value for an entity."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "set_value")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="set_value START", entity_id=entity_id, value=value,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            set_value_impl,
        )
        result = set_value_impl(entity_id, value, attribute, oauth_token, **kwargs)
        _log_complete(correlation_id, "set_value", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "set_value", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "set_value", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "set_value", e)

    except Exception as e:
        return _log_error(correlation_id, "set_value", e)


def get_available_services(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all available services."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_available_services")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_available_services START", has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_available_services_impl,
        )
        result = get_available_services_impl(oauth_token, **kwargs)
        _log_complete(correlation_id, "get_available_services", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_available_services", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_available_services", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_available_services", e)

    except Exception as e:
        return _log_error(correlation_id, "get_available_services", e)


def get_service_schema(domain: str, service: str, oauth_token: str = None,
                       **kwargs) -> dict[str, Any]:
    """Get schema for a specific service."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_service_schema")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_service_schema START", domain=domain, service=service,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_service_schema_impl,
        )
        result = get_service_schema_impl(domain, service, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_service_schema", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_service_schema", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_service_schema", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_service_schema", e)

    except Exception as e:
        return _log_error(correlation_id, "get_service_schema", e)


def validate_service_call(domain: str, service: str, service_data: dict,
                          oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Validate a service call."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "validate_service_call")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="validate_service_call START", domain=domain, service=service,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            validate_service_call_impl,
        )
        result = validate_service_call_impl(domain, service, service_data, oauth_token, **kwargs)
        _log_complete(correlation_id, "validate_service_call", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "validate_service_call", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "validate_service_call", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "validate_service_call", e)

    except Exception as e:
        return _log_error(correlation_id, "validate_service_call", e)


def call_service_with_response(domain: str, service: str, entity_id: str = None,
                               service_data: dict = None, oauth_token: str = None,
                               **kwargs) -> dict[str, Any]:
    """Call service and wait for response."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "call_service_with_response")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="call_service_with_response START", domain=domain, service=service,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            call_service_with_response_impl,
        )
        result = call_service_with_response_impl(domain, service, entity_id, service_data,
                                                  oauth_token, **kwargs)
        _log_complete(correlation_id, "call_service_with_response", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "call_service_with_response", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "call_service_with_response", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "call_service_with_response", e)

    except Exception as e:
        return _log_error(correlation_id, "call_service_with_response", e)


