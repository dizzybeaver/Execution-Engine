"""device_helpers.py
Version: 2026-04-06
Purpose: Helper functions for device wrappers
License: Apache 2.0

This module contains helper functions used by device wrapper modules.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if devices core is available
try:
    from lee.home_assistant.ha_cache.ha_devices_cache import (  # noqa: F401
        get_diagnostic_info_impl,
        get_performance_report_impl,
        invalidate_domain_cache_impl,
        invalidate_entity_cache_impl,
        warm_cache_impl,
    )
    from lee.home_assistant.ha_devices.ha_devices_generic import (  # noqa: F401
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
    from lee.home_assistant.ha_devices.ha_devices_helpers import (  # noqa: F401
        call_ha_api_impl,
        get_ha_config_impl,
    )
    _DEVICES_AVAILABLE = True
    _DEVICES_IMPORT_ERROR = None
except ImportError as e:
    _DEVICES_AVAILABLE = False
    _DEVICES_IMPORT_ERROR = str(e)


def _core_unavailable_error(correlation_id: str, operation: str) -> dict[str, Any]:
    """Return standardized error when core unavailable."""
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message=f"{operation} FAILED - Devices core unavailable",
                     error=_DEVICES_IMPORT_ERROR)
    return {
        "success": False,
        "error": "Devices core not available",
        "error_code": "CORE_UNAVAILABLE",
    }


def _log_complete(correlation_id: str, operation: str, success: bool) -> None:
    """Log operation completion."""
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message=f"{operation} COMPLETE", success=success)


def _log_error(correlation_id: str, operation: str, error: Exception) -> dict[str, Any]:
    """Log operation error."""
    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message=f"{operation} FAILED", error=str(error))
    return {
        "success": False,
        "error": str(error),
        "error_code": f"{operation.upper()}_FAILED",
    }


def _resolve_oauth_token(oauth_token: Optional[str]) -> Optional[str]:
    """Resolve OAuth token from parameter or config."""
    if oauth_token:
        return oauth_token
    from lee.home_assistant.ha_config import get_ha_config
    config = get_ha_config()
    return config.HOME_ASSISTANT_API_KEY if config and config.HOME_ASSISTANT_API_KEY else None


def _create_device_wrapper(impl_func, operation_name: str, log_params: Optional[list[str]] = None):
    """Factory function to eliminate 800+ lines of duplication.

    Args:
        impl_func: The implementation function to wrap
        operation_name: Name of the operation for logging
        log_params: Optional list of parameter names to log

    Returns:
        Wrapped function with common OAuth resolution, availability check, and error handling
    """
    def wrapper(*args, oauth_token: str = None, **kwargs):
        correlation_id = generate_correlation_id("ha")

        # Common OAuth resolution
        resolved_token = _resolve_oauth_token(oauth_token)

        # Common availability check
        if not _DEVICES_AVAILABLE:
            return _core_unavailable_error(correlation_id, operation_name)

        # Extract log parameters
        log_context = {}
        if log_params:
            for i, param_name in enumerate(log_params):
                if i < len(args):
                    log_context[param_name] = args[i]

        log_context["has_token"] = bool(resolved_token)

        # Log operation start
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message=f"{operation_name} START", **log_context)

        try:
            # Call implementation with resolved token
            result = impl_func(*args, oauth_token=resolved_token, **kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message=f"{operation_name} COMPLETE",
                             success=result.get("success", False))
            return result
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
            return _log_error(correlation_id, operation_name, e)
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message=f"{operation_name} FAILED with unexpected error", error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": f"{operation_name.upper()}_FAILED",
            }

    return wrapper
