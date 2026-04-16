# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Device cache operations with batch metrics

"""ha_devices_cache.py - Cache management for Home Assistant devices

Provides caching, diagnostic, and performance reporting functions
with batch operation metrics.
"""

import threading
import time
from typing import Any

from lee.gateway import GatewayInterface, execute_operation

# Thread-safe cache with locks
_entity_cache: dict[str, dict[str, Any]] = {}
_domain_cache: dict[str, list[str]] = {}
_cache_timestamps: dict[str, float] = {}
_cache_lock = threading.RLock()  # Reentrant lock for nested calls
_warming_lock = threading.Lock()
_warming_flag = False

CACHE_TTL = 30  # seconds


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    import os
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def _update_domain_index(entity_id: str, add: bool = True) -> None:
    """Update domain index when entity is added or removed.

    Args:
        entity_id: Entity ID to update
        add: True if adding entity, False if removing
    """
    try:
        if not entity_id or "." not in entity_id or entity_id.startswith("."):
            return

        domain = entity_id.split(".", 1)[0]

        if add:
            if domain not in _domain_cache:
                _domain_cache[domain] = []
            if entity_id not in _domain_cache[domain]:
                _domain_cache[domain].append(entity_id)
        else:
            if domain in _domain_cache and entity_id in _domain_cache[domain]:
                _domain_cache[domain].remove(entity_id)
                if not _domain_cache[domain]:
                    del _domain_cache[domain]
    except (ValueError, KeyError, AttributeError) as e:
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                'log_error',
                message=f'(ValueError, KeyError, AttributeError) occurred: {e}',
                corr_id=None
            )
        except (ImportError, AttributeError, RuntimeError):
            pass  # Gateway not available


def warm_cache_impl(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Pre-warm cache with frequently accessed entities.

    Args:
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status and cache stats
    """
    try:
        from lee.home_assistant.ha_devices.ha_devices_generic import get_states_impl

        result = get_states_impl(None, False, oauth_token, **kwargs)

        if not result.get("success"):
            return result

        states = result.get("states", [])
        cache_count = 0

        for state in states:
            entity_id = state.get("entity_id")
            if entity_id:
                _entity_cache[entity_id] = state
                _cache_timestamps[entity_id] = time.time()
                _update_domain_index(entity_id, add=True)
                cache_count += 1

        return {
            "success": True,
            "cached_entities": cache_count,
            "cache_ttl_seconds": CACHE_TTL
        }

    except (ImportError, AttributeError, KeyError, ValueError, TypeError, RuntimeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"warm_cache failed: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "WARM_CACHE_ERROR"
        }


def invalidate_entity_cache_impl(entity_id: str, **kwargs) -> bool:
    """Invalidate cache for a specific entity.

    Args:
        entity_id: Entity ID to invalidate
        **kwargs: Additional parameters

    Returns:
        True if invalidated, False otherwise
    """
    try:
        if entity_id in _entity_cache:
            del _entity_cache[entity_id]
        if entity_id in _cache_timestamps:
            del _cache_timestamps[entity_id]
        return True
    except (KeyError, AttributeError, TypeError, RuntimeError):
        # Key deletion or cache manipulation errors
        ...
        return False


def invalidate_domain_cache_impl(domain: str, **kwargs) -> int:
    """Invalidate cache for all entities in a domain.

    Args:
        domain: Domain to invalidate
        **kwargs: Additional parameters

    Returns:
        Number of entities invalidated
    """
    try:
        count = 0

        if domain in _domain_cache:
            entity_ids = _domain_cache[domain][:]

            for entity_id in entity_ids:
                if entity_id in _entity_cache:
                    del _entity_cache[entity_id]
                if entity_id in _cache_timestamps:
                    del _cache_timestamps[entity_id]
                _update_domain_index(entity_id, add=False)
                count += 1

        return count

    except (KeyError, AttributeError, TypeError, RuntimeError):
        # Cache iteration or deletion errors
        ...
        return 0


def get_performance_report_impl(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get performance report including batch operation metrics.

    Args:
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status and performance metrics
    """
    try:
        # Get batch metrics from metrics system
        batch_metrics = execute_operation(GatewayInterface.METRICS, "get_metrics",
                                        metric_pattern="ha_batch_*")

        # Calculate stats
        batch_count = len([m for m in batch_metrics if "batch" in m.get("name", "")])
        total_calls = sum(m.get("value", 0) for m in batch_metrics)

        return {
            "success": True,
            "batch_operations_count": batch_count,
            "total_batch_calls": total_calls,
            "cache_size": len(_entity_cache),
            "cache_ttl_seconds": CACHE_TTL,
            "metrics": batch_metrics
        }

    except (KeyError, ValueError, TypeError, AttributeError, RuntimeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_performance_report failed: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "PERFORMANCE_REPORT_ERROR"
        }


def get_diagnostic_info_impl(oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get diagnostic information about cache and batch operations.

    Args:
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status and diagnostic data
    """
    try:
        # Get stale cache entries
        current_time = time.time()
        stale_entries = []

        for entity_id, timestamp in _cache_timestamps.items():
            age = current_time - timestamp
            if age > CACHE_TTL:
                stale_entries.append({
                    "entity_id": entity_id,
                    "age_seconds": int(age)
                })

        # Get domain distribution (O(1) lookup from pre-computed index)
        domain_counts = {domain: len(entity_ids) for domain, entity_ids in _domain_cache.items()}

        return {
            "success": True,
            "cache_stats": {
                "total_entries": len(_entity_cache),
                "stale_entries": len(stale_entries),
                "domains": domain_counts
            },
            "stale_entries": stale_entries[:10],  # Limit to first 10
            "cache_ttl_seconds": CACHE_TTL
        }

    except (KeyError, ValueError, TypeError, AttributeError, RuntimeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_diagnostic_info failed: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "DIAGNOSTIC_INFO_ERROR"
        }
