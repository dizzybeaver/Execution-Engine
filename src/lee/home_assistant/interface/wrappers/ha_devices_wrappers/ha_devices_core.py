"""ha_devices_core.py
Version: 2026-04-11
Purpose: Core device wrappers (factory-generated, batch, cache, config)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Devices router.
External modules MUST use execute_devices_operation() instead of importing directly.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import helper functions from device_helpers module
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.device_helpers import (
    _resolve_oauth_token,
    _create_device_wrapper,
    _DEVICES_AVAILABLE,
    _DEVICES_IMPORT_ERROR,
)

# Import protection - only work if devices core is available
try:
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        get_diagnostic_info_impl,
        get_performance_report_impl,
        invalidate_domain_cache_impl,
        invalidate_entity_cache_impl,
        warm_cache_impl,
    )
    from lee.home_assistant.ha_devices.ha_devices_generic import (
        call_service_batch_impl,
        call_service_impl,
        check_status_impl,
        find_fuzzy_impl,
        get_by_id_impl,
        get_states_batch_impl,
        get_states_impl,
        list_by_domain_impl,
        update_state_impl,
    )
    from lee.home_assistant.ha_devices.ha_devices_helpers import (
        call_ha_api_impl,
        get_ha_config_impl,
    )
except ImportError:
    pass  # Already handled in device_helpers


# Factory-generated wrapper for get_states
get_states = _create_device_wrapper(
    get_states_impl,
    "get_states",
    log_params=["entity_ids", "use_cache"]
)
get_states.__doc__ = """Get entity states."""
get_states.__annotations__ = {
    "entity_ids": "Optional[list[str]]",
    "use_cache": "bool",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}


# Factory-generated wrapper for get_by_id
get_by_id = _create_device_wrapper(
    get_by_id_impl,
    "get_by_id",
    log_params=["entity_id"]
)
get_by_id.__doc__ = """Get device by ID."""
get_by_id.__annotations__ = {
    "entity_id": "str",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}


def find_fuzzy(search_name: str, threshold: float = 0.6,
                oauth_token: str = None, **kwargs) -> Optional[str]:
    """Find device via fuzzy matching."""
    correlation_id = generate_correlation_id("ha")

    resolved_token = _resolve_oauth_token(oauth_token)

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="find_fuzzy FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return None

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="find_fuzzy START", search_name=search_name,
                     threshold=threshold, has_token=bool(resolved_token))

    try:
        result = find_fuzzy_impl(search_name, threshold, oauth_token=resolved_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="find_fuzzy COMPLETE", found=bool(result))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="find_fuzzy FAILED", error=str(e))
        return None
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="find_fuzzy FAILED with unexpected error", error=str(e))
        return None


# Factory-generated wrapper for update_state
update_state = _create_device_wrapper(
    update_state_impl,
    "update_state",
    log_params=["entity_id"]
)
update_state.__doc__ = """Update device state."""
update_state.__annotations__ = {
    "entity_id": "str",
    "state_data": "dict[str, Any]",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}


# Factory-generated wrapper for call_service
_call_service_base = _create_device_wrapper(
    call_service_impl,
    "call_service",
    log_params=["domain", "service", "entity_id"]
)
_call_service_base.__doc__ = """Call HA service."""
_call_service_base.__annotations__ = {
    "domain": "str",
    "service": "str",
    "entity_id": "Optional[str]",
    "service_data": "Optional[dict]",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}


def call_service(domain: str, service: str, entity_id: Optional[str] = None,
                service_data: Optional[dict] = None, oauth_token: str = None,
                **kwargs) -> dict[str, Any]:
    """Call HA service with cache invalidation.

    Args:
        domain: Service domain (e.g., "light", "switch")
        service: Service name (e.g., "turn_on", "toggle")
        entity_id: Target entity ID
        service_data: Service data dict
        oauth_token: OAuth token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        return _core_unavailable_error(correlation_id, "call_service")

    # Call base service
    result = _call_service_base(
        domain=domain,
        service=service,
        entity_id=entity_id,
        service_data=service_data,
        oauth_token=oauth_token,
        **kwargs
    )

    # Invalidate cache on successful service call
    if result.get("success"):
        try:
            from lee.home_assistant.ha_cache.ha_cache_invalidators import invalidate_on_service_call

            # Prepare service data for invalidation
            invalidation_data = service_data or {}
            if entity_id:
                invalidation_data = dict(invalidation_data, entity_id=entity_id)

            invalidate_on_service_call(
                domain=domain,
                service=service,
                service_data=invalidation_data,
                corr_id=correlation_id
            )

        except (ImportError, AttributeError) as cache_error:
            # Cache invalidation not available - non-fatal
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HOME_ASSISTANT",
                            message="call_service cache invalidation unavailable",
                            error=str(cache_error))

    return result


