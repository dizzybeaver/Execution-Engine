"""
cache/cache_core.py
Version: 2025-12-08_1
Purpose: LUGS-integrated cache with TTL, rate limiting, and metrics
License: Apache 2.0
"""

import time
import sys
from collections import deque
from typing import Any, Dict, Optional, Set

from cache import (
    CacheEntry,
    _CACHE_MISS,
    DEFAULT_CACHE_TTL,
    MAX_CACHE_BYTES,
    RATE_LIMIT_WINDOW_MS,
    RATE_LIMIT_MAX_OPS,
)


class LUGSIntegratedCache:
    """In-memory cache with LUGS integration, metrics, and rate limiting."""

    def __init__(self, max_bytes: int = MAX_CACHE_BYTES, correlation_id: str = None, **kwargs):
        # NEW: Add debug tracing for exact failure point identification
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "LUGSIntegratedCache.__init__ called",
                 max_bytes=max_bytes)

        with debug_timing(correlation_id, "CACHE", "LUGSIntegratedCache.__init__", max_bytes=max_bytes):
            self._cache: Dict[str, CacheEntry] = {}
            self.max_bytes = max_bytes
            self.current_bytes = 0
            self._rate_limiter = deque(maxlen=RATE_LIMIT_MAX_OPS)
            self._rate_limit_window_ms = RATE_LIMIT_WINDOW_MS
            self._rate_limited_count = 0

            debug_log(correlation_id, "CACHE", "LUGSIntegratedCache.__init__ completed", success=True)

    def _check_rate_limit(self, correlation_id: str = None, **kwargs) -> bool:
        """Check if rate limit exceeded using sliding window."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "_check_rate_limit called")

        with debug_timing(correlation_id, "CACHE", "_check_rate_limit"):
            try:
                now = time.time() * 1000

                while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
                    self._rate_limiter.popleft()

                if len(self._rate_limiter) >= RATE_LIMIT_MAX_OPS:
                    self._rate_limited_count += 1
                    debug_log(correlation_id, "CACHE", "_check_rate_limit completed",
                             success=False, reason="Rate limit exceeded")
                    return False

                self._rate_limiter.append(now)
                debug_log(correlation_id, "CACHE", "_check_rate_limit completed",
                         success=True, rate_limited=False)
                return True
            except Exception as e:
                debug_log(correlation_id, "CACHE", "_check_rate_limit failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def _calculate_entry_size(self, key: str, value: Any, correlation_id: str = None, **kwargs) -> int:
        """Estimate memory size of cache entry."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "_calculate_entry_size called",
                 key_length=len(key) if key else 0, value_type=type(value).__name__)

        with debug_timing(correlation_id, "CACHE", "_calculate_entry_size",
                         key_length=len(key) if key else 0, value_type=type(value).__name__):
            try:
                result = sys.getsizeof(key) + sys.getsizeof(value) + 200
                debug_log(correlation_id, "CACHE", "_calculate_entry_size completed",
                         success=True, estimated_size=result)
                return result
            except Exception as e:
                debug_log(correlation_id, "CACHE", "_calculate_entry_size failed",
                         error_type=type(e).__name__, error=str(e))
                return 1024

    def _check_memory_pressure(self, correlation_id: str = None, **kwargs) -> bool:
        """Check if cache is under memory pressure (>80% full)."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "_check_memory_pressure called",
                 current_bytes=self.current_bytes, max_bytes=self.max_bytes)

        with debug_timing(correlation_id, "CACHE", "_check_memory_pressure"):
            try:
                utilization = (self.current_bytes / self.max_bytes) * 100 if self.max_bytes > 0 else 0
                result = self.current_bytes > (self.max_bytes * 0.8)
                debug_log(correlation_id, "CACHE", "_check_memory_pressure completed",
                         success=True, under_pressure=result, utilization_percent=utilization)
                return result
            except Exception as e:
                debug_log(correlation_id, "CACHE", "_check_memory_pressure failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def _evict_lru_entries(self, bytes_needed: int, correlation_id: str = None, **kwargs) -> int:
        """Evict least recently used entries to free memory."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "_evict_lru_entries called",
                 bytes_needed=bytes_needed, cache_size=len(self._cache))

        with debug_timing(correlation_id, "CACHE", "_evict_lru_entries",
                         bytes_needed=bytes_needed, cache_size=len(self._cache)):
            try:
                if not self._cache:
                    debug_log(correlation_id, "CACHE", "_evict_lru_entries completed",
                             success=True, evicted_count=0, reason="Cache is empty")
                    return 0

                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_access
                )

                bytes_freed = 0
                evicted_count = 0

                for key, entry in sorted_entries:
                    if bytes_freed >= bytes_needed:
                        break

                    bytes_freed += entry.value_size_bytes
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    evicted_count += 1

                if evicted_count > 0:
                    try:
                        from gateway import increment_counter
                        increment_counter('cache.entries_evicted', evicted_count)
                    except (ImportError, Exception):
                        pass

                debug_log(correlation_id, "CACHE", "_evict_lru_entries completed",
                         success=True, evicted_count=evicted_count, bytes_freed=bytes_freed)
                return evicted_count
            except Exception as e:
                debug_log(correlation_id, "CACHE", "_evict_lru_entries failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def _handle_memory_pressure(self, correlation_id: str = None, **kwargs) -> None:
        """Handle memory pressure by evicting entries."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "_handle_memory_pressure called")

        with debug_timing(correlation_id, "CACHE", "_handle_memory_pressure"):
            try:
                bytes_to_free = int(self.max_bytes * 0.2)
                evicted = self._evict_lru_entries(bytes_to_free, correlation_id=correlation_id)
                debug_log(correlation_id, "CACHE", "_handle_memory_pressure completed",
                         success=True, bytes_freed_target=bytes_to_free, evicted_count=evicted)
            except Exception as e:
                debug_log(correlation_id, "CACHE", "_handle_memory_pressure failed",
                         error_type=type(e).__name__, error=str(e))
                raise

    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL,
            source_module: Optional[str] = None, correlation_id: str = None, **kwargs) -> None:
        """Set cache entry with TTL and optional module tracking."""
        if correlation_id is None:
            from debug import generate_correlation_id
            correlation_id = generate_correlation_id()

        from debug import debug_log, debug_timing

        debug_log(correlation_id, "CACHE", "set called",
                 key=key, ttl=ttl, source_module=source_module, value_type=type(value).__name__)

        with debug_timing(correlation_id, "CACHE", "set",
                         key=key, ttl=ttl, source_module=source_module, value_type=type(value).__name__):
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    debug_log(correlation_id, "CACHE", "set completed",
                             success=False, reason="Rate limited")
                    return

                # FIXED: Don't silence validation errors (MEDIUM-003)
                from gateway import validate_cache_key, validate_ttl, validate_module_name, increment_counter

                validate_cache_key(key)
                validate_ttl(ttl)

                if source_module:
                    validate_module_name(source_module)

                if self._check_memory_pressure(correlation_id=correlation_id):
                    self._handle_memory_pressure(correlation_id=correlation_id)

                entry_size = self._calculate_entry_size(key, value, correlation_id=correlation_id)

                if self.current_bytes + entry_size > self.max_bytes:
                    bytes_needed = entry_size - (self.max_bytes - self.current_bytes)
                    self._evict_lru_entries(bytes_needed, correlation_id=correlation_id)

                is_update = key in self._cache
                if is_update:
                    old_entry = self._cache[key]
                    self.current_bytes -= old_entry.value_size_bytes

                current_time = time.time()

                entry = CacheEntry(
                    value=value,
                    timestamp=current_time,
                    ttl=ttl,
                    source_module=source_module,
                    access_count=0,
                    last_access=current_time,
                    value_size_bytes=entry_size
                )

                self._cache[key] = entry
                self.current_bytes += entry_size

                try:
                    increment_counter('cache.total_sets')
                except Exception:
                    pass

                if source_module:
                    try:
                        from gateway import add_cache_module_dependency
                        add_cache_module_dependency(source_module, key)
                    except (ImportError, Exception):
                        pass

                debug_log(correlation_id, "CACHE", "set completed",
                         success=True, is_update=is_update, entry_size=entry_size)
            except Exception as e:
                debug_log(correlation_id, "CACHE", "set failed",
                         error_type=type(e).__name__, error=str(e))
                raise


_cache_instance = None


__all__ = [
    'LUGSIntegratedCache',
]

# EOF