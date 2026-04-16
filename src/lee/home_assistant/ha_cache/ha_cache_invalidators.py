# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Cache invalidation strategies

"""Home Assistant cache invalidation strategies.

Provides intelligent cache invalidation for service calls,
domain-wide operations, and device-level changes.
"""

from typing import Any

try:
    from lee.gateway import execute_operation, GatewayInterface
    from lee.interface.wrappers.cache_wrappers import (
        cache_get,
        cache_delete
    )
except ImportError:
    # Fallback for testing
    execute_operation = None
    GatewayInterface = None


def invalidate_on_service_call(
    domain: str,
    service: str,
    service_data: dict[str, Any],
    **kwargs
) -> None:
    """Invalidate cache entries affected by service call.

    Invalidation Strategy:
    1. Direct entity invalidation:
       - service_data["entity_id"] specified
       - Invalidate HA_STATE:{entity_id}

    2. Domain-wide invalidation:
       - Services that affect entire domain
       - Examples: light.turn_on_all, switch.toggle_all
       - Invalidate all HA_STATE:{domain}:* entries

    3. Device-wide invalidation:
       - Device-level operations
       - Invalidate all entities for device_id
       - Use HA_DEVICE:{device_id} index

    Args:
        domain: Domain (e.g., "light", "switch")
        service: Service name (e.g., "turn_on", "toggle")
        service_data: Service data dict
        **kwargs: Additional parameters
    """
    correlation_id = kwargs.get("corr_id")

    # Direct entity invalidation
    if "entity_id" in service_data:
        entity_id = service_data["entity_id"]
        cache_key = f"HA_STATE:{entity_id}"

        # Get cached state before deleting (for device cache)
        cached_state = cache_get(cache_key)
        if cached_state and cached_state.value:
            attributes = cached_state.value.get("attributes", {})
            device_id = attributes.get("device_id")
            if device_id:
                device_cache_key = f"HA_DEVICE:{device_id}"
                cache_delete(device_cache_key)

        # Delete entity cache
        cache_delete(cache_key)

        if execute_operation and correlation_id:
            execute_operation(
                GatewayInterface.LOGGING,
                'log_debug',
                message=f'Invalidated cache for {entity_id} after {domain}.{service}',
                corr_id=correlation_id
            )

    # Domain-wide invalidation
    elif is_domain_wide_service(domain, service):
        # Get all cached entities for domain
        domain_cache_key = f"HA_DOMAIN:{domain}"
        domain_entry = cache_get(domain_cache_key)

        if domain_entry and domain_entry.value:
            domain_entities = domain_entry.value
            for entity_id in domain_entities:
                cache_delete(f"HA_STATE:{entity_id}")

            cache_delete(domain_cache_key)

            if execute_operation and correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_info',
                    message=f'Invalidated {len(domain_entities)} entities for domain {domain}',
                    corr_id=correlation_id
                )


def is_domain_wide_service(domain: str, service: str) -> bool:
    """Check if service affects entire domain.

    Args:
        domain: Domain name
        service: Service name

    Returns:
        True if service affects entire domain
    """
    domain_wide_patterns = [
        "turn_on_all",
        "turn_off_all",
        "toggle_all",
        "reload",
    ]

    return any(pattern in service for pattern in domain_wide_patterns)
