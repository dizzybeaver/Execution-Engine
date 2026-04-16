# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Entity state cache warming implementation

"""Home Assistant entity state cache warming.

Provides cache warming functionality for entity states after
discovery operations to prevent cold-start penalties.
"""

from typing import Any, Optional

try:
    from lee.gateway import execute_operation, GatewayInterface
    from lee.home_assistant.ha_gateway import ha_execute_operation, HAGatewayInterface
    from lee.interface.wrappers.cache_wrappers import cache_set
except ImportError:
    # Fallback for testing
    execute_operation = None
    GatewayInterface = None
    ha_execute_operation = None
    HAGatewayInterface = None

from lee.home_assistant.ha_cache.ha_state_ttl import calculate_entity_ttl


def warm_entity_states_cache(
    entity_ids: list[str],
    oauth_token: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Warm cache for specified entity states.

    Typically called after Alexa discovery to pre-load states
    for all discovered entities, reducing latency for subsequent
    state retrieval operations.

    Args:
        entity_ids: List of entity IDs to warm
        oauth_token: OAuth token for HA API
        **kwargs: Additional parameters

    Returns:
        Dict with:
        - success: bool
        - warmed_count: int
        - failed_count: int
        - total_count: int
    """
    correlation_id = kwargs.get("corr_id")
    warmed_count = 0
    failed_count = 0

    if not entity_ids:
        return {
            "success": True,
            "warmed_count": 0,
            "failed_count": 0,
            "total_count": 0
        }

    # Batch fetch all entity states
    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        'get_states_batch',
        entity_ids=entity_ids,
        oauth_token=oauth_token,
        use_cache=False,
        **kwargs
    )

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "Failed to fetch states"),
            "warmed_count": 0,
            "failed_count": len(entity_ids),
            "total_count": len(entity_ids)
        }

    states = result.get("states", {})

    # Cache each state with appropriate TTL
    for entity_id, state in states.items():
        try:
            cache_key = f"HA_STATE:{entity_id}"
            ttl = calculate_entity_ttl(state)

            cache_set(
                cache_key,
                state,
                ttl=ttl,
                source_module="ha_cache_warmer"
            )

            warmed_count += 1

        except Exception as e:
            failed_count += 1

            if execute_operation and correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_warning',
                    message=f'Failed to warm cache for {entity_id}: {str(e)}',
                    corr_id=correlation_id
                )

    if execute_operation and correlation_id:
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f'Warmed cache for {warmed_count}/{len(entity_ids)} entities',
            corr_id=correlation_id
        )

    return {
        "success": True,
        "warmed_count": warmed_count,
        "failed_count": failed_count,
        "total_count": len(entity_ids)
    }


def warm_discovered_entities(
    discovered_entities: dict[str, Any],
    oauth_token: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Warm cache for all entities discovered by Alexa.

    Extracts entity IDs from Alexa discovery response and warms
    their states in the cache.

    Args:
        discovered_entities: Discovery response with entity data
        oauth_token: OAuth token for HA API
        **kwargs: Additional parameters

    Returns:
        Dict with warming statistics
    """
    entity_ids = []

    # Extract entity IDs from discovery response
    for endpoint in discovered_entities.get("endpoints", []):
        for entity in endpoint.get("entities", []):
            entity_id = entity.get("entity_id")
            if entity_id:
                entity_ids.append(entity_id)

    return warm_entity_states_cache(entity_ids, oauth_token, **kwargs)
