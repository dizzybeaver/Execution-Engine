"""ha_utilities.py
Version: 2026-04-11
Purpose: Utility and validation operations
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


# ===== Utility Wrappers =====


def validate_entity_id(entity_id: str, **kwargs) -> dict[str, Any]:
    """Validate entity ID format."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "validate_entity_id")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="validate_entity_id START", entity_id=entity_id)

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            validate_entity_id_impl,
        )
        result = validate_entity_id_impl(entity_id, **kwargs)
        _log_complete(correlation_id, "validate_entity_id", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "validate_entity_id", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "validate_entity_id", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "validate_entity_id", e)

    except Exception as e:
        return _log_error(correlation_id, "validate_entity_id", e)


def validate_device_id(device_id: str, **kwargs) -> dict[str, Any]:
    """Validate device ID format."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "validate_device_id")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="validate_device_id START", device_id=device_id)

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            validate_device_id_impl,
        )
        result = validate_device_id_impl(device_id, **kwargs)
        _log_complete(correlation_id, "validate_device_id", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "validate_device_id", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "validate_device_id", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "validate_device_id", e)

    except Exception as e:
        return _log_error(correlation_id, "validate_device_id", e)


def get_device_config(device_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get device configuration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_device_config")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_device_config START", device_id=device_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_device_config_impl,
        )
        result = get_device_config_impl(device_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_device_config", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_device_config", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_device_config", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_device_config", e)

    except Exception as e:
        return _log_error(correlation_id, "get_device_config", e)


def set_device_config(device_id: str, area_id: str = None, name_by_user: str = None,
                      oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Set device configuration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "set_device_config")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="set_device_config START", device_id=device_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            set_device_config_impl,
        )
        result = set_device_config_impl(device_id, area_id, name_by_user, oauth_token, **kwargs)
        _log_complete(correlation_id, "set_device_config", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "set_device_config", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "set_device_config", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "set_device_config", e)

    except Exception as e:
        return _log_error(correlation_id, "set_device_config", e)


def get_entity_config(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get entity configuration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_entity_config")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_entity_config START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_entity_config_impl,
        )
        result = get_entity_config_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_entity_config", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_entity_config", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_entity_config", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_entity_config", e)

    except Exception as e:
        return _log_error(correlation_id, "get_entity_config", e)


def set_entity_config(entity_id: str, area_id: str = None, name: str = None, icon: str = None,
                      disabled: bool = None, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Set entity configuration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "set_entity_config")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="set_entity_config START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            set_entity_config_impl,
        )
        result = set_entity_config_impl(entity_id, area_id, name, icon, disabled, oauth_token, **kwargs)
        _log_complete(correlation_id, "set_entity_config", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "set_entity_config", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "set_entity_config", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "set_entity_config", e)

    except Exception as e:
        return _log_error(correlation_id, "set_entity_config", e)


def get_integration_info(integration_domain: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get integration information."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_integration_info")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_integration_info START", integration_domain=integration_domain,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_integration_info_impl,
        )
        result = get_integration_info_impl(integration_domain, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_integration_info", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_integration_info", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_integration_info", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_integration_info", e)

    except Exception as e:
        return _log_error(correlation_id, "get_integration_info", e)


def reload_integration(integration_domain: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Reload an integration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "reload_integration")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="reload_integration START", integration_domain=integration_domain,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            reload_integration_impl,
        )
        result = reload_integration_impl(integration_domain, oauth_token, **kwargs)
        _log_complete(correlation_id, "reload_integration", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "reload_integration", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "reload_integration", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "reload_integration", e)

    except Exception as e:
        return _log_error(correlation_id, "reload_integration", e)


