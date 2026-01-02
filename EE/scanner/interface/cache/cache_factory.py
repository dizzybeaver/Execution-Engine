"""Cache Factory - Scanner Domain (EE 2.1 Compliant).

Version: 2.1.0
Date: 2025-12-31
Purpose: Factory contains all business logic for scanner cache operations
Type: EE 2.1 Factory Implementation

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, get_config, call_operation via DI
- NO imports outside scanner domain (except stdlib)
- All cross-domain calls via call_operation callback
- Thread-safe module-level cache for persistence across instances
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from collections import OrderedDict
import threading


# =============================================================================
# Module-level cache storage (shared across all instances)
# =============================================================================

_CACHE_STORE: OrderedDict = OrderedDict()
_CACHE_LOCK = threading.RLock()
_CACHE_MAX_SIZE = 128


# =============================================================================
# Cache Factory Class
# =============================================================================

class CacheFactory:
    """Factory for cache operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all cache business logic
    - Use DI (logger, metrics, config, call_operation)
    - Thread-safe operations with module-level cache
    - LRU eviction policy

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    - Uses module-level cache for persistence
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize cache factory with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        self.logger = get_logger("scanner.cache.factory")
        self.metrics = get_metrics("scanner.cache.factory")
        self._get_config = get_config
        self._call_operation = call_operation

        # Load max size from config if available
        self._max_size = get_config("scanner.cache.max_size", _CACHE_MAX_SIZE)

    def get(self, key: str, **kwargs) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            **kwargs: Additional parameters (unused)

        Returns:
            Cached value or None if not found
        """
        with _CACHE_LOCK:
            if key in _CACHE_STORE:
                # Move to end (most recently used)
                value = _CACHE_STORE.pop(key)
                _CACHE_STORE[key] = value
                self.logger.debug(f"Cache HIT: {key}")
                return value
            else:
                self.logger.debug(f"Cache MISS: {key}")
                return None

    def set(self, key: str, value: Any, **kwargs) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            **kwargs: Additional parameters (unused)
        """
        with _CACHE_LOCK:
            # Simple LRU: if cache full, clear oldest item
            if len(_CACHE_STORE) >= self._max_size and key not in _CACHE_STORE:
                # Remove first item (oldest)
                oldest_key = next(iter(_CACHE_STORE))
                del _CACHE_STORE[oldest_key]
                self.logger.debug(f"Cache EVICT: {oldest_key}")

            _CACHE_STORE[key] = value
            self.logger.debug(f"Cache SET: {key}")

    def delete(self, key: str, **kwargs) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key
            **kwargs: Additional parameters (unused)

        Returns:
            True if key was deleted, False if not found
        """
        with _CACHE_LOCK:
            if key in _CACHE_STORE:
                del _CACHE_STORE[key]
                self.logger.debug(f"Cache DELETE: {key}")
                return True
            return False

    def clear(self, **kwargs) -> None:
        """Clear all cached values.

        Args:
            **kwargs: Additional parameters (unused)
        """
        with _CACHE_LOCK:
            _CACHE_STORE.clear()
            self.logger.debug("Cache CLEAR: all entries")

    def get_stats(self, **kwargs) -> Dict[str, Any]:
        """Get cache statistics.

        Args:
            **kwargs: Additional parameters (unused)

        Returns:
            Dict with cache stats (size, maxsize, keys)
        """
        with _CACHE_LOCK:
            return {
                'size': len(_CACHE_STORE),
                'maxsize': self._max_size,
                'keys': list(_CACHE_STORE.keys())
            }


__all__ = ['CacheFactory']
