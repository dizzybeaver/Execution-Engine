"""Generic cache implementation for LEE.

Version: 2025-12-08_1
License: Apache 2.0
"""

import heapq
import os
import secrets
import sys
import threading
import time
from collections import deque
from contextlib import nullcontext
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_cache.cache_compression import get_cache_compressor
from lee.lee_cache.cache_enums import (
    DEFAULT_CACHE_TTL,
    MAX_CACHE_BYTES,
    RATE_LIMIT_MAX_OPS,
    RATE_LIMIT_WINDOW_MS,
    CacheEntry,
)
from lee.lee_config.constants import (
    CACHE_MEMORY_CHECK_INTERVAL_MS,
    CACHE_MEMORY_CHECK_SAMPLE_RATE,
)
from lee.lee_utility.debug_logging_helper import DebugLoggingHelper

# LEE_DEBUG tracing for cache core operations
_debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

def _trace_cache_core(message: str, **kwargs: Any) -> None:
    """Trace cache core operations when LEE_DEBUG is enabled.

    Args:
        message: Debug message
        **kwargs: Additional context data
    """
    if _debug_enabled:
        try:
            execute_operation(GatewayInterface.DEBUG, 'log',
                            message=message, scope='CACHE_CORE', **kwargs)
        except RuntimeError:
            # Gateway unavailable, silently skip tracing
            pass


class _ThreadSafeDict:
    """Thread-safe dictionary with read-write locking.

    Provides concurrent read access and exclusive write access.
    All dict operations are automatically protected by appropriate locks.
    """

    def __init__(self) -> None:
        """Initialize thread-safe dictionary."""
        self._data: dict[str, Any] = {}
        self._lock = threading.RLock()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with read lock."""
        with self._lock:
            return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get value with read lock."""
        with self._lock:
            return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value with write lock."""
        with self._lock:
            self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete value with write lock."""
        with self._lock:
            del self._data[key]

    def __contains__(self, key: str) -> bool:
        """Check membership with read lock."""
        with self._lock:
            return key in self._data

    def __len__(self) -> int:
        """Get length with read lock."""
        with self._lock:
            return len(self._data)

    def items(self) -> Any:
        """Get items with read lock."""
        with self._lock:
            return self._data.items()

    def keys(self) -> Any:
        """Get keys with read lock."""
        with self._lock:
            return self._data.keys()

    def values(self) -> Any:
        """Get values with read lock."""
        with self._lock:
            return self._data.values()

    def pop(self, key: str, default: Any = None) -> Any:
        """Pop value with write lock."""
        with self._lock:
            return self._data.pop(key, default)

    def clear(self) -> None:
        """Clear dictionary with write lock."""
        with self._lock:
            self._data.clear()

    def update(self, other: dict[str, Any]) -> None:
        """Update dictionary with write lock."""
        with self._lock:
            self._data.update(other)


