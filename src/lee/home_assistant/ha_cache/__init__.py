# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Home Assistant cache operations with state caching

"""ha_cache - Home Assistant cache management

Provides caching operations for device states, entity states,
cache invalidation, and cache warming.
"""

from lee.home_assistant.ha_cache.ha_devices_cache import (
    get_diagnostic_info_impl,
    get_performance_report_impl,
    invalidate_domain_cache_impl,
    invalidate_entity_cache_impl,
    warm_cache_impl,
)

from lee.home_assistant.ha_cache.ha_state_cache import (
    get_state_with_cache,
    get_states_batch_with_cache,
)

from lee.home_assistant.ha_cache.ha_cache_invalidators import (
    invalidate_on_service_call,
    is_domain_wide_service,
)

from lee.home_assistant.ha_cache.ha_cache_warmer import (
    warm_entity_states_cache,
    warm_discovered_entities,
)

__all__ = [
    # Device cache operations
    "get_diagnostic_info_impl",
    "get_performance_report_impl",
    "invalidate_domain_cache_impl",
    "invalidate_entity_cache_impl",
    "warm_cache_impl",
    # State cache operations
    "get_state_with_cache",
    "get_states_batch_with_cache",
    # Cache invalidation operations
    "invalidate_on_service_call",
    "is_domain_wide_service",
    # Cache warming operations
    "warm_entity_states_cache",
    "warm_discovered_entities",
]
