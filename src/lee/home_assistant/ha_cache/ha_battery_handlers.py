# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Battery sensor special handling

"""Home Assistant battery sensor special handling.

Provides extended cache TTL for offline battery sensors and graceful
degradation to keep Alexa app responsive during room assignment.
"""

from typing import Any, Optional

try:
    from lee.gateway import execute_operation, GatewayInterface
    from lee.home_assistant.ha_cache.ha_state_ttl import (
        is_battery_sensor,
        is_entry_expired,
    )
    from lee.interface.wrappers.cache_wrappers import cache_get, cache_set
except ImportError:
    # Fallback for testing
    execute_operation = None
    GatewayInterface = None

    def cache_get(key, correlation_id=None):
        return None
    def cache_set(key, value, ttl=None, correlation_id=None, **kwargs):
        pass

def cache_touch(key: str, ttl: int, correlation_id: str = None) -> bool:
    """Touch a cache entry to update its TTL."""
    cached = cache_get(key, correlation_id=correlation_id)
    if cached:
        cache_set(key, cached, ttl=ttl, correlation_id=correlation_id)
        return True
    return False


def handle_battery_sensor_offline(
    entity_id: str,
    **kwargs
) -> dict[str, Any]:
    """Special handling for offline battery sensors.

    Strategy:
    1. Detect offline state (unknown/unavailable)
    2. Extend cache TTL to 2 hours maximum
    3. Graceful degradation: return last known state
    4. Log offline state for monitoring

    This ensures Alexa app doesn't lose battery sensor
    states during room assignment, even when devices
    are asleep/offline.

    Args:
        entity_id: Entity ID (e.g., "sensor.motion_battery")
        **kwargs: Additional parameters

    Returns:
        Dict with:
        - success: bool
        - state: dict (cached state)
        - source: str ("cache_extended")
        - cached_at: float
        - extended_ttl: bool
    """
    cache_key = f"HA_STATE:{entity_id}"
    correlation_id = kwargs.get("corr_id")

    # Check current cached entry
    cached_entry = cache_get(cache_key)

    if not cached_entry:
        # No cached state - return error
        return {
            "success": False,
            "error": "Battery sensor offline and no cached state",
            "entity_id": entity_id
        }

    # Check if entry is expired
    if is_entry_expired(cached_entry):
        # Entry expired, but check if we can extend
        if is_battery_sensor(cached_entry.value):
            # Extend TTL for battery sensor
            cache_touch(cache_key, ttl=7200)

            if execute_operation and correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_warning',
                    message=(
                        f'Extended TTL for offline battery sensor: '
                        f'{entity_id}'
                    ),
                    corr_id=correlation_id
                )
        else:
            # Non-battery sensor - expired
            return {
                "success": False,
                "error": "Cache entry expired",
                "entity_id": entity_id
            }

    # Return cached state
    return {
        "success": True,
        "state": cached_entry.value,
        "source": "cache_extended",
        "cached_at": cached_entry.timestamp,
        "extended_ttl": True
    }
