"""cache_operations_split/lugs_operations.py

LUGSIntegratedCacheOperations class with debug tracing.
"""

from __future__ import annotations

import time
import threading
from typing import Any, Optional

from lee.gateway import execute_operation, GatewayInterface, generate_correlation_id
from lee.lee_cache.cache_observability_split import get_cache_observability
from lee.lee_cache.cache_operations_split.models import (
    _get_gateway,
    _get_cache_observability_instance,
)
from lee.lee_cache.cache_enums import (
    _CACHE_MISS,
    DEFAULT_CACHE_TTL,
)
from lee.lee_cache.cache_generic import LUGSIntegratedCache
from lee.lee_utility.debug_logging_helper import DebugLoggingHelper
from lee.lee_cache.cache_compression import get_cache_compressor
from lee.lee_cache.cache_key_optimizer import get_cache_key_optimizer

# pylint: disable=import-outside-toplevel
# Lazy imports below are for optional dependencies to avoid circular imports
try:
    from lee.lee_logging import get_logger
    _debug_logger = get_logger(__name__)
except ImportError:
    _debug_logger = None

class LUGSIntegratedCacheOperations(LUGSIntegratedCache):
    """Extended cache operations with debug tracing."""

    def __init__(self, *args, **kwargs):
        """Initialize cache operations with debug logging helper."""
        super().__init__(*args, **kwargs)
        self._debug_helper = DebugLoggingHelper(scope="CACHE")

    def _get_debug_helper(self):
        """Get debug helper with gateway functions loaded."""
        _GatewayInterface, _execute_operation = _get_gateway()
        if _execute_operation and _GatewayInterface:
            self._debug_helper.set_gateway(_execute_operation, _GatewayInterface)
        return self._debug_helper

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    # Complex cache operation requires comprehensive logic
    def get(self, key: str, correlation_id: str = None, **_kwargs) -> Any:
        """Get cached value if exists and not expired."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        if correlation_id is None:
            # Use utility function
            correlation_id = generate_correlation_id(prefix="cache")

        # Get debug helper
        _debug = self._get_debug_helper()

        # Optimize and track key
        try:
            key_optimizer = get_cache_key_optimizer()
            optimized_key = key_optimizer.optimize_key(key, use_hash=False, correlation_id=correlation_id)
        except (ImportError, RuntimeError, ValueError, TypeError):
            # Fallback to original key if optimizer unavailable
            optimized_key = key

        # SUGA-ISP compliance - all debug through execute_operation (lazy import)
        _debug.log_operation_start(correlation_id, "get", key=key, optimized_key=optimized_key)

        timing_ctx = _debug.timing_context(correlation_id, "get", key=key)

        # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "get completed", success=False, reason="Rate limited")
                    return _CACHE_MISS

                if optimized_key not in self._cache:
                    # Record miss metrics
                    duration_ms = (time.time() - _operation_start_time) * 1000
                    try:
                        get_obs = _get_cache_observability_instance()
                        if get_obs:
                            observability = get_obs()
                            observability.record_operation("get", hit=False, miss=True, latency_ms=duration_ms, key=key, correlation_id=correlation_id)
                        key_optimizer.record_key_access(key, hit=False, correlation_id=correlation_id)
                    except (ImportError, RuntimeError, ValueError, TypeError) as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'(ImportError, Exception) occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

                    _debug.record_metrics(operation_name="get", miss=True)
                    _debug.log_debug(correlation_id, "get completed", success=False, reason="Key not found")
                    return _CACHE_MISS

                try:
                    entry = self._cache[optimized_key]
                except KeyError:
                    # Record miss metrics
                    duration_ms = (time.time() - _operation_start_time) * 1000
                    try:
                        observability = get_cache_observability()
                        observability.record_operation("get", hit=False, miss=True, latency_ms=duration_ms, key=key, correlation_id=correlation_id)
                        key_optimizer.record_key_access(key, hit=False, correlation_id=correlation_id)
                    except (ImportError, RuntimeError, ValueError, TypeError) as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'(ImportError, Exception) occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

                    _debug.record_metrics(operation_name="get", miss=True)
                    _debug.log_debug(correlation_id, "get completed", success=False, reason="Key deleted during check")
                    return _CACHE_MISS

                # PERFORMANCE: Reuse cached timestamp instead of calling time.time() again
                current_time = _operation_start_time
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    try:
                        del self._cache[key]
                    except KeyError as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'KeyError occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

                    _debug.increment_metrics("cache.entries_expired")
                    _debug.record_metrics(operation_name="get", miss=True)
                    _debug.log_debug(correlation_id, "get completed", success=False, reason="Entry expired",
                                        age=age, ttl=entry.ttl)
                    return _CACHE_MISS

                entry.access_count += 1
                entry.last_access = current_time

                _debug.record_metrics(operation_name="get", hit=True)

                # Always decompress (handles None metadata for uncompressed data)
                return_value = entry.value
                try:
                    compressor = get_cache_compressor()
                    return_value = compressor.decompress(entry.value, entry.compression_metadata)
                except (ValueError, TypeError, RuntimeError) as e:
                    # Decompression failed, log error and return as-is
                    _debug.log_error(correlation_id,
                                   f"Decompression failed for key {key}: {type(e).__name__}: {e}")

                _debug.log_debug(correlation_id, "get completed", success=True, hit=True, access_count=entry.access_count)
                return return_value
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "get failed", error_type=type(e).__name__, error=str(e))
                raise

    def exists(self, key: str, correlation_id: str = None, **_kwargs) -> bool:
        """Check if key exists and is not expired."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "exists called", key=key)

        timing_ctx = _debug.timing_context(correlation_id, "exists", key=key)

        # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "exists completed", success=False, reason="Rate limited")
                    return False

                if key not in self._cache:
                    _debug.log_debug(correlation_id, "exists completed", success=True, exists=False, reason="Key not found")
                    return False

                entry = self._cache[key]
                # PERFORMANCE: Reuse cached timestamp for age check
                current_time = _operation_start_time
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]

                    _debug.increment_metrics("cache.entries_expired")
                    _debug.log_debug(correlation_id, "exists completed", success=True, exists=False, reason="Entry expired")
                    return False

                _debug.log_debug(correlation_id, "exists completed", success=True, exists=True, age=age, ttl=entry.ttl)
                return True
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "exists failed", error_type=type(e).__name__, error=str(e))
                raise

    def delete(self, key: str, correlation_id: str = None, **_kwargs) -> bool:
        """Delete cache entry if it exists."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "delete called", key=key)

        timing_ctx = _debug.timing_context(correlation_id, "delete", key=key)

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "delete completed", success=False, reason="Rate limited")
                    return False

                if key in self._cache:
                    entry = self._cache[key]
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    _debug.log_debug(correlation_id, "delete completed", success=True, deleted=True, entry_size=entry.value_size_bytes)
                    return True

                _debug.log_debug(correlation_id, "delete completed", success=True, deleted=False, reason="Key not found")
                return False
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "delete failed", error_type=type(e).__name__, error=str(e))
                raise

    def clear(self, correlation_id: str = None, **_kwargs) -> int:
        """Clear all cache entries."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "clear called")

        timing_ctx = _debug.timing_context(correlation_id, "clear")

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "clear completed", success=False, reason="Rate limited", cleared_count=0)
                    return 0

                count = len(self._cache)
                self._cache.clear()
                self.current_bytes = 0
                _debug.log_debug(correlation_id, "clear completed", success=True, cleared_count=count)
                return count
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "clear failed", error_type=type(e).__name__, error=str(e))
                raise

    def reset(self, correlation_id: str = None, **_kwargs) -> bool:
        """Reset cache to initial state."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "reset called")

        timing_ctx = _debug.timing_context(correlation_id, "reset")

        with timing_ctx:
            try:
                self._cache.clear()
                self.current_bytes = 0
                self._rate_limiter.clear()
                self._rate_limited_count = 0
                _debug.log_debug(correlation_id, "reset completed", success=True)
                return True
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "reset failed", error_type=type(e).__name__, error=str(e))
                raise

    def cleanup_expired(self, correlation_id: str = None, **_kwargs) -> int:
        """Remove all expired entries."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache")

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "cleanup_expired called")

        timing_ctx = _debug.timing_context(correlation_id, "cleanup_expired")

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "cleanup_expired completed", success=False, reason="Rate limited", cleaned_count=0)
                    return 0

                # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
                current_time = time.time()

                expired_items = [
                    (key, entry) for key, entry in self._cache.items()
                    if current_time - entry.timestamp > entry.ttl
                ]

                for key, entry in expired_items:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]

                count = len(expired_items)

                if count > 0:
                    _debug.increment_metrics("cache.entries_expired", count)

                _debug.log_debug(correlation_id, "cleanup_expired completed", success=True, cleaned_count=count)
                return count
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "cleanup_expired failed", error_type=type(e).__name__, error=str(e))
                raise

    def get_metadata(self, key: str, correlation_id: str = None, **_kwargs) -> Optional[dict[str, Any]]:
        """Get cache entry metadata without accessing value."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "get_metadata called", key=key)

        timing_ctx = _debug.timing_context(correlation_id, "get_metadata", key=key)

        # PERFORMANCE: Cache timestamp at operation start to avoid repeated system calls
        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "get_metadata completed", success=False, reason="Rate limited")
                    return None

                _debug.increment_metrics("cache.metadata_queries")

                if key not in self._cache:
                    _debug.log_debug(correlation_id, "get_metadata completed", success=False, reason="Key not found")
                    return None

                entry = self._cache[key]
                # PERFORMANCE: Reuse cached timestamp for age check
                current_time = _operation_start_time
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    _debug.increment_metrics("cache.entries_expired")
                    _debug.log_debug(correlation_id, "get_metadata completed", success=False, reason="Entry expired")
                    return None

                metadata = {
                    "source_module": entry.source_module,
                    "timestamp": entry.timestamp,
                    "age_seconds": age,
                    "ttl": entry.ttl,
                    "ttl_remaining": max(0, entry.ttl - age),
                    "access_count": entry.access_count,
                    "last_access": entry.last_access,
                    "size_bytes": entry.value_size_bytes,
                    "is_expired": False,
                }

                _debug.log_debug(correlation_id, "get_metadata completed", success=True, has_metadata=True)
                return metadata
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "get_metadata failed", error_type=type(e).__name__, error=str(e))
                raise

    def get_stats(self, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
        """Get cache statistics."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "get_stats called")

        timing_ctx = _debug.timing_context(correlation_id, "get_stats")

        with timing_ctx:
            try:
                stats = {
                    "size": len(self._cache),
                    "memory_bytes": self.current_bytes,
                    "memory_mb": round(self.current_bytes / (1024 * 1024), 2),
                    "max_bytes": self.max_bytes,
                    "max_mb": round(self.max_bytes / (1024 * 1024), 2),
                    "memory_utilization_percent": round((self.current_bytes / self.max_bytes) * 100, 2) if self.max_bytes > 0 else 0,
                    "default_ttl_seconds": DEFAULT_CACHE_TTL,
                    "rate_limited_count": self._rate_limited_count,
                }

                # Add compression statistics if available
                try:
                    compressor = get_cache_compressor()
                    compression_stats = compressor.get_stats()
                    stats["compression"] = compression_stats.to_dict()
                except ImportError:
                    # Compression module not available
                    pass
                    stats["compression"] = None

                _debug.log_debug(correlation_id, "get_stats completed", success=True, cache_size=stats["size"],
                                    utilization=stats["memory_utilization_percent"])
                return stats
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "get_stats failed", error_type=type(e).__name__, error=str(e))
                raise

    def get_module_dependencies(self, correlation_id: str = None, **_kwargs) -> set[str]:
        """Get set of all module names that have cache dependencies."""
        # SUGA-ISP compliance - lazy load gateway
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "get_module_dependencies called")

        timing_ctx = _debug.timing_context(correlation_id, "get_module_dependencies")

        with timing_ctx:
            try:
                modules = set()
                for entry in self._cache.values():
                    if entry.source_module:
                        modules.add(entry.source_module)

                _debug.log_debug(correlation_id, "get_module_dependencies completed", success=True, module_count=len(modules))
                return modules
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "get_module_dependencies failed", error_type=type(e).__name__, error=str(e))
                raise

    def keys(self, correlation_id: str = None, **_kwargs) -> list[str]:
        """Get all non-expired cache keys."""
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "keys called")

        timing_ctx = _debug.timing_context(correlation_id, "keys")

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "keys completed", success=False, reason="Rate limited")
                    return []

                current_time = _operation_start_time
                valid_keys = [
                    key for key, entry in self._cache.items()
                    if current_time - entry.timestamp <= entry.ttl
                ]

                _debug.log_debug(correlation_id, "keys completed", success=True, key_count=len(valid_keys))
                return valid_keys
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "keys failed", error_type=type(e).__name__, error=str(e))
                raise

    def values(self, correlation_id: str = None, **_kwargs) -> list[Any]:
        """Get all non-expired cache values."""
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "values called")

        timing_ctx = _debug.timing_context(correlation_id, "values")

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "values completed", success=False, reason="Rate limited")
                    return []

                current_time = _operation_start_time
                result = []
                compressor = get_cache_compressor()

                for _key, entry in self._cache.items():
                    if current_time - entry.timestamp <= entry.ttl:
                        value = entry.value
                        try:
                            value = compressor.decompress(value, entry.compression_metadata)
                        except (ValueError, TypeError, RuntimeError) as e:
                            try:
                                execute_operation(
                                    GatewayInterface.LOGGING,
                                    'log_error',
                                    message=f'(ValueError, TypeError, RuntimeError) occurred: {e}',
                                    corr_id=None
                                )
                            except (ImportError, AttributeError, RuntimeError):
                                pass  # Gateway not available
                        result.append(value)

                _debug.log_debug(correlation_id, "values completed", success=True, value_count=len(result))
                return result
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "values failed", error_type=type(e).__name__, error=str(e))
                raise

    def items(self, correlation_id: str = None, **_kwargs) -> dict[str, Any]:
        """Get all non-expired cache key-value pairs."""
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "items called")

        timing_ctx = _debug.timing_context(correlation_id, "items")

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "items completed", success=False, reason="Rate limited")
                    return {}

                current_time = _operation_start_time
                result = {}
                compressor = get_cache_compressor()

                for key, entry in self._cache.items():
                    if current_time - entry.timestamp <= entry.ttl:
                        value = entry.value
                        try:
                            value = compressor.decompress(value, entry.compression_metadata)
                        except (ValueError, TypeError, RuntimeError) as e:
                            try:
                                execute_operation(
                                    GatewayInterface.LOGGING,
                                    'log_error',
                                    message=f'(ValueError, TypeError, RuntimeError) occurred: {e}',
                                    corr_id=None
                                )
                            except (ImportError, AttributeError, RuntimeError):
                                pass  # Gateway not available
                        result[key] = value

                _debug.log_debug(correlation_id, "items completed", success=True, item_count=len(result))
                return result
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "items failed", error_type=type(e).__name__, error=str(e))
                raise

    def pop(self, key: str, default: Any = None, correlation_id: str = None, **_kwargs) -> Any:
        """Remove and return value if exists and not expired.

        Args:
            key: Cache key to pop
            default: Default value if key not found
            correlation_id: Optional correlation ID for tracking

        Returns:
            Cached value or default if not found
        """
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "pop called", key=key)

        timing_ctx = _debug.timing_context(correlation_id, "pop", key=key)

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "pop completed", success=False, reason="Rate limited")
                    return default

                if key not in self._cache:
                    _debug.log_debug(correlation_id, "pop completed", success=True, found=False, returned_default=True)
                    return default

                entry = self._cache[key]
                current_time = _operation_start_time
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    _debug.increment_metrics("cache.entries_expired")
                    _debug.log_debug(correlation_id, "pop completed", success=True, found=False, reason="Entry expired", returned_default=True)
                    return default

                value = entry.value
                try:
                    compressor = get_cache_compressor()
                    value = compressor.decompress(value, entry.compression_metadata)
                except (ValueError, TypeError, RuntimeError) as e:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f'(ValueError, TypeError, RuntimeError) occurred: {e}',
                            corr_id=None
                        )
                    except (ImportError, AttributeError, RuntimeError):
                        pass  # Gateway not available

                self.current_bytes -= entry.value_size_bytes
                del self._cache[key]

                _debug.log_debug(correlation_id, "pop completed", success=True, found=True, value_size=entry.value_size_bytes)
                return value
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "pop failed", error_type=type(e).__name__, error=str(e))
                raise

    def update(self, items: dict[str, Any], ttl: int = DEFAULT_CACHE_TTL,
               source_module: Optional[str] = None, correlation_id: str = None, **kwargs) -> int:
        """Update cache with multiple key-value pairs.

        Args:
            items: Dictionary of key-value pairs to set
            ttl: Time-to-live for all entries
            source_module: Optional source module name
            correlation_id: Optional correlation ID for tracking

        Returns:
            Number of keys updated
        """
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "update called", item_count=len(items), ttl=ttl)

        timing_ctx = _debug.timing_context(correlation_id, "update")

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "update completed", success=False, reason="Rate limited", updated_count=0)
                    return 0

                count = 0
                for key, value in items.items():
                    try:
                        self.set(key, value, ttl=ttl, source_module=source_module, correlation_id=correlation_id, **kwargs)
                        count += 1
                    except (RuntimeError, ValueError, TypeError) as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'Exception occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

                _debug.log_debug(correlation_id, "update completed", success=True, updated_count=count)
                return count
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "update failed", error_type=type(e).__name__, error=str(e))
                raise

    def touch(self, key: str, ttl: Optional[int] = None, correlation_id: str = None, **_kwargs) -> bool:
        """Reset TTL for a key without changing its value.

        Args:
            key: Cache key to touch
            ttl: New TTL (uses existing TTL if None)
            correlation_id: Optional correlation ID for tracking

        Returns:
            True if key was touched, False if not found
        """
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "touch called", key=key, ttl=ttl)

        timing_ctx = _debug.timing_context(correlation_id, "touch", key=key)

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "touch completed", success=False, reason="Rate limited")
                    return False

                if key not in self._cache:
                    _debug.log_debug(correlation_id, "touch completed", success=True, touched=False, reason="Key not found")
                    return False

                entry = self._cache[key]
                current_time = _operation_start_time
                age = current_time - entry.timestamp

                if age > entry.ttl:
                    self.current_bytes -= entry.value_size_bytes
                    del self._cache[key]
                    _debug.increment_metrics("cache.entries_expired")
                    _debug.log_debug(correlation_id, "touch completed", success=True, touched=False, reason="Entry expired")
                    return False

                new_ttl = ttl if ttl is not None else entry.ttl
                entry.timestamp = current_time
                entry.ttl = new_ttl

                _debug.log_debug(correlation_id, "touch completed", success=True, touched=True, new_ttl=new_ttl)
                return True
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "touch failed", error_type=type(e).__name__, error=str(e))
                raise

    def increment(self, key: str, delta: int = 1, ttl: int = DEFAULT_CACHE_TTL,
                  correlation_id: str = None, **kwargs) -> int:
        """Increment a counter value in cache.

        Args:
            key: Cache key for counter
            delta: Amount to increment (default 1)
            ttl: Time-to-live for new entries
            correlation_id: Optional correlation ID for tracking

        Returns:
            New counter value
        """
        _GatewayInterface, _execute_operation = _get_gateway()

        _debug = self._get_debug_helper()
        _debug.log_debug(correlation_id, "increment called", key=key, delta=delta)

        timing_ctx = _debug.timing_context(correlation_id, "increment", key=key)

        _operation_start_time = time.time()

        with timing_ctx:
            try:
                if not self._check_rate_limit(correlation_id=correlation_id):
                    _debug.log_debug(correlation_id, "increment completed", success=False, reason="Rate limited")
                    raise RuntimeError("Rate limit exceeded")

                if key in self._cache:
                    entry = self._cache[key]
                    current_time = _operation_start_time
                    age = current_time - entry.timestamp

                    if age > entry.ttl:
                        self.current_bytes -= entry.value_size_bytes
                        del self._cache[key]
                        new_value = delta
                    else:
                        value = entry.value
                        try:
                            compressor = get_cache_compressor()
                            value = compressor.decompress(value, entry.compression_metadata)
                        except (ValueError, TypeError, RuntimeError) as e:
                            try:
                                execute_operation(
                                    GatewayInterface.LOGGING,
                                    'log_error',
                                    message=f'(ValueError, TypeError, RuntimeError) occurred: {e}',
                                    corr_id=None
                                )
                            except (ImportError, AttributeError, RuntimeError):
                                pass  # Gateway not available

                        if isinstance(value, int):
                            new_value = value + delta
                        else:
                            new_value = delta
                else:
                    new_value = delta

                self.set(key, new_value, ttl=ttl, source_module=None, correlation_id=correlation_id, **kwargs)

                _debug.log_debug(correlation_id, "increment completed", success=True, new_value=new_value)
                return new_value
            except (KeyError, ValueError, TypeError, RuntimeError, AttributeError) as e:
                _debug.log_debug(correlation_id, "increment failed", error_type=type(e).__name__, error=str(e))
                raise


_cache_instance = None
_cache_lock = threading.Lock()
# Module-level debug helper for singleton function
_module_debug_helper = DebugLoggingHelper(scope="CACHE")