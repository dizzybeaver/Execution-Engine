"""
Cache Factory - Operations Domain

Caching operations with LRU eviction implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation factory functions via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation(domain, interface, operation, **kwargs) callback
- Module-level cache for persistence across instances
"""

from collections import OrderedDict
from typing import Any, Dict, Optional, Callable
import threading
import time
import logging


# =============================================================================
# Module-level cache storage (shared across all instances)
# =============================================================================

_CACHE_STORE: OrderedDict = OrderedDict()
_CACHE_LOCK = threading.RLock()
_CACHE_STATS = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
}


# =============================================================================
# Cache Factory Class
# =============================================================================

class CacheFactory:
    """Caching operations factory.

    Provides LRU cache implementation with configurable eviction.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    - Uses module-level cache for persistence
    """

    # MODIFIED: EE 2.1 compliant constructor - receives factory functions
    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize cache factory.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations with signature: call_operation(domain, interface, operation, **kwargs)
        """
        # Create logger using factory function
        if get_logger:
            self.logger = get_logger("operations.cache")
        else:
            self.logger = logging.getLogger(__name__)

        self.get_metrics = get_metrics
        self.call_operation = call_operation

    def get(self, key: str, default: Any = None, **kwargs) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if not found
            **kwargs: Additional parameters

        Returns:
            Cached value or default
        """
        with _CACHE_LOCK:
            if key in _CACHE_STORE:
                # Move to end (most recently used)
                value, expiry = _CACHE_STORE.pop(key)
                if expiry is None or time.time() < expiry:
                    _CACHE_STORE[key] = (value, expiry)
                    _CACHE_STATS["hits"] += 1
                    return value
                else:
                    # Expired
                    _CACHE_STATS["misses"] += 1
                    return default
            else:
                _CACHE_STATS["misses"] += 1
                return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiry)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with _CACHE_LOCK:
            expiry = None
            if ttl is not None:
                expiry = time.time() + ttl

            _CACHE_STORE[key] = (value, expiry)
            _CACHE_STATS["sets"] += 1

            # Evict oldest if cache is too large (LRU)
            max_size = kwargs.get("max_size", 1000)
            while len(_CACHE_STORE) > max_size:
                _CACHE_STORE.popitem(last=False)

            return True

    def delete(self, key: str, **kwargs) -> bool:
        """Delete from cache.

        Args:
            key: Cache key
            **kwargs: Additional parameters

        Returns:
            True if deleted, False if not found
        """
        with _CACHE_LOCK:
            if key in _CACHE_STORE:
                del _CACHE_STORE[key]
                _CACHE_STATS["deletes"] += 1
                return True
            return False

    def clear(self, **kwargs) -> bool:
        """Clear all cache entries.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with _CACHE_LOCK:
            _CACHE_STORE.clear()
            return True

    def stats(self, **kwargs) -> Dict[str, Any]:
        """Get cache statistics.

        Args:
            **kwargs: Additional parameters

        Returns:
            Cache statistics dictionary
        """
        with _CACHE_LOCK:
            total_requests = _CACHE_STATS["hits"] + _CACHE_STATS["misses"]
            hit_rate = (
                _CACHE_STATS["hits"] / total_requests
                if total_requests > 0
                else 0.0
            )

            return {
                "hits": _CACHE_STATS["hits"],
                "misses": _CACHE_STATS["misses"],
                "sets": _CACHE_STATS["sets"],
                "deletes": _CACHE_STATS["deletes"],
                "size": len(_CACHE_STORE),
                "hit_rate": round(hit_rate, 4),
            }

    def exists(self, key: str, **kwargs) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key
            **kwargs: Additional parameters

        Returns:
            True if key exists and not expired
        """
        with _CACHE_LOCK:
            if key in _CACHE_STORE:
                value, expiry = _CACHE_STORE[key]
                if expiry is None or time.time() < expiry:
                    return True
                else:
                    # Expired, remove it
                    del _CACHE_STORE[key]
                    return False
            return False


__all__ = [
    "CacheFactory",
]