class LUGSIntegratedCache:
    """In-memory cache with LUGS integration, metrics, and rate limiting."""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, max_bytes: int = MAX_CACHE_BYTES, correlation_id: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize LUGS-integrated cache.

        Args:
            max_bytes: Maximum cache size in bytes
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments
        """
        _trace_cache_core("LUGSIntegratedCache.__init__ called",
                         max_bytes=max_bytes, correlation_id=correlation_id)

        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache")

        self._debug_helper = DebugLoggingHelper(scope="CACHE")
        self._debug_helper.set_gateway(execute_operation, GatewayInterface)

        should_log = hash(time.time_ns()) % 10 == 0

        if should_log:
            self._debug_helper.log_debug(correlation_id,
                               message="LUGSIntegratedCache.__init__ called",
                               max_bytes=max_bytes)

        timing_ctx = self._debug_helper.timing_context(correlation_id, "LUGSIntegratedCache.__init__",
            max_bytes=max_bytes) if should_log else nullcontext()

        with timing_ctx:
            self._cache: _ThreadSafeDict = _ThreadSafeDict()
            self.max_bytes = max_bytes
            self.current_bytes = 0
            self._rate_limiter = deque(maxlen=RATE_LIMIT_MAX_OPS)
            self._rate_limit_window_ms = RATE_LIMIT_WINDOW_MS
            self._rate_limited_count = 0

            self._last_memory_check_time = 0.0
            self._memory_check_interval_ms = CACHE_MEMORY_CHECK_INTERVAL_MS
            self._operation_count_since_check = 0
            self._memory_check_sample_rate = CACHE_MEMORY_CHECK_SAMPLE_RATE
            self._last_memory_pressure_result = False

            self._lru_heap: list[tuple[float, str]] = []

            self._debug_helper.log_debug(correlation_id,
                               message="LUGSIntegratedCache.__init__ completed", success=True)

        _trace_cache_core("LUGSIntegratedCache.__init__ completed",
                         max_bytes=max_bytes, correlation_id=correlation_id,
                         cache_size=len(self._cache), current_bytes=self.current_bytes)

    def _check_rate_limit(self, correlation_id: Optional[str] = None, **_kwargs: Any) -> bool:
        """Check if rate limit exceeded using sliding window.

        Args:
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments

        Returns:
            True if under rate limit, False if exceeded
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        _trace_cache_core("Cache rate limit check",
                         correlation_id=correlation_id)

        should_log = (secrets.randbits(8) < 13)

        if should_log:
            self._debug_helper.log_debug(correlation_id,
                               message="_check_rate_limit called")

        timing_ctx = self._debug_helper.timing_context(correlation_id, "_check_rate_limit") if should_log else nullcontext()

        with timing_ctx:
            now = time.time() * 1000

            while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
                self._rate_limiter.popleft()

            if len(self._rate_limiter) >= RATE_LIMIT_MAX_OPS:
                self._rate_limited_count += 1
                self._debug_helper.log_debug(correlation_id,
                                   message="_check_rate_limit completed",
                                   success=False, reason="Rate limit exceeded")
                _trace_cache_core("Cache rate limit exceeded",
                                 rate_limited=True, correlation_id=correlation_id)
                return False

            self._rate_limiter.append(now)
            self._debug_helper.log_debug(correlation_id,
                               message="_check_rate_limit completed",
                               success=True, rate_limited=False)
            _trace_cache_core("Cache rate limit check passed",
                             rate_limited=False, correlation_id=correlation_id)
            return True

    def _calculate_entry_size(self, key: str, value: Any, correlation_id: Optional[str] = None, **_kwargs: Any) -> int:
        """Calculate accurate memory size of cache entry.

        Uses safe serialization for accurate size estimation with safety margin.

        Args:
            key: Cache key
            value: Cache value
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments

        Returns:
            Estimated size in bytes with 50% safety margin
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        _trace_cache_core("Cache entry size calculation",
                         key_length=len(key) if key else 0, value_type=type(value).__name__,
                         correlation_id=correlation_id)

        self._debug_helper.log_debug(correlation_id,
                           message="_calculate_entry_size called",
                           key_length=len(key) if key else 0, value_type=type(value).__name__)
        timing_ctx = self._debug_helper.timing_context(correlation_id, "_calculate_entry_size",
            key_length=len(key) if key else 0, value_type=type(value).__name__)
        try:
            with timing_ctx:
                # Base overhead for Python objects
                size = 100

                # Key size (UTF-8 encoded)
                size += len(key.encode('utf-8'))

                # Value size using safe serialization from lee_security
                try:
                    from lee_security import safe_dumps
                    size += len(safe_dumps(value))
                except (ImportError, TypeError, AttributeError):
                    # Fallback: estimate with safety margin
                    size += sys.getsizeof(value) * 2

                # Add 50% safety margin for overhead and fragmentation
                result = int(size * 1.5)

            self._debug_helper.log_debug(correlation_id,
                               message="_calculate_entry_size completed",
                               success=True, estimated_size=result)
            return result
        except (TypeError, AttributeError, OverflowError, MemoryError) as e:
            self._debug_helper.log_debug(correlation_id,
                               message="_calculate_entry_size failed",
                               error_type=type(e).__name__, error=str(e))
            return 1024

    def _check_memory_pressure(self, correlation_id: Optional[str] = None, **_kwargs: Any) -> bool:
        """Check if cache is under memory pressure (>80% full).

        Uses lazy evaluation to reduce overhead:
        - Only checks when time-based interval elapsed
        - Uses random sampling when not due for check
        - Caches last result to avoid redundant calculations

        Args:
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments

        Returns:
            True if under memory pressure, False otherwise
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        self._operation_count_since_check += 1
        now = time.time() * 1000
        time_since_last_check = now - self._last_memory_check_time

        utilization = (self.current_bytes / self.max_bytes) * 100 if self.max_bytes > 0 else 0
        should_check = (
            time_since_last_check >= self._memory_check_interval_ms or
            (secrets.randbelow(100) < (self._memory_check_sample_rate * 100)) or
            utilization >= 90.0
        )

        if not should_check:
            self._debug_helper.log_debug(correlation_id,
                               message="_check_memory_pressure skipped (lazy check)",
                               cached_result=self._last_memory_pressure_result,
                               time_since_last_check_ms=time_since_last_check,
                               operations_since_check=self._operation_count_since_check)
            _trace_cache_core("Cache memory pressure check skipped (lazy)",
                             cached_result=self._last_memory_pressure_result,
                             utilization_percent=utilization,
                             correlation_id=correlation_id)
            return self._last_memory_pressure_result

        _trace_cache_core("Cache memory pressure check",
                         current_bytes=self.current_bytes, max_bytes=self.max_bytes,
                         utilization_percent=utilization, correlation_id=correlation_id)

        self._debug_helper.log_debug(correlation_id,
                           message="_check_memory_pressure called",
                           current_bytes=self.current_bytes, max_bytes=self.max_bytes)
        timing_ctx = self._debug_helper.timing_context(correlation_id, "_check_memory_pressure")
        try:
            with timing_ctx:
                result = self.current_bytes > (self.max_bytes * 0.8)

            self._last_memory_check_time = now
            self._operation_count_since_check = 0
            self._last_memory_pressure_result = result

            self._debug_helper.log_debug(correlation_id,
                               message="_check_memory_pressure completed",
                               success=True, under_pressure=result, utilization_percent=utilization)

            _trace_cache_core("Cache memory pressure check completed",
                             under_pressure=result, utilization_percent=utilization,
                             correlation_id=correlation_id)
            return result
        except (ZeroDivisionError, OverflowError, ArithmeticError) as e:
            self._debug_helper.log_debug(correlation_id,
                               message="_check_memory_pressure failed",
                               error_type=type(e).__name__, error=str(e))
            raise

    def _evict_lru_entries(self, bytes_needed: int, correlation_id: Optional[str] = None, **_kwargs: Any) -> int:
        """Evict least recently used entries to free memory.

        Args:
            bytes_needed: Number of bytes to free
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments

        Returns:
            Number of entries evicted
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        _trace_cache_core("Cache LRU eviction started",
                         bytes_needed=bytes_needed, cache_size=len(self._cache),
                         correlation_id=correlation_id)

        self._debug_helper.log_debug(correlation_id,
                           message="_evict_lru_entries called",
                           bytes_needed=bytes_needed, cache_size=len(self._cache))
        timing_ctx = self._debug_helper.timing_context(correlation_id, "_evict_lru_entries",
            bytes_needed=bytes_needed, cache_size=len(self._cache))
        try:
            with timing_ctx:
                if not self._cache:
                    self._debug_helper.log_debug(correlation_id,
                                       message="_evict_lru_entries completed",
                                       success=True, evicted_count=0, reason="Cache is empty")
                    return 0

                bytes_freed = 0
                evicted_count = 0
                evicted_keys = set()

                while self._lru_heap and bytes_freed < bytes_needed:
                    last_access, key = heapq.heappop(self._lru_heap)

                    if key in self._cache and key not in evicted_keys:
                        entry = self._cache[key]
                        bytes_freed += entry.value_size_bytes
                        self.current_bytes -= entry.value_size_bytes
                        del self._cache[key]
                        evicted_keys.add(key)
                        evicted_count += 1

                if evicted_count > 0:
                    execute_operation(GatewayInterface.OBSERVABILITY, "increment_counter",
                                     metric_name="cache.entries_evicted", value=evicted_count)

            self._debug_helper.log_debug(correlation_id,
                               message="_evict_lru_entries completed",
                               success=True, evicted_count=evicted_count, bytes_freed=bytes_freed)

            _trace_cache_core("Cache LRU eviction completed",
                             evicted_count=evicted_count, bytes_freed=bytes_freed,
                             correlation_id=correlation_id)
            return evicted_count
        except (IndexError, ValueError, KeyError, OverflowError) as e:
            self._debug_helper.log_debug(correlation_id,
                               message="_evict_lru_entries failed",
                               error_type=type(e).__name__, error=str(e))
            raise

    def _handle_memory_pressure(self, correlation_id: Optional[str] = None, **_kwargs: Any) -> None:
        """Handle memory pressure by evicting entries.

        Args:
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        _trace_cache_core("Cache memory pressure handling started",
                         correlation_id=correlation_id)

        self._debug_helper.log_debug(correlation_id,
                           message="_handle_memory_pressure called")
        timing_ctx = self._debug_helper.timing_context(correlation_id, "_handle_memory_pressure")
        try:
            with timing_ctx:
                bytes_to_free = int(self.max_bytes * 0.2)
                evicted = self._evict_lru_entries(bytes_to_free, correlation_id=correlation_id)
            self._debug_helper.log_debug(correlation_id,
                               message="_handle_memory_pressure completed",
                               success=True, bytes_freed_target=bytes_to_free, evicted_count=evicted)

            _trace_cache_core("Cache memory pressure handling completed",
                             bytes_freed_target=bytes_to_free, evicted_count=evicted,
                             correlation_id=correlation_id)
        except (OverflowError, ArithmeticError, RuntimeError) as e:
            self._debug_helper.log_debug(correlation_id,
                               message="_handle_memory_pressure failed",
                               error_type=type(e).__name__, error=str(e))
            raise

    def _validate_security_requirements(self, key: str, ttl: int,
                                       source_module: Optional[str],
                                       correlation_id: str) -> None:
        """Validate cache operation security requirements.

        Args:
            key: Cache key to validate
            ttl: TTL value to validate
            source_module: Optional source module name
            correlation_id: Correlation ID for tracking
        """
        try:
            execute_operation(GatewayInterface.SECURITY, "validate_cache_key", key=key)
            execute_operation(GatewayInterface.SECURITY, "validate_ttl", ttl=ttl)
            if source_module:
                execute_operation(GatewayInterface.SECURITY, "validate_module_name",
                               module_name=source_module)
        except RuntimeError as e:
            if "Security interface unavailable" in str(e):
                self._debug_helper.log_debug(correlation_id,
                                   message="Security validation skipped (unavailable)")
            else:
                raise

    def _compress_if_needed(self, value: Any, key: str,
                          correlation_id: str) -> Optional[tuple[Any, dict[str, Any]]]:
        """Compress value if compression is enabled.

        Args:
            value: Value to compress
            key: Cache key
            correlation_id: Correlation ID for tracking

        Returns:
            Tuple of (compressed_value, compression_metadata)
        """
        _trace_cache_core("Cache compression started",
                         key=key, value_type=type(value).__name__,
                         correlation_id=correlation_id)

        try:
            compressor = get_cache_compressor()
            result = compressor.compress(value, key=key)

            _trace_cache_core("Cache compression completed",
                             key=key, compressed=result is not None,
                             correlation_id=correlation_id)
            return result
        except (ValueError, TypeError, RuntimeError, MemoryError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_warning",
                           message=f"Compression failed for key {key}, storing uncompressed: {e}",
                           corr_id=correlation_id)
            _trace_cache_core("Cache compression failed",
                             key=key, error_type=type(e).__name__,
                             error=str(e), correlation_id=correlation_id)
            return value, None

    def _ensure_capacity_for_entry(self, key: str, value: Any,
                                  correlation_id: str) -> int:
        """Ensure cache has capacity for new entry, return entry size.

        Args:
            key: Cache key
            value: Cache value
            correlation_id: Correlation ID for tracking

        Returns:
            Entry size in bytes
        """
        _trace_cache_core("Cache capacity check started",
                         key=key, correlation_id=correlation_id)

        entry_size = self._calculate_entry_size(key, value, correlation_id=correlation_id)

        if self._check_memory_pressure(correlation_id=correlation_id):
            self._handle_memory_pressure(correlation_id=correlation_id)

        if self.current_bytes + entry_size > self.max_bytes:
            bytes_needed = entry_size - (self.max_bytes - self.current_bytes)
            _trace_cache_core("Cache capacity exceeded, eviction required",
                             bytes_needed=bytes_needed, current_bytes=self.current_bytes,
                             max_bytes=self.max_bytes, correlation_id=correlation_id)
            self._evict_lru_entries(bytes_needed, correlation_id=correlation_id)

        _trace_cache_core("Cache capacity ensured",
                         entry_size=entry_size, key=key, correlation_id=correlation_id)
        return entry_size

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _update_or_create_entry(self, key: str, compressed_value: Any,
                               entry_size: int, ttl: int, source_module: Optional[str],
                               compression_metadata: Optional[dict[str, Any]]) -> bool:
        """Update existing entry or create new one.

        Performance: O(log n) heap push on new entries.

        Args:
            key: Cache key
            compressed_value: Compressed cache value
            entry_size: Size of entry in bytes
            ttl: Time-to-live in seconds
            source_module: Optional source module name
            compression_metadata: Optional compression metadata

        Returns:
            True if update, False if new entry
        """
        is_update = key in self._cache

        _trace_cache_core("Cache entry update/create",
                         key=key, is_update=is_update, entry_size=entry_size,
                         ttl=ttl, source_module=source_module)
        if is_update:
            old_entry = self._cache[key]
            self.current_bytes -= old_entry.value_size_bytes
        else:
            current_time = time.time()
            heapq.heappush(self._lru_heap, (current_time, key))

        current_time = time.time()
        entry = CacheEntry(
            value=compressed_value,
            timestamp=current_time,
            ttl=ttl,
            source_module=source_module,
            access_count=0,
            last_access=current_time,
            value_size_bytes=entry_size,
            compression_metadata=compression_metadata,
        )

        self._cache[key] = entry
        self.current_bytes += entry_size

        execute_operation(GatewayInterface.OBSERVABILITY, "increment_counter",
                       metric_name="cache.total_sets")

        _trace_cache_core("Cache entry update/create completed",
                         key=key, is_update=is_update,
                         current_cache_size=len(self._cache),
                         current_bytes=self.current_bytes)
        return is_update

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL,
            source_module: Optional[str] = None, correlation_id: Optional[str] = None, **_kwargs: Any) -> None:
        """Set cache entry with TTL and optional module tracking.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            source_module: Optional source module name
            correlation_id: Optional correlation ID for tracking
            **kwargs: Additional keyword arguments
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("cache")

        _trace_cache_core("Cache set called",
                         key=key, ttl=ttl, source_module=source_module,
                         value_type=type(value).__name__, correlation_id=correlation_id)

        self._debug_helper.log_debug(correlation_id,
                           message="set called",
                           key=key, ttl=ttl, source_module=source_module, value_type=type(value).__name__)
        timing_ctx = self._debug_helper.timing_context(correlation_id, "set",
            key=key, ttl=ttl, source_module=source_module,
            value_type=type(value).__name__)
        try:
            with timing_ctx:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    self._debug_helper.log_debug(correlation_id,
                                       message="set completed",
                                       success=False, reason="Rate limited")
                    return

                self._validate_security_requirements(key, ttl, source_module, correlation_id)

                entry_size = self._ensure_capacity_for_entry(key, value, correlation_id)

                compressed_value, compression_metadata = self._compress_if_needed(
                    value, key, correlation_id)

                entry_size = self._calculate_entry_size(key, compressed_value,
                                                       correlation_id=correlation_id)

                is_update = self._update_or_create_entry(
                    key, compressed_value, entry_size, ttl, source_module,
                    compression_metadata)

                if source_module:
                    try:
                        from lee.gateway import add_cache_module_dependency  # pylint: disable=import-outside-toplevel
                        add_cache_module_dependency(source_module, key)
                    except ImportError:
                        pass

            self._debug_helper.log_debug(correlation_id,
                               message="set completed",
                               success=True, is_update=is_update, entry_size=entry_size)

            _trace_cache_core("Cache set completed",
                             key=key, success=True, is_update=is_update,
                             entry_size=entry_size, correlation_id=correlation_id)
        except (ValueError, KeyError, RuntimeError, MemoryError, OverflowError) as e:
            self._debug_helper.log_debug(correlation_id,
                               message="set failed",
                               error_type=type(e).__name__, error=str(e))
            _trace_cache_core("Cache set failed",
                             key=key, error_type=type(e).__name__,
                             error=str(e), correlation_id=correlation_id)
            raise


_cache_instance = None


__all__ = [
    "LUGSIntegratedCache",
]

# EOF
