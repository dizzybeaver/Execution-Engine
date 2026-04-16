# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Add caching to Home Assistant Alexa proxy mode

"""Proxy mode caching layer for Home Assistant Alexa integration.

Adds intelligent caching to proxy mode to reduce latency while
maintaining benefits of native Home Assistant Alexa endpoint.
"""

import json
import time
from typing import Any, Optional

try:
    from lee.gateway import GatewayInterface, execute_operation
    from lee.interface.wrappers.cache_wrappers import (
        cache_get,
        cache_set,
        cache_delete
    )
except ImportError:
    # Fallback for testing
    execute_operation = None
    GatewayInterface = None

    def cache_get(key, correlation_id=None):
        return None
    def cache_set(key, value, ttl=None, correlation_id=None, **kwargs):
        pass
    def cache_delete(key, correlation_id=None):
        pass


# Cache key prefixes
ALEXA_PROXY_CACHE_PREFIX = "HA_ALEXA_PROXY:"
DISCOVERY_CACHE_KEY = f"{ALEXA_PROXY_CACHE_PREFIX}DISCOVERY"
STATE_CACHE_KEY = f"{ALEXA_PROXY_CACHE_PREFIX}STATE:"

# Cache TTLs (seconds)
DISCOVERY_CACHE_TTL = 3600  # 1 hour for discovery
STATE_CACHE_TTL = 300     # 5 minutes for device states


def get_cache_key_from_directive(directive: dict[str, Any]) -> Optional[str]:
    """Generate cache key from Alexa directive.

    Args:
        directive: Alexa directive dictionary

    Returns:
        Cache key or None if not cacheable
    """
    directive_name = directive.get("header", {}).get("name")

    if directive_name == "Discover":
        # Discovery is cached per user/token
        scope = directive.get("endpoint", {}).get("scope", {})
        token_id = scope.get("token", "default")[:16]  # First 16 chars of token
        return f"{DISCOVERY_CACHE_KEY}:{token_id}"

    elif directive_name in ("ReportState", "Discovery"):
        # These are state-related directives
        endpoint_id = directive.get("endpoint", {}).get("endpointId", "unknown")
        return f"{STATE_CACHE_KEY}:{endpoint_id}"

    return None


def should_use_cache(directive: dict[str, Any]) -> bool:
    """Check if directive should use cached response.

    Args:
        directive: Alexa directive dictionary

    Returns:
        True if directive should use cache
    """
    directive_name = directive.get("header", {}).get("name")

    # Cache discovery requests
    if directive_name == "Discover":
        return True

    # Cache state reporting requests
    if directive_name == "ReportState":
        return True

    # Don't cache control directives (they need to execute immediately)
    return False


def get_cached_response(directive: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Get cached response for directive if available.

    Args:
        directive: Alexa directive dictionary

    Returns:
        Cached response or None if not in cache
    """
    cache_key = get_cache_key_from_directive(directive)
    if not cache_key:
        return None

    try:
        cached_entry = cache_get(cache_key, correlation_id="ALEXA_PROXY_CACHE")

        # Handle different cache return types
        if cached_entry is None:
            return None

        # Check if this is a cache miss indicator
        if hasattr(cached_entry, '__class__') and 'CacheMiss' in str(cached_entry.__class__):
            return None

        # Handle cache entry objects with .value attribute
        if hasattr(cached_entry, 'value'):
            directive_name = directive.get("header", {}).get("name", "Unknown")
            execute_operation(
                GatewayInterface.LOGGING,
                'log_info',
                message=f'Alexa proxy cache hit: {directive_name}',
                corr_id="ALEXA_PROXY_CACHE"
            )
            return cached_entry.value

        # Direct cached value (rare case)
        directive_name = directive.get("header", {}).get("name", "Unknown")
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f'Alexa proxy cache hit: {directive_name}',
            corr_id="ALEXA_PROXY_CACHE"
        )
        return cached_entry

    except Exception as e:
        # Cache lookup failed, treat as cache miss
        execute_operation(
            GatewayInterface.LOGGING,
            'log_debug',
            message=f'Alexa proxy cache lookup failed: {str(e)}',
            corr_id="ALEXA_PROXY_CACHE"
        )
        return None


def cache_response(directive: dict[str, Any], response: dict[str, Any]) -> None:
    """Cache successful response for directive.

    Args:
        directive: Alexa directive dictionary
        response: Response from Home Assistant
    """
    cache_key = get_cache_key_from_directive(directive)
    if not cache_key:
        return

    directive_name = directive.get("header", {}).get("name")

    # Set appropriate TTL based on directive type
    if directive_name == "Discover":
        ttl = DISCOVERY_CACHE_TTL
    elif directive_name == "ReportState":
        ttl = STATE_CACHE_TTL
    else:
        ttl = STATE_CACHE_TTL

    cache_set(cache_key, response, ttl=ttl, correlation_id="ALEXA_PROXY_CACHE")

    execute_operation(
        GatewayInterface.LOGGING,
        'log_info',
        message=f'Alexa proxy cached response: {directive_name} (TTL: {ttl}s)',
        corr_id="ALEXA_PROXY_CACHE"
    )


def invalidate_on_control_directive(directive: dict[str, Any]) -> None:
    """Invalidate cached state when control directive is executed.

    Args:
        directive: Alexa control directive
    """
    directive_name = directive.get("header", {}).get("name")

    # Only control directives invalidate cache
    if directive_name not in ("TurnOn", "TurnOff", "SetPercentage",
                            "AdjustBrightness", "SetColor",
                            "SetTemperature", "Lock", "Unlock"):
        return

    # Invalidate discovery cache (device states may have changed)
    cache_delete(DISCOVERY_CACHE_KEY + ":*")  # This would need wildcard support

    # Invalidate specific device state cache
    endpoint_id = directive.get("endpoint", {}).get("endpointId")
    if endpoint_id:
        state_key = f"{STATE_CACHE_KEY}:{endpoint_id}"
        cache_delete(state_key)

        execute_operation(
            GatewayInterface.LOGGING,
            'log_debug',
            message=f'Alexa proxy invalidated cache for: {endpoint_id}',
            corr_id="ALEXA_PROXY_CACHE"
        )


def is_cache_successful_response(response: dict[str, Any]) -> bool:
    """Check if response is successful and should be cached.

    Args:
        response: Response from Home Assistant

    Returns:
        True if response should be cached
    """
    try:
        # Check for successful response structure
        if "event" in response:
            # Success response
            payload = response["event"].get("payload", {})

            # Don't cache error responses
            if payload.get("type") in [
                "AUTHORIZATION_REQUIRED",
                "INTERNAL_ERROR",
                "INVALID_AUTHORIZATION_CREDENTIAL"
            ]:
                return False

            return True

        return False
    except Exception:
        # If response structure is unexpected, don't cache it
        return False


def get_discovery_cache_stats() -> dict[str, Any]:
    """Get discovery cache statistics.

    Returns:
        Dict with cache statistics
    """
    # This would need cache_stats functionality
    return {
        "discovery_cache_enabled": True,
        "state_cache_enabled": True,
        "cache_keys": [
            DISCOVERY_CACHE_KEY,
            STATE_CACHE_KEY
        ]
    }