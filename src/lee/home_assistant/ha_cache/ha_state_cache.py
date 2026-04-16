# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Core state caching implementation

"""Home Assistant state caching module.

Provides intelligent caching for device states with domain-specific TTLs,
battery sensor special handling, and seamless SUGA-ISP integration.
"""

from typing import Any, Optional
import time

try:
    from lee.gateway import execute_operation, GatewayInterface
    from lee.home_assistant.ha_gateway import ha_execute_operation, HAGatewayInterface
    from lee.interface.wrappers.cache_wrappers import cache_get, cache_set, cache_delete
except ImportError:
    # Fallback for testing
    execute_operation = None
    GatewayInterface = None
    ha_execute_operation = None
    HAGatewayInterface = None

try:
    cache_get  # noqa: F821
    cache_set  # noqa: F821
    cache_delete  # noqa: F821
except NameError:
    # Fallback for testing when cache_wrappers not available
    def cache_get(key, correlation_id=None):
        return None
    def cache_set(key, value, ttl=None, correlation_id=None, **kwargs):
        pass
    def cache_delete(key, correlation_id=None):
        pass

from lee.home_assistant.ha_cache.ha_state_ttl import calculate_entity_ttl, is_entry_expired


def get_state_with_cache(
    entity_id: str,
    oauth_token: Optional[str] = None,
    force_refresh: bool = False,
    **kwargs
) -> dict[str, Any]:
    """Get entity state with intelligent cache lookup.

    Flow:
    1. Check cache for valid entry
    2. If cache hit and not force_refresh:
       - Update access statistics
       - Return cached state
    3. If cache miss or force_refresh:
       - Fetch from Home Assistant API
       - Cache the result with appropriate TTL
       - Return fresh state

    Args:
        entity_id: Entity ID (e.g., "light.office")
        oauth_token: OAuth token for HA API
        force_refresh: Force cache bypass
        **kwargs: Additional parameters

    Returns:
        Dict with:
        - success: bool
        - state: dict (the entity state)
        - source: str ("cache" or "fresh")
        - cached_at: float (if from cache)
    """
    cache_key = f"HA_STATE:{entity_id}"
    correlation_id = kwargs.get("corr_id")

    # Check cache if not forcing refresh
    if not force_refresh:
        cached_entry = cache_get(cache_key)
        if cached_entry and not is_entry_expired(cached_entry):
            return {
                "success": True,
                "state": cached_entry.value,
                "source": "cache",
                "cached_at": cached_entry.timestamp
            }

    # Cache miss or force refresh - fetch from HA
    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        'get_state',
        entity_id=entity_id,
        oauth_token=oauth_token,
        use_cache=False,  # Prevent infinite loop
        **kwargs
    )

    if result.get("success"):
        state = result.get("state")

        # Determine appropriate TTL
        ttl = calculate_entity_ttl(state)

        # Cache the result
        cache_set(
            cache_key,
            state,
            ttl=ttl,
            source_module="ha_state_cache"
        )

        if execute_operation:
            execute_operation(
                GatewayInterface.LOGGING,
                'log_debug',
                message=f'Cached state for {entity_id} with TTL {ttl}s',
                corr_id=correlation_id
            )

    return result


def get_states_batch_with_cache(
    entity_ids: list[str],
    oauth_token: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Batch state retrieval with cache optimization.

    Flow:
    1. Check cache for all entities
    2. Identify cache misses
    3. Batch fetch only misses from HA
    4. Merge cached and fresh results
    5. Update cache with fresh results

    Args:
        entity_ids: List of entity IDs
        oauth_token: OAuth token for HA API
        **kwargs: Additional parameters

    Returns:
        Dict with:
        - success: bool
        - states: dict[entity_id, state]
        - cache_hits: int
        - cache_misses: int
        - sources: dict[entity_id, str] ("cache" or "fresh")
    """
    cache_hits = {}
    cache_misses = []
    results = {}
    correlation_id = kwargs.get("corr_id")

    # Check cache for all entities
    for entity_id in entity_ids:
        cache_key = f"HA_STATE:{entity_id}"
        cached_entry = cache_get(cache_key)

        if cached_entry and not is_entry_expired(cached_entry):
            cache_hits[entity_id] = cached_entry.value
        else:
            cache_misses.append(entity_id)

    # Batch fetch cache misses
    fresh_states = {}
    if cache_misses:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'get_states_batch',
            entity_ids=cache_misses,
            oauth_token=oauth_token,
            use_cache=False,
            **kwargs
        )

        if result.get("success"):
            fresh_states = result.get("states", {})

            # Cache fresh results
            for entity_id, state in fresh_states.items():
                cache_key = f"HA_STATE:{entity_id}"
                ttl = calculate_entity_ttl(state)
                cache_set(cache_key, state, ttl=ttl, source_module="ha_state_cache")

    # Merge results
    results.update(cache_hits)
    results.update(fresh_states)

    if execute_operation and correlation_id:
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f'Batch retrieval: {len(cache_hits)} hits, {len(cache_misses)} misses',
            corr_id=correlation_id
        )

    return {
        "success": True,
        "states": results,
        "cache_hits": len(cache_hits),
        "cache_misses": len(cache_misses),
        "sources": {
            eid: "cache" if eid in cache_hits else "fresh"
            for eid in entity_ids
        }
    }
