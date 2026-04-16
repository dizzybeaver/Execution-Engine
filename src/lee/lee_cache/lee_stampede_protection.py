"""lee_cache/lee_stampede_protection.py
Version: 2025-03-02_1
Purpose: Cache stampede protection for LEE - Request coalescing for Lambda concurrency
License: Apache 2.0

Prevents cache stampede (thundering herd) when multiple concurrent Lambda instances
request the same expired cache entry.

The Problem (Lambda-specific):
    When a Home Assistant entity state expires, multiple concurrent Alexa requests
    may detect the cache miss simultaneously and all attempt to fetch from HA API.
    This causes:
        - Thundering herd on Home Assistant (API rate limiting)
        - Wasted Lambda execution time (cost increase)
        - Increased latency for all requests (Alexa SLA breach)
        - Potential HA service degradation

The Solution:
    1. Request Coalescing: Multiple concurrent requests wait for single computation
    2. Cache-Based Locking: Use cache itself as distributed lock manager
    3. Lease Timeout: Prevent permanent lock if computation fails
    4. Graceful Degradation: Fall back to direct computation if locking fails

Integration with LEE SUGA-ISP:
    - Uses execute_operation(GatewayInterface.CACHE, ...) for all cache access
    - Metrics via GatewayInterface.OBSERVABILITY
    - Logging via GatewayInterface.LOGGING
    - No direct cache access - follows gateway pattern
"""

import functools  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from collections import OrderedDict  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from enum import Enum, auto  # noqa: E402
from typing import Any, Optional  # noqa: E402

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_cache.cache_enums import _CACHE_MISS, CacheError
from lee.lee_cache.exception_handler import handle_cache_exception

# Memory limits for lease registry (2026-03-29 fix)
MAX_LEASES = 1000

# Lazy import L2 cache for L2-aware stampede protection
_l2_cache_imported = False
_get_l2_cache = None


def _get_l2_cache_instance():
    """Lazy import and get L2 cache instance.

    Returns L2 cache instance if available, None otherwise.
    """
    # pylint: disable=global-statement
    global _l2_cache_imported, _get_l2_cache
    if not _l2_cache_imported:
        # pylint: disable=import-outside-toplevel
        # pylint: disable=import-outside-toplevel
        # pylint: disable=global-statement
        try:
            # pylint: disable=import-outside-toplevel
            from lee.lee_cache.cache_l2_disk import get_l2_cache
            _get_l2_cache = get_l2_cache
            _l2_cache_imported = True
        except ImportError:
            _l2_cache_imported = True
    if _get_l2_cache:
        try:
            return _get_l2_cache()
        except (ImportError, AttributeError, RuntimeError):
            # L2 cache import or initialization failed
            return None
    return None


class ComputationStatus(Enum):
    """Status of in-flight computation."""

    PENDING = auto()  # Computation in progress
    COMPLETE = auto()  # Computation complete
    FAILED = auto()  # Computation failed


@dataclass
class ComputationLease:
    """Lease for ongoing computation.

    Tracks in-flight computations to prevent duplicate work.
    Uses cache as backing store for distributed locking across Lambda instances.
    """

    key: str
    status: ComputationStatus = ComputationStatus.PENDING
    created_at: float = 0.0  # Set by factory
    expires_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[Exception] = None
    waiting_count: int = 0

    def is_expired(self) -> bool:
        """Check if lease has expired."""
        if self.expires_at is None:
            return False
        current_time = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")
        return current_time > self.expires_at

    def add_waiter(self) -> None:
        """Increment waiting thread count."""
        self.waiting_count += 1

    def remove_waiter(self) -> None:
        """Decrement waiting thread count."""
        self.waiting_count = max(0, self.waiting_count - 1)

    def has_waiters(self) -> bool:
        """Check if any threads are waiting."""
        return self.waiting_count > 0


