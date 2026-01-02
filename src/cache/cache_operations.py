"""
cache/cache_operations.py
Version: 2025-12-08_1
Purpose: Cache operations with debug tracing - split from cache_core.py
License: Apache 2.0
"""

import time
from typing import Any, Dict, Optional, Set

from cache import _CACHE_MISS, DEFAULT_CACHE_TTL

# Import the LUGSIntegratedCache class from cache_core
from cache.cache_core import LUGSIntegratedCache


class LUGSIntegratedCacheOperations(LUGSIntegratedCache):
    """Extended cache operations with debug tracing."""

    def get(self, key: str, correlation_id: str = None, **kwargs) -> Any:
        """Get cached value if exists and not expired."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "get called", key=key)

        with debug_timing(correlation_id, "CACHE", "get", key=key):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "get completed",
                             success=False, reason="Rate limited")
                    return _CACHE_MISS

                try:
                    from gateway import record_cache_metric, increment_counter
                except ImportError:
                    debug_log(correlation_id, "CACHE", "get completed",
                             success=False, reason="Gateway import failed")
                    return _CACHE_MISS

                if key not in self._cache:
                    try:
                        record_cache_metric(operation_name='get', hit=False)
                    except Exception:
                        pass
                    debug_log(correlation_id, "CACHE", "get completed",
                             success=False, reason="Key not found")
                    return _CACHE_MISS

                entry = self._cache[key]
                current_time = time.time()
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]

                    try:
                        increment_counter('cache.entries_expired')
                        record_cache_metric(operation_name='get', hit=False)
                    except Exception:
                        pass
                    debug_log(correlation_id, "CACHE", "get completed",
                             success=False, reason="Entry expired", age=age, ttl=entry.ttl)
                    return _CACHE_MISS

                entry.access_count += 1
                entry.last_access = current_time

                try:
                    record_cache_metric(operation_name='get', hit=True)
                except Exception:
                    pass

                debug_log(correlation_id, "CACHE", "get completed",
                         success=True, hit=True, access_count=entry.access_count)
                return entry.value
            except Exception as e:
                debug_log(correlation_id, "CACHE", "get failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def exists(self, key: str, correlation_id: str = None, **kwargs) -> bool:
        """Check if key exists and is not expired."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "exists called", key=key)

        with debug_timing(correlation_id, "CACHE", "exists", key=key):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "exists completed",
                             success=False, reason="Rate limited")
                    return False

                if key not in self._cache:
                    debug_log(correlation_id, "CACHE", "exists completed",
                             success=True, exists=False, reason="Key not found")
                    return False

                entry = self._cache[key]
                current_time = time.time()
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]

                    try:
                        from gateway import increment_counter
                        increment_counter('cache.entries_expired')
                    except (ImportError, Exception):
                        pass

                    debug_log(correlation_id, "CACHE", "exists completed",
                             success=True, exists=False, reason="Entry expired")
                    return False

                debug_log(correlation_id, "CACHE", "exists completed",
                         success=True, exists=True, age=age, ttl=entry.ttl)
                return True
            except Exception as e:
                debug_log(correlation_id, "CACHE", "exists failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def delete(self, key: str, correlation_id: str = None, **kwargs) -> bool:
        """Delete cache entry if it exists."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "delete called", key=key)

        with debug_timing(correlation_id, "CACHE", "delete", key=key):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "delete completed",
                             success=False, reason="Rate limited")
                    return False

                if key in self._cache:
                    entry = self._cache[key]
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    debug_log(correlation_id, "CACHE", "delete completed",
                             success=True, deleted=True, entry_size=entry.value_size_bytes)
                    return True

                debug_log(correlation_id, "CACHE", "delete completed",
                         success=True, deleted=False, reason="Key not found")
                return False
            except Exception as e:
                debug_log(correlation_id, "CACHE", "delete failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def clear(self, correlation_id: str = None, **kwargs) -> int:
        """Clear all cache entries."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "clear called")

        with debug_timing(correlation_id, "CACHE", "clear"):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "clear completed",
                             success=False, reason="Rate limited", cleared_count=0)
                    return 0

                count = len(self._cache)
                self._cache.clear()
                self.current_bytes = 0
                debug_log(correlation_id, "CACHE", "clear completed",
                         success=True, cleared_count=count)
                return count
            except Exception as e:
                debug_log(correlation_id, "CACHE", "clear failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def reset(self, correlation_id: str = None, **kwargs) -> bool:
        """Reset cache to initial state."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "reset called")

        with debug_timing(correlation_id, "CACHE", "reset"):
            try:
                self._cache.clear()
                self.current_bytes = 0
                self._rate_limiter.clear()
                self._rate_limited_count = 0
                debug_log(correlation_id, "CACHE", "reset completed", success=True)
                return True
            except Exception as e:
                debug_log(correlation_id, "CACHE", "reset failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def cleanup_expired(self, correlation_id: str = None, **kwargs) -> int:
        """Remove all expired entries."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "cleanup_expired called")

        with debug_timing(correlation_id, "CACHE", "cleanup_expired"):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "cleanup_expired completed",
                             success=False, reason="Rate limited", cleaned_count=0)
                    return 0

                try:
                    from gateway import increment_counter
                except ImportError:
                    increment_counter = None

                current_time = time.time()
                expired_keys = [
                    key for key, entry in self._cache.items()
                    if current_time - entry.timestamp > entry.ttl
                ]

                for key in expired_keys:
                    entry = self._cache[key]
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]

                count = len(expired_keys)

                if count > 0 and increment_counter:
                    try:
                        increment_counter('cache.entries_expired', count)
                    except Exception:
                        pass

                debug_log(correlation_id, "CACHE", "cleanup_expired completed",
                         success=True, cleaned_count=count)
                return count
            except Exception as e:
                debug_log(correlation_id, "CACHE", "cleanup_expired failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_metadata(self, key: str, correlation_id: str = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cache entry metadata without accessing value."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "get_metadata called", key=key)

        with debug_timing(correlation_id, "CACHE", "get_metadata", key=key):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "get_metadata completed",
                             success=False, reason="Rate limited")
                    return None

                try:
                    from gateway import increment_counter
                    increment_counter('cache.metadata_queries')
                except (ImportError, Exception):
                    pass

                if key not in self._cache:
                    debug_log(correlation_id, "CACHE", "get_metadata completed",
                             success=False, reason="Key not found")
                    return None

                entry = self._cache[key]
                current_time = time.time()
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    try:
                        from gateway import increment_counter
                        increment_counter('cache.entries_expired')
                    except (ImportError, Exception):
                        pass
                    debug_log(correlation_id, "CACHE", "get_metadata completed",
                             success=False, reason="Entry expired")
                    return None

                metadata = {
                    'source_module': entry.source_module,
                    'timestamp': entry.timestamp,
                    'age_seconds': age,
                    'ttl': entry.ttl,
                    'ttl_remaining': max(0, entry.ttl - age),
                    'access_count': entry.access_count,
                    'last_access': entry.last_access,
                    'size_bytes': entry.value_size_bytes,
                    'is_expired': False
                }

                debug_log(correlation_id, "CACHE", "get_metadata completed",
                         success=True, has_metadata=True)
                return metadata
            except Exception as e:
                debug_log(correlation_id, "CACHE", "get_metadata failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_stats(self, correlation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get cache statistics."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "get_stats called")

        with debug_timing(correlation_id, "CACHE", "get_stats"):
            try:
                stats = {
                    'size': len(self._cache),
                    'memory_bytes': self.current_bytes,
                    'memory_mb': round(self.current_bytes / (1024 * 1024), 2),
                    'max_bytes': self.max_bytes,
                    'max_mb': round(self.max_bytes / (1024 * 1024), 2),
                    'memory_utilization_percent': round((self.current_bytes / self.max_bytes) * 100, 2) if self.max_bytes > 0 else 0,
                    'default_ttl_seconds': DEFAULT_CACHE_TTL,
                    'rate_limited_count': self._rate_limited_count
                }

                debug_log(correlation_id, "CACHE", "get_stats completed",
                         success=True, cache_size=stats['size'], utilization=stats['memory_utilization_percent'])
                return stats
            except Exception as e:
                debug_log(correlation_id, "CACHE", "get_stats failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def get_module_dependencies(self, correlation_id: str = None, **kwargs) -> Set[str]:
        """Get set of all module names that have cache dependencies."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "get_module_dependencies called")

        with debug_timing(correlation_id, "CACHE", "get_module_dependencies"):
            try:
                modules = set()
                for entry in self._cache.values():
                    if entry.source_module:
                        modules.add(entry.source_module)

                debug_log(correlation_id, "CACHE", "get_module_dependencies completed",
                         success=True, module_count=len(modules))
                return modules
            except Exception as e:
                debug_log(correlation_id, "CACHE", "get_module_dependencies failed",
                         error_type=type(e).__name__, error=str(e))
                raise


_cache_instance = None


def _get_cache_instance(correlation_id: str = None, **kwargs) -> LUGSIntegratedCacheOperations:
    """Get or create cache singleton instance via SINGLETON interface."""
    if correlation_id is None:
        from debug import generate_correlation_id
        correlation_id = generate_correlation_id()

    from debug import debug_log, debug_timing

    debug_log(correlation_id, "CACHE", "_get_cache_instance called")

    with debug_timing(correlation_id, "CACHE", "_get_cache_instance"):
        try:
            global _cache_instance

            try:
                from gateway import singleton_get, singleton_register

                manager = singleton_get('cache_manager')
                if manager is None:
                    manager = LUGSIntegratedCacheOperations(correlation_id=correlation_id)
                    singleton_register('cache_manager', manager)

                debug_log(correlation_id, "CACHE", "_get_cache_instance completed",
                         success=True, using_gateway=True)
                return manager
            except (ImportError, Exception):
                if _cache_instance is None:
                    _cache_instance = LUGSIntegratedCacheOperations(correlation_id=correlation_id)

                debug_log(correlation_id, "CACHE", "_get_cache_instance completed",
                         success=True, using_gateway=False, using_fallback=True)
                return _cache_instance
        except Exception as e:
            debug_log(correlation_id, "CACHE", "_get_cache_instance failed",
                     error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'LUGSIntegratedCacheOperations',
    '_get_cache_instance',
]

# EOF