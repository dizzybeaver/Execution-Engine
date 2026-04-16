"""ha_state_management.py
Version: 2026-04-11
Purpose: State management operations (get_state, get_by_type, get_by_domain, etc.)
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


# ===== State Management Wrappers =====


def get_state(entity_id: str, use_cache: bool = True, oauth_token: str = None,
              **kwargs) -> dict[str, Any]:
    """Get state for a single entity with cache support."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_state")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_state START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        # Try cache first if enabled
        if use_cache:
            try:
                from lee.home_assistant.ha_cache.ha_state_cache import get_state_with_cache
                result = get_state_with_cache(entity_id, oauth_token=oauth_token,
                                            force_refresh=False, corr_id=correlation_id, **kwargs)

                if result.get("success"):
                    _log_complete(correlation_id, "get_state (cached)", True)
                    return result

                # Cache miss or error - fall through to API call
            except (ImportError, AttributeError) as cache_error:
                # Cache not available - fall through to API
                execute_operation(GatewayInterface.DEBUG, "log",
                                corr_id=correlation_id, scope="HOME_ASSISTANT",
                                message="get_state cache unavailable - using API",
                                error=str(cache_error))

        # Fallback to direct API call
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_state_impl,
        )
        result = get_state_impl(entity_id, use_cache=False, oauth_token=oauth_token, **kwargs)
        _log_complete(correlation_id, "get_state (API)", result.get("success", False))
        return result

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_state", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_state", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_state", e)

    except Exception as e:
        return _log_error(correlation_id, "get_state", e)


def get_by_type(entity_type: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all entities of a specific type."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_by_type")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_by_type START", entity_type=entity_type, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_by_type_impl,
        )
        result = get_by_type_impl(entity_type, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_by_type", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_by_type", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_by_type", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_by_type", e)

    except Exception as e:
        return _log_error(correlation_id, "get_by_type", e)


def get_by_domain(domain: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get all entities in a domain."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_by_domain")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_by_domain START", domain=domain, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_by_domain_impl,
        )
        result = get_by_domain_impl(domain, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_by_domain", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_by_domain", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_by_domain", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_by_domain", e)

    except Exception as e:
        return _log_error(correlation_id, "get_by_domain", e)


def refresh_state(entity_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Force refresh entity state."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "refresh_state")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="refresh_state START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            refresh_state_impl,
        )
        result = refresh_state_impl(entity_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "refresh_state", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "refresh_state", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "refresh_state", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "refresh_state", e)

    except Exception as e:
        return _log_error(correlation_id, "refresh_state", e)


def subscribe_to_events(event_type: str, callback: Any = None, oauth_token: str = None,
                         **kwargs) -> dict[str, Any]:
    """Subscribe to Home Assistant events."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "subscribe_to_events")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="subscribe_to_events START", event_type=event_type, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            subscribe_to_events_impl,
        )
        result = subscribe_to_events_impl(event_type, callback, oauth_token, **kwargs)
        _log_complete(correlation_id, "subscribe_to_events", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "subscribe_to_events", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "subscribe_to_events", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "subscribe_to_events", e)

    except Exception as e:
        return _log_error(correlation_id, "subscribe_to_events", e)


def unsubscribe_from_events(subscription_id: str, oauth_token: str = None,
                             **kwargs) -> dict[str, Any]:
    """Unsubscribe from Home Assistant events."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "unsubscribe_from_events")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="unsubscribe_from_events START", subscription_id=subscription_id,
                     has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            unsubscribe_from_events_impl,
        )
        result = unsubscribe_from_events_impl(subscription_id, oauth_token, **kwargs)
        _log_complete(correlation_id, "unsubscribe_from_events", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "unsubscribe_from_events", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "unsubscribe_from_events", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "unsubscribe_from_events", e)

    except Exception as e:
        return _log_error(correlation_id, "unsubscribe_from_events", e)


def get_history(entity_id: str = None, start_time: str = None, end_time: str = None,
                oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get historical state data."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "get_history")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_history START", entity_id=entity_id, has_token=bool(oauth_token))

    try:
        from lee.home_assistant.ha_devices.ha_devices_core_extended import (
            get_history_impl,
        )
        result = get_history_impl(entity_id, start_time, end_time, oauth_token, **kwargs)
        _log_complete(correlation_id, "get_history", result.get("success", False))
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return _log_error(correlation_id, "get_history", e)

    except (ConnectionError, TimeoutError, OSError) as e:
        return _log_error(correlation_id, "get_history", e)

    except (ImportError, ModuleNotFoundError) as e:
        return _log_error(correlation_id, "get_history", e)

    except Exception as e:
        return _log_error(correlation_id, "get_history", e)