@dataclass
class StampedeProtectionConfig:
    """Configuration for stampede protection."""

    # Lease configuration
    lease_timeout_seconds: float = 30.0  # Maximum time to hold lease
    lock_key_suffix: str = ":lock"  # Suffix for lock keys in cache

    # Request coalescing
    enable_coalescing: bool = True
    max_waiters_per_key: int = 100  # Max threads waiting for computation

    # Retry configuration
    max_wait_attempts: int = 30  # Max retry attempts when waiting
    wait_interval_seconds: float = 0.1  # Seconds between retry checks

    # Fallback behavior
    enable_fallback: bool = True  # Allow direct computation if locking fails

    # Metrics
    enable_metrics: bool = True

    # L2 Cache awareness (2026-03-25 enhancement)
    enable_l2_aware: bool = True  # Check L2 cache when L1 miss occurs
    l2_lock_coordination: bool = True  # Use L2 for cross-instance lock coordination

    # pylint: disable=too-many-instance-attributes
    # 10 instance attributes is acceptable for this configuration dataclass


class InMemoryLeaseRegistry:
    """In-memory registry for active leases.

    For Lambda single-threaded execution, this provides thread-safe
    lease tracking. For cross-instance coordination, uses cache-based locking.
    """

    def __init__(self):
        # Use OrderedDict for LRU eviction
        self._leases: OrderedDict[str, ComputationLease] = OrderedDict()
        self._lock = threading.RLock()
        self._operation_count = 0
        self._cleanup_interval = 100  # Cleanup every 100 operations

    def _maybe_cleanup(self) -> None:
        """Perform periodic cleanup based on operation count."""
        self._operation_count += 1

        if self._operation_count >= self._cleanup_interval:
            self._operation_count = 0
            cleaned = self.cleanup_expired()

            if cleaned > 0:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_debug",
                        message=f"StampedeProtection: Cleaned {cleaned} expired leases",
                        scope="STAMPEDE",
                    )
                except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                    # Logging failed - continue
                    ...

    def get_lease(self, key: str) -> Optional[ComputationLease]:
        """Get lease for key."""
        with self._lock:
            return self._leases.get(key)

    def set_lease(self, key: str, lease: ComputationLease) -> None:
        """Set lease for key with LRU eviction."""
        with self._lock:
            # Periodic cleanup
            self._maybe_cleanup()

            # Enforce size limit with LRU eviction
            if len(self._leases) >= MAX_LEASES:
                # Evict oldest entry
                self._leases.popitem(last=False)
            self._leases[key] = lease

    def remove_lease(self, key: str) -> None:
        """Remove lease for key."""
        with self._lock:
            self._leases.pop(key, None)

    def cleanup_expired(self) -> int:
        """Clean up expired leases. Returns count removed."""
        with self._lock:
            execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")  # Time reference for expiration check
            expired_items = [
                (k, lease) for k, lease in self._leases.items()
                if lease.is_expired() and not lease.has_waiters()
            ]
            for key, _ in expired_items:
                self._leases.pop(key, None)
            return len(expired_items)


