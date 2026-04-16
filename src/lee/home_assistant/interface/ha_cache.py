"""ha_cache.py - Router for Cache Interface

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter

# Import device cache operations
try:
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        get_diagnostic_info_impl as _get_diagnostic_info_impl,
    )
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        get_performance_report_impl as _get_performance_report_impl,
    )
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        invalidate_domain_cache_impl as _invalidate_domain_cache_impl,
    )
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        invalidate_entity_cache_impl as _invalidate_entity_cache_impl,
    )
    from lee.home_assistant.ha_cache.ha_devices_cache import (
        warm_cache_impl as _warm_cache_impl,
    )
    _DEVICES_CACHE_AVAILABLE = True
except ImportError:
    _DEVICES_CACHE_AVAILABLE = False

    # Create stub implementations
    def _warm_cache_impl(**kwargs):
        return {"success": False, "error": "Devices cache not available"}

    def _invalidate_entity_cache_impl(**kwargs):
        return {"success": False, "error": "Devices cache not available"}

    def _invalidate_domain_cache_impl(**kwargs):
        return {"success": False, "error": "Devices cache not available"}

    def _get_performance_report_impl(**kwargs):
        return {"success": False, "error": "Devices cache not available"}

    def _get_diagnostic_info_impl(**kwargs):
        return {"success": False, "error": "Devices cache not available"}

# Import state cache operations
try:
    from lee.home_assistant.ha_cache.ha_state_cache import (
        get_state_with_cache as _get_state_with_cache,
    )
    from lee.home_assistant.ha_cache.ha_state_cache import (
        get_states_batch_with_cache as _get_states_batch_with_cache,
    )
    _STATE_CACHE_AVAILABLE = True
except ImportError:
    _STATE_CACHE_AVAILABLE = False

    # Create stub implementations
    def _get_state_with_cache(**kwargs):
        return {"success": False, "error": "State cache not available"}

    def _get_states_batch_with_cache(**kwargs):
        return {"success": False, "error": "State cache not available"}

# Import cache invalidation operations
try:
    from lee.home_assistant.ha_cache.ha_cache_invalidators import (
        invalidate_on_service_call as _invalidate_on_service_call,
    )
    _INVALIDATORS_AVAILABLE = True
except ImportError:
    _INVALIDATORS_AVAILABLE = False

    # Create stub implementation
    def _invalidate_on_service_call(**kwargs):
        return {"success": False, "error": "Cache invalidators not available"}

# Import cache warming operations
try:
    from lee.home_assistant.ha_cache.ha_cache_warmer import (
        warm_entity_states_cache as _warm_entity_states_cache,
    )
    _WARMER_AVAILABLE = True
except ImportError:
    _WARMER_AVAILABLE = False

    # Create stub implementation
    def _warm_entity_states_cache(**kwargs):
        return {"success": False, "error": "Cache warmer not available"}

# Import Alexa cache operations
try:
    from lee.home_assistant.ha_cache.ha_alexa_cache_wrappers import (
        get_alexa_cache_state_impl as _get_alexa_cache_state_impl,
    )
    from lee.home_assistant.ha_cache.ha_alexa_cache_wrappers import (
        get_alexa_discovery_impl as _get_alexa_discovery_impl,
    )
    from lee.home_assistant.ha_cache.ha_alexa_cache_wrappers import (
        get_alexa_multiple_states_impl as _get_alexa_multiple_states_impl,
    )
    from lee.home_assistant.ha_cache.ha_alexa_cache_wrappers import (
        invalidate_alexa_entity_impl as _invalidate_alexa_entity_impl,
    )
    from lee.home_assistant.ha_cache.ha_alexa_cache_wrappers import (
        warm_alexa_cache_impl as _warm_alexa_cache_impl,
    )
    _ALEXA_CACHE_AVAILABLE = True
except ImportError:
    _ALEXA_CACHE_AVAILABLE = False

    # Create stub implementations
    def _get_alexa_cache_state_impl(**kwargs):
        return {"success": False, "error": "Alexa cache not available"}

    def _get_alexa_discovery_impl(**kwargs):
        return {"success": False, "error": "Alexa cache not available"}

    def _get_alexa_multiple_states_impl(**kwargs):
        return {"success": False, "error": "Alexa cache not available"}

    def _invalidate_alexa_entity_impl(**kwargs):
        return {"success": False, "error": "Alexa cache not available"}

    def _warm_alexa_cache_impl(**kwargs):
        return {"success": False, "error": "Alexa cache not available"}

# Dispatch dictionary for O(1) operation routing
_CACHE_DISPATCH = {
    # Device cache operations
    "warm_cache": _warm_cache_impl,
    "invalidate_entity_cache": _invalidate_entity_cache_impl,
    "invalidate_domain_cache": _invalidate_domain_cache_impl,
    "get_performance_report": _get_performance_report_impl,
    "get_diagnostic_info": _get_diagnostic_info_impl,
    # State cache operations
    "get_state_with_cache": _get_state_with_cache,
    "get_states_batch_with_cache": _get_states_batch_with_cache,
    # Cache invalidation operations
    "invalidate_on_service_call": _invalidate_on_service_call,
    # Cache warming operations
    "warm_entity_states_cache": _warm_entity_states_cache,
    # Alexa cache operations
    "get_alexa_entity_state": _get_alexa_cache_state_impl,
    "get_alexa_discovery": _get_alexa_discovery_impl,
    "get_alexa_multiple_states": _get_alexa_multiple_states_impl,
    "invalidate_alexa_entity": _invalidate_alexa_entity_impl,
    "warm_alexa_cache": _warm_alexa_cache_impl,
}


class _CacheRouter(BaseSimpleDispatchRouter):
    """Router for Cache interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Cache",
            core_module=DummyModule(),
            dispatch_map=_CACHE_DISPATCH
        )


_cache_router = _CacheRouter()


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """Execute cache operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The cache operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from cache implementation
    """
    return _cache_router.execute(operation, **kwargs)


def list_cache_operations() -> list[str]:
    """List all available cache operations."""
    return _cache_router.dispatch_map.keys()


__all__ = [
    "execute_cache_operation",
    "list_cache_operations",
    "_DEVICES_CACHE_AVAILABLE",
    "_STATE_CACHE_AVAILABLE",
    "_INVALIDATORS_AVAILABLE",
    "_WARMER_AVAILABLE",
    "_ALEXA_CACHE_AVAILABLE"
]