# Factory-generated wrapper for list_by_domain
list_by_domain = _create_device_wrapper(
    list_by_domain_impl,
    "list_by_domain",
    log_params=["domain"]
)
list_by_domain.__doc__ = """List devices by domain."""
list_by_domain.__annotations__ = {
    "domain": "str",
    "oauth_token": "Optional[str]",
    "return": "dict[str, Any]"
}


def check_status(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Check HA connection status."""
    correlation_id = generate_correlation_id("ha")

    if not oauth_token:
        from lee.home_assistant.ha_config import get_ha_config
        config = get_ha_config()
        if config and config.HOME_ASSISTANT_API_KEY:
            oauth_token = config.HOME_ASSISTANT_API_KEY

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_status FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="check_status START", has_token=bool(oauth_token))

    try:
        result = check_status_impl(oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_status COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_status FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "CHECK_STATUS_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_status FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "CHECK_STATUS_FAILED",
        }


def call_ha_api(endpoint: str, method: str = "GET", data: Optional[dict] = None,
                  oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Call HA API directly."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_ha_api FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="call_ha_api START", endpoint=endpoint, method=method,
                     has_token=bool(oauth_token))

    try:
        result = call_ha_api_impl(endpoint, method, data, oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_ha_api COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_ha_api FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "CALL_HA_API_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_ha_api FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "CALL_HA_API_FAILED",
        }


def get_ha_config(force_reload: bool = False, **kwargs) -> dict[str, Any]:
    """Get HA configuration."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_ha_config FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_ha_config START", force_reload=force_reload)

    try:
        result = get_ha_config_impl(force_reload, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_ha_config COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_ha_config FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_HA_CONFIG_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_ha_config FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_HA_CONFIG_FAILED",
        }


def warm_cache(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Pre-warm cache."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="warm_cache FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="warm_cache START", has_token=bool(oauth_token))

    try:
        result = warm_cache_impl(oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="warm_cache COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="warm_cache FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "WARM_CACHE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="warm_cache FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "WARM_CACHE_FAILED",
        }


def invalidate_entity_cache(entity_id: str, **kwargs) -> bool:
    """Invalidate entity cache."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_entity_cache FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return False

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="invalidate_entity_cache START", entity_id=entity_id)

    try:
        result = invalidate_entity_cache_impl(entity_id, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_entity_cache COMPLETE", success=result)
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_entity_cache FAILED", error=str(e))
        return False
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_entity_cache FAILED with unexpected error", error=str(e))
        return False


def invalidate_domain_cache(domain: str, **kwargs) -> int:
    """Invalidate domain cache."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_domain_cache FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return 0

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="invalidate_domain_cache START", domain=domain)

    try:
        result = invalidate_domain_cache_impl(domain, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_domain_cache COMPLETE", invalidated_count=result)
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_domain_cache FAILED", error=str(e))
        return 0
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="invalidate_domain_cache FAILED with unexpected error", error=str(e))
        return 0


def get_performance_report(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get performance report."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_performance_report FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_performance_report START", has_token=bool(oauth_token))

    try:
        result = get_performance_report_impl(oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_performance_report COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_performance_report FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_PERFORMANCE_REPORT_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_performance_report FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_PERFORMANCE_REPORT_FAILED",
        }


def get_diagnostic_info(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get diagnostic info."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_diagnostic_info FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_diagnostic_info START", has_token=bool(oauth_token))

    try:
        result = get_diagnostic_info_impl(oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_diagnostic_info COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_diagnostic_info FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_diagnostic_info FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
        }


# ===== BATCH OPERATION WRAPPERS =====


def get_states_batch(entity_ids: list[str], use_cache: bool = True,
                    oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get multiple entity states in batch."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_states_batch FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_states_batch START", entity_count=len(entity_ids),
                     use_cache=use_cache, has_token=bool(oauth_token))

    try:
        result = get_states_batch_impl(entity_ids, use_cache, oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_states_batch COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_states_batch FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_STATES_BATCH_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_states_batch FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_STATES_BATCH_FAILED",
        }


def call_service_batch(domain: str, service: str, entity_ids: list[str],
                      service_data: Optional[dict] = None, oauth_token: str = None,
                      **kwargs) -> dict[str, Any]:
    """Call service for multiple entities in batch."""
    correlation_id = generate_correlation_id("ha")

    if not _DEVICES_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_service_batch FAILED - Devices core unavailable",
                         error=_DEVICES_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Devices core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="call_service_batch START", domain=domain, service=service,
                     entity_count=len(entity_ids), has_token=bool(oauth_token))

    try:
        result = call_service_batch_impl(domain, service, entity_ids, service_data,
                                        oauth_token=oauth_token, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_service_batch COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_service_batch FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "CALL_SERVICE_BATCH_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="call_service_batch FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "CALL_SERVICE_BATCH_FAILED",
        }