class StampedeProtection:
    """Cache stampede protection for LEE.

    Wraps cache operations with request coalescing to prevent
    thundering herd on Home Assistant API.

    Example:
        >>> from lee.lee_cache.lee_stampede_protection import StampedeProtection
        >>> from lee.gateway import execute_operation, GatewayInterface
        >>>
        >>> # Get protected instance
        >>> protection = StampedeProtection()
        >>>
        >>> # Get with factory - protected against stampede
        >>> def fetch_entity_state():
        ...     return execute_operation(
        ...         GatewayInterface.HA_DEVICES, 'get_state',
        ...         entity_id='light.bubs_bedroom_inside_light_switch_1'
        ...     )
        >>>
        >>> state = protection.get_or_compute(
        ...     'entity:light.bubs_bedroom_inside_light_switch_1',
        ...     factory=fetch_entity_state,
        ... )

    """

    def __init__(
        self,
        config: Optional[StampedeProtectionConfig] = None,
        correlation_id: str = None,
    ):
        """Initialize stampede protection.

            config: Configuration for stampede protection behavior
            correlation_id: Optional correlation ID for tracing

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("stampede")

        self._config = config or StampedeProtectionConfig()
        self._registry = InMemoryLeaseRegistry()

        # Statistics
        self._stats_lock = threading.RLock()
        self._stats = {
            "coalesced_requests": 0,
            "duplicate_computations": 0,
            "lease_timeouts": 0,
            "failed_computations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l2_stampede_prevented": 0,
            "l2_lock_wait_count": 0,
        }

        # SUGA-ISP compliance - log initialization
        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="StampedeProtection initialized",
                             corr_id=correlation_id,
                             scope="STAMPEDE",
                             config=f"coalescing={self._config.enable_coalescing}")
        except (ImportError, AttributeError, RuntimeError, KeyError, TypeError) as e:
            # Gateway operations may fail during initialization or if gateway unavailable
            ...
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed in unknown: {e}",
                                 extra_context=str(e))
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                # Logging failed - acceptable during initialization
                ...
            # Don't re-raise ImportError - gateway is optional
            if isinstance(e, ImportError):
                # Gateway not available - acceptable
                pass
            else:
                raise CacheError(f"Cache operation failed in unknown: {e}") from e

    def _get_lock_key(self, key: str) -> str:
        """Get lock key for cache-based locking."""
        return f"{key}{self._config.lock_key_suffix}"

    def _try_get_from_l2(
        self,
        key: str,
        correlation_id: str = None,
    ) -> Optional[Any]:
        """Try to get value from L2 cache with stampede protection.

        Called when L1 cache miss occurs and L2 awareness is enabled.
        Tracks L2 hits/misses for monitoring.

            key: Cache key
            correlation_id: Optional correlation ID

            Cached value from L2, or None if not found/expired

        """
        if not self._config.enable_l2_aware:
            return None

        l2_cache = _get_l2_cache_instance()
        if l2_cache is None:
            return None

        try:
            # Get from L2 cache
            result = l2_cache.get(key, correlation_id=correlation_id)
            if result is not None:
                # L2 hit - populate L1 cache for faster access next time
                execute_operation(
                    GatewayInterface.CACHE, "set",
                    key=key,
                    value=result,
                    ttl=300,  # Default L1 TTL for L2-promoted values
                    source_module="stampede_protection_l2_promote",
                    corr_id=correlation_id,
                )
                # Track L2 hit metric
                with self._stats_lock:
                    self._stats["l2_hits"] += 1
                return result
            else:
                # Track L2 miss metric
                with self._stats_lock:
                    self._stats["l2_misses"] += 1
        except (ImportError, AttributeError, RuntimeError, OSError):
            # L2 cache failed - fall back to computation
            with self._stats_lock:
                self._stats["l2_misses"] += 1

        return None

    def _store_in_both_caches(
        self,
        key: str,
        value: Any,
        ttl: int,
        correlation_id: str = None,
    ) -> None:
        """Store value in both L1 and L2 caches.

            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            correlation_id: Optional correlation ID

        """
        # Always store in L1
        execute_operation(
            GatewayInterface.CACHE, "set",
            key=key,
            value=value,
            ttl=ttl,
            source_module="stampede_protection",
            corr_id=correlation_id,
        )

        # Store in L2 if enabled
        if self._config.enable_l2_aware:
            l2_cache = _get_l2_cache_instance()
            if l2_cache is not None:
                try:
                    l2_cache.set(key, value, ttl=ttl, correlation_id=correlation_id)
                except (ImportError, AttributeError, RuntimeError, OSError):
                    # L2 storage failed - continue with L1 only
                    pass

    def _try_acquire_lock(
        self,
        key: str,
        correlation_id: str = None,
    ) -> bool:
        """Try to acquire computation lock via cache.
        Uses cache 'add' semantics (set if not exists) for distributed locking.

            key: Cache key
            correlation_id: Optional correlation ID

            True if lock acquired, False otherwise

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("stampede")

        lock_key = self._get_lock_key(key)
        timestamp = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")
        execution_id = f"{threading.get_ident()}_{timestamp}"

        try:
            # L2-aware lock coordination: Check L2 cache first if enabled
            if self._config.l2_lock_coordination:
                l2_cache = _get_l2_cache_instance()
                if l2_cache is not None:
                    try:
                        # Check if lock exists in L2 cache
                        l2_lock = l2_cache.get(lock_key, correlation_id=correlation_id)
                        if l2_lock is not None:
                            # Lock exists in L2 - another instance holds it
                            with self._stats_lock:
                                self._stats["l2_lock_wait_count"] += 1
                            return False
                    except (ImportError, AttributeError, RuntimeError, OSError):
                        # L2 check failed - continue with L1 check
                        pass

            # Try to set lock key in L1 cache (only succeeds if not exists)
            try:
                # Check if lock exists first
                existing = execute_operation(
                    GatewayInterface.CACHE, "exists",
                    key=lock_key,
                    corr_id=correlation_id,
                )

                if existing:
                    return False

                # Try to acquire lock by setting it
                execute_operation(
                    GatewayInterface.CACHE, "set",
                    key=lock_key,
                    value=execution_id,
                    ttl=int(self._config.lease_timeout_seconds),
                    source_module="stampede_protection",
                    corr_id=correlation_id,
                )

                # Also store in L2 if coordination is enabled
                if self._config.l2_lock_coordination:
                    l2_cache = _get_l2_cache_instance()
                    if l2_cache is not None:
                        try:
                            l2_cache.set(
                                lock_key,
                                execution_id,
                                ttl=int(self._config.lease_timeout_seconds),
                                correlation_id=correlation_id,
                            )
                        except (ImportError, AttributeError, RuntimeError, OSError):
                            # L2 storage failed - continue with L1 lock only
                            pass

                return True

            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError, OSError, threading.ThreadError) as e:
                # Cache operations may fail for various reasons
                pass
                handle_cache_exception(
                    exception=e,
                    operation_name="stampede_protection",
                    context="Cache operation failed",
                    gateway_interface=GatewayInterface,
                    execute_op=execute_operation
                )
                raise

        except (ImportError, AttributeError, RuntimeError, KeyError, TypeError, OSError, threading.ThreadError) as e:
            # Gateway operations may fail during initialization or if gateway unavailable
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed in unknown: {e}",
                                 extra_context=str(e))
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                # Logging failed - acceptable
                pass
            # Don't re-raise ImportError - gateway is optional
            if isinstance(e, ImportError):
                # Gateway not available - acceptable
                pass
            else:
                raise CacheError(f"Cache operation failed in unknown: {e}") from e

        # Fallback to in-memory lock
        self._registry.get_lease(key)

    def _release_lock(
        self,
        key: str,
        correlation_id: str = None,
    ) -> None:
        """Release computation lock from both L1 and L2 caches.

            key: Cache key
            correlation_id: Optional correlation ID

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("stampede")

        lock_key = self._get_lock_key(key)

        # Release L1 lock
        try:
            execute_operation(
                GatewayInterface.CACHE, "delete",
                key=lock_key,
                corr_id=correlation_id,
            )
        except (ImportError, RuntimeError):
            # Optional dependency - continue if unavailable
            pass

        # Release L2 lock if coordination is enabled
        if self._config.l2_lock_coordination:
            l2_cache = _get_l2_cache_instance()
            if l2_cache is not None:
                try:
                    l2_cache.delete(lock_key, correlation_id=correlation_id)
                except (ImportError, AttributeError, RuntimeError, OSError):
                    # L2 deletion failed - continue with cleanup
                    pass

        # Clean up in-memory registry
        self._registry.remove_lease(key)

    def _check_l2_stampede_in_progress(
        self,
        key: str,
        correlation_id: str = None,
    ) -> bool:
        """Check if an L2 cache stampede is currently in progress.

        When L2 lock coordination is enabled, checks if another Lambda instance
        is currently computing the value by looking for the lock in L2 cache.

            key: Cache key
            correlation_id: Optional correlation ID

            True if stampede protection is active (another instance computing)

        """
        if not self._config.l2_lock_coordination:
            return False

        l2_cache = _get_l2_cache_instance()
        if l2_cache is None:
            return False

        try:
            lock_key = self._get_lock_key(key)
            l2_lock = l2_cache.get(lock_key, correlation_id=correlation_id)
            if l2_lock is not None:
                # Another instance holds the lock - stampede in progress
                with self._stats_lock:
                    self._stats["l2_stampede_prevented"] += 1
                return True
        except (ImportError, AttributeError, RuntimeError, OSError):
            # L2 check failed - assume no stampede
            pass

        return False

    def _wait_for_result(
        self,
        key: str,
        correlation_id: str = None,
    ) -> Optional[Any]:
        """Wait for computation result from another thread.

            key: Cache key
            correlation_id: Optional correlation ID

            Computed value if available, None if timeout/failed

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("stampede")

        try:
            for _attempt in range(self._config.max_wait_attempts):
                # Check L1 cache first
                result = execute_operation(
                    GatewayInterface.CACHE, "get",
                    key=key,
                    corr_id=correlation_id,
                )

                # Check if this is the _CACHE_MISS sentinel
                if result is not _CACHE_MISS:
                    # Success - result is available
                    with self._stats_lock:
                        self._stats["coalesced_requests"] += 1
                    return result

                # If L1 miss, check L2 cache if enabled
                if self._config.enable_l2_aware:
                    l2_result = self._try_get_from_l2(key, correlation_id=correlation_id)
                    if l2_result is not None:
                        # L2 has the result
                        with self._stats_lock:
                            self._stats["coalesced_requests"] += 1
                        return l2_result

                # Check if lock expired (computation failed)
                lock_key = self._get_lock_key(key)

                # Check L1 lock
                lock_exists = execute_operation(
                    GatewayInterface.CACHE, "exists",
                    key=lock_key,
                    corr_id=correlation_id,
                )

                # Also check L2 lock if coordination is enabled
                l2_lock_exists = False
                if not lock_exists and self._config.l2_lock_coordination:
                    l2_lock_exists = self._check_l2_stampede_in_progress(key, correlation_id)

                if not lock_exists and not l2_lock_exists:
                    # Both locks expired - computation failed
                    with self._stats_lock:
                        self._stats["lease_timeouts"] += 1
                    return None

                # Wait before retry
                # NOTE: time.sleep() is acceptable here for request coalescing wait loop
                # This is a critical wait mechanism for stampede protection and using
                # the gateway would add unnecessary overhead to tight retry loops.
                time.sleep(self._config.wait_interval_seconds)

            # Max attempts reached
            with self._stats_lock:
                self._stats["lease_timeouts"] += 1
            return None

        except (ImportError, RuntimeError):
            return None

    def get_or_compute(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = 300,
        correlation_id: str = None,
    ) -> Any:
        """Get value with stampede protection.

        If cache miss, uses request coalescing to ensure only one
        thread computes the value while others wait.

            key: Cache key
            factory: Factory function to compute value on miss
            ttl: Time-to-live for cached value in seconds
            correlation_id: Optional correlation ID for tracing

            Cached or computed value

        Raises:
            Exception: If factory function raises an exception

            >>> def fetch_device_state():
            ...     # Expensive Home Assistant API call
            ...     return ha_api.get_state('light.bubs_bedroom_inside_light_switch_1')
            >>>
            >>> state = protection.get_or_compute(
            ...     'device:light.bubs_bedroom_inside_light_switch_1',
            ...     factory=fetch_device_state,
            ...     ttl=60
            ... )

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("stampede")

        try:

            # Try to get from cache first
            cached_value = execute_operation(
                GatewayInterface.CACHE, "get",
                key=key,
                corr_id=correlation_id,
            )

            if cached_value is not _CACHE_MISS:
                # Cache hit
                with self._stats_lock:
                    self._stats["cache_hits"] += 1
                return cached_value

            # Cache miss - try L2 if enabled
            l2_value = self._try_get_from_l2(key, correlation_id=correlation_id)
            if l2_value is not None:
                # L2 cache hit
                with self._stats_lock:
                    self._stats["cache_hits"] += 1
                return l2_value

            # Complete cache miss (L1 and L2)
            with self._stats_lock:
                self._stats["cache_misses"] += 1

            # Try to acquire computation lock
            if not self._config.enable_coalescing:
                # Coalescing disabled - compute directly
                result = factory()
                self._store_in_both_caches(key, result, ttl, correlation_id=correlation_id)
                return result

            # Try to acquire lock
            has_lock = self._try_acquire_lock(key, correlation_id=correlation_id)

            if has_lock:
                # We acquired the lock - compute and cache
                try:
                    # Create lease entry
                    current_time = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")
                    lease = ComputationLease(
                        key=key,
                        created_at=current_time,
                        expires_at=current_time + self._config.lease_timeout_seconds,
                    )
                    self._registry.set_lease(key, lease)

                    # Compute the result
                    result = factory()

                    # Cache the result in both L1 and L2
                    self._store_in_both_caches(key, result, ttl, correlation_id=correlation_id)

                    # Record metrics
                    if self._config.enable_metrics:
                        try:
                            execute_operation(
                                GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="stampede.computations_performed",
                                corr_id=correlation_id,
                            )
                        except (ImportError, Exception):
                            # Optional dependency - continue if unavailable
                            ...

                    return result

                except (ImportError, AttributeError, RuntimeError, OSError, ValueError, TypeError):
                    # Computation failed - release lock
                    ...
                    with self._stats_lock:
                        self._stats["failed_computations"] += 1
                    raise

                finally:
                    # Always release lock
                    self._release_lock(key, correlation_id=correlation_id)

            else:
                # Another thread is computing - wait for result
                result = self._wait_for_result(key, correlation_id=correlation_id)

                if result is not None:
                    return result

                # Wait failed or lock expired - compute anyway (fallback)
                if self._config.enable_fallback:
                    with self._stats_lock:
                        self._stats["duplicate_computations"] += 1

                    result = factory()
                    self._store_in_both_caches(key, result, ttl, correlation_id=correlation_id)
                    return result
                raise TimeoutError(
                    f"Stampede protection timeout for key: {key}. "
                    f"Failed to wait for computation result.",
                )

        except (ImportError, AttributeError, RuntimeError, OSError, ValueError, TypeError) as e:
            # Log error
            try:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Stampede protection error: {e}",
                    scope="STAMPEDE",
                    corr_id=correlation_id,
                    key=key,
                    error_type=type(e).__name__,
                )
            except (ImportError, AttributeError, RuntimeError, KeyError, TypeError):
                # Logging failed - acceptable
                pass
            raise

    def get_stats(self) -> dict[str, int]:
        """Get stampede protection statistics.

            Dictionary of statistics counters

        """
        with self._stats_lock:
            return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._stats_lock:
            for key in self._stats:
                self._stats[key] = 0


# Singleton instance for convenience
_stampede_protection_instance: Optional[StampedeProtection] = None
_instance_lock = threading.RLock()


def get_stampede_protection(
    config: Optional[StampedeProtectionConfig] = None,
    correlation_id: str = None,
) -> StampedeProtection:
    """Get or create singleton stampede protection instance.

        config: Optional configuration (only used on first call)
        correlation_id: Optional correlation ID

        StampedeProtection singleton instance

    """
    # pylint: disable=global-statement
    global _stampede_protection_instance

    with _instance_lock:
        if _stampede_protection_instance is None:
            _stampede_protection_instance = StampedeProtection(
                config=config,
                correlation_id=correlation_id,
            )

        return _stampede_protection_instance


def stampede_protected(
    ttl: int = 300,
    key_func: Optional[Callable] = None,
    correlation_id_param: str = "corr_id",
):
    """Decorator for stampede-protected memoization.

    Prevents cache stampede when decorating expensive functions.

        ttl: Time-to-live for cached results in seconds
        key_func: Optional function to generate cache key from arguments.
                  If None, uses function name and arguments.
        correlation_id_param: Parameter name for correlation ID (if present)

    Example:
        >>> from lee.lee_cache.lee_stampede_protection import stampede_protected
        >>>
        >>> @stampede_protected(ttl=60)
        >>> def get_device_state(entity_id: str):
        ...     # Expensive HA API call
        ...     return ha_api.get_state(entity_id)
        >>>
        >>> # First call computes, subsequent calls use cache
        >>> state2 = get_device_state('light.bubs_bedroom_inside_light_switch_1')  # Cache hit
        >>>
        >>> # With custom key function
        >>> @stampede_protected(
        ...     ttl=300,
        ...     key_func=lambda entity_id: f"device:{entity_id}"
        ... )
        ...     return ha_api.get_entity(entity_id)

    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract correlation ID if provided
            corr_id = kwargs.get(correlation_id_param)
            if corr_id is None:
                corr_id = generate_correlation_id("stampede")

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Generate key from function name and arguments
                args_str = ",".join(str(arg) for arg in args)
                kwargs_str = ",".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if k != correlation_id_param)
                cache_key = f"memoize:{func.__name__}:{args_str}:{kwargs_str}"

            # Get stampede protection instance
            protection = get_stampede_protection(correlation_id=corr_id)

            # Define factory function
            def factory():
                return func(*args, **kwargs)

            # Get or compute with stampede protection
            return protection.get_or_compute(
                key=cache_key,
                factory=factory,
                ttl=ttl,
                correlation_id=corr_id,
            )

        return wrapper
    return decorator


__all__ = [
    "ComputationLease",
    "ComputationStatus",
    "InMemoryLeaseRegistry",
    "StampedeProtection",
    "StampedeProtectionConfig",
    "get_stampede_protection",
    "stampede_protected",
]

# EOF
