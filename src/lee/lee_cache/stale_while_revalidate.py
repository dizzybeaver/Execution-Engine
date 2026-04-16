"""lee_cache/stale_while_revalidate.py
Version: 2025-03-02_1
Purpose: Stale-While-Revalidate cache extension for Alexa SLA compliance
License: Apache 2.0

Implements stale-while-revalidate caching strategy to serve stale data
during cache refresh, preventing latency spikes when cache entries expire.

The Problem (Alexa SLA):
    Alexa Smart Home API requires <200ms response time for control operations.
    If cache expires mid-request, fetching fresh data from Home Assistant
    can take 500-2000ms, causing SLA breach.

The Solution:
    1. Grace Period: Serve stale data if entry is recently expired (< grace period)
    2. Async Refresh: Trigger background refresh of stale data
    3. Zero User Latency: User gets immediate response from stale cache
    4. Fresh Data Next Request: Next caller gets fresh data

Use Cases:
    - Device state queries (60s TTL, 30s grace)
    - Entity discovery (300s TTL, 60s grace)
    - Configuration data (600s TTL, 120s grace)

Integration with LEE SUGA-ISP:
    - Extends LUGSIntegratedCache with get_with_grace_period()
    - Uses execute_operation for all gateway interactions
    - Metrics for stale serves, refresh triggers
"""

import threading  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from enum import Enum, auto, StrEnum  # noqa: E402
from typing import Any, Optional


from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_cache.cache_enums import CacheError


class StaleDataPolicy(StrEnum):
    """Policy for serving stale data."""

    SERVE_STALE = "serve_stale"  # Serve stale data, trigger async refresh
    FORCE_REFRESH = "force_refresh"  # Always fetch fresh data
    SERVE_STALE_NO_REFRESH = "serve_stale_no_refresh"  # Serve stale, no refresh


@dataclass
class StaleWhileRevalidateConfig:
    """Configuration for stale-while-revalidate behavior."""

    # Grace period configuration
    default_grace_period_seconds: int = 30  # Default grace period
    enable_grace_period: bool = True

    # Async refresh configuration
    enable_async_refresh: bool = True
    max_pending_refreshes: int = 100  # Max concurrent async refreshes

    # Fallback behavior
    serve_expired_beyond_grace: bool = False  # Serve even if beyond grace period

    # Metrics
    enable_metrics: bool = True

    # pylint: disable=too-many-instance-attributes
    # 8 instance attributes is acceptable for this configuration dataclass


class RefreshStatus(Enum):
    """Status of async refresh operation."""

    PENDING = auto()  # Refresh scheduled/pending
    IN_PROGRESS = auto()  # Refresh currently executing
    COMPLETE = auto()  # Refresh complete
    FAILED = auto()  # Refresh failed


@dataclass
class PendingRefresh:
    """Track pending async refresh for a key."""
    key: str
    factory: Callable[[], Any]
    ttl: int
    status: RefreshStatus = RefreshStatus.PENDING
    created_at: float = 0.0  # Set by factory
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[Exception] = None

    def is_expired(self, timeout_seconds: float = 60) -> bool:
        """Check if refresh has timed out."""
        current_time = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")
        if self.started_at is None:
            # Not started yet - check creation time
            return (current_time - self.created_at) > timeout_seconds
        # Started - check start time
        return (current_time - self.started_at) > timeout_seconds

    def duration(self) -> Optional[float]:
        """Get refresh duration in seconds."""
        if self.completed_at is not None and self.started_at is not None:
            return self.completed_at - self.started_at
        return None


class AsyncRefreshRegistry:
    """Registry for pending async refreshes.

    For Lambda single-threaded execution, this tracks refreshes that
    need to be executed. In multi-threaded environments, would use
    a thread pool executor.
    """

    def __init__(self, max_pending: int = 100):
        self._refreshes: dict[str, PendingRefresh] = {}
        self._lock = threading.RLock()
        self._max_pending = max_pending

    def add_refresh(self, refresh: PendingRefresh) -> bool:
        """Add a pending refresh.

            refresh: Pending refresh to add

            True if added, False if at capacity

        """
        with self._lock:
            if len(self._refreshes) >= self._max_pending:
                return False

            self._refreshes[refresh.key] = refresh
            return True

    def get_refresh(self, key: str) -> Optional[PendingRefresh]:
        """Get pending refresh for key."""
        with self._lock:
            return self._refreshes.get(key)

    def remove_refresh(self, key: str) -> None:
        """Remove refresh for key."""
        with self._lock:
            self._refreshes.pop(key, None)

    def cleanup_expired(self, timeout_seconds: float = 60) -> int:
        """Clean up expired/failed refreshes. Returns count removed."""
        with self._lock:
            execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")  # Time reference for expiration check
            expired_items = [
                (key, refresh) for key, refresh in self._refreshes.items()
                if refresh.status in (RefreshStatus.COMPLETE, RefreshStatus.FAILED) or refresh.is_expired(timeout_seconds)
            ]

            for key, _ in expired_items:
                self._refreshes.pop(key, None)

            return len(expired_items)

    def get_all_pending(self) -> list[PendingRefresh]:
        """Get all pending refreshes."""
        with self._lock:
            return [r for r in self._refreshes.values()
                    if r.status == RefreshStatus.PENDING]


class StaleWhileRevalidate:
    """Stale-While-Revalidate cache extension for LEE.

    Extends cache get() operation with grace period logic:
    - If entry exists but is expired within grace period → serve stale, trigger refresh
    - If entry exists and is fresh → serve normally
    - If entry doesn't exist → return cache miss

    Example:
        >>> from lee.lee_cache.stale_while_revalidate import StaleWhileRevalidate
        >>> from lee.gateway import execute_operation, GatewayInterface
        >>>
        >>> swr = StaleWhileRevalidate()
        >>>
        >>> # Get with grace period
        >>> def fetch_state():
        ...     return execute_operation(
        ...         GatewayInterface.HA_DEVICES, 'get_state',
        ...         entity_id='light.bubs_bedroom_inside_light_switch_1'
        ...     )
        >>>
        >>> result = swr.get_with_grace_period(
        ...     key='entity:light.bubs_bedroom_inside_light_switch_1',
        ...     factory=fetch_state,
        ...     ttl=60,
        ...     grace_period=30
        ... )

    """

    def __init__(
        self,
        config: Optional[StaleWhileRevalidateConfig] = None,
        correlation_id: str = None,
    ):
        """Initialize stale-while-revalidate extension.

            config: Configuration for SWR behavior
            correlation_id: Optional correlation ID for tracing

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("swr")

        self._config = config or StaleWhileRevalidateConfig()
        self._refresh_registry = AsyncRefreshRegistry(
            max_pending=self._config.max_pending_refreshes,
        )

        # Statistics
        self._stats_lock = threading.RLock()
        self._stats = {
            "stale_serves": 0,
            "fresh_serves": 0,
            "cache_misses": 0,
            "async_refreshes_triggered": 0,
            "async_refreshes_completed": 0,
            "async_refreshes_failed": 0,
            "grace_period_exceeded": 0,
        }

        # SUGA-ISP compliance - log initialization
        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="StaleWhileRevalidate initialized",
                             corr_id=correlation_id,
                             scope="SWR",
                             config=f"grace_period={self._config.default_grace_period_seconds}s")
        except (ImportError, ValueError, TypeError, AttributeError, KeyError) as e:
            # Expected dependency errors - continue if unavailable
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed: {e}",
                                 extra_context=str(e))
            except (ValueError, TypeError, AttributeError, KeyError):
                # Logging failures - silent fail
                pass
        except RuntimeError as e:
            # Unexpected errors
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed unexpectedly: {e}",
                                 extra_context=str(e) + f" (error_type: {type(e).__name__})")
            except (ValueError, TypeError, AttributeError, KeyError):
                # Logging failures - silent fail
                pass
            if isinstance(e, ImportError):
                # Gateway not available - acceptable
                pass
            else:
                raise CacheError(f"Cache operation failed in unknown: {e}") from e

    def _calculate_age(self, entry, current_time: float) -> float:
        """Calculate entry age in seconds."""
        return current_time - entry.timestamp

    def _is_expired(self, entry, current_time: float) -> bool:
        """Check if entry is expired."""
        age = self._calculate_age(entry, current_time)
        return age > entry.ttl

    def _is_within_grace_period(
        self,
        entry,
        current_time: float,
        grace_period: int,
    ) -> bool:
        """Check if expired entry is within grace period."""
        age = self._calculate_age(entry, current_time)
        time_since_expiration = age - entry.ttl
        return time_since_expiration <= grace_period

    def _trigger_async_refresh(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int,
        correlation_id: str = None,
    ) -> None:
        """Trigger async refresh of stale cache entry.

        In Lambda's single-threaded model, this schedules the refresh
        for later execution. In multi-threaded environments, would
        use a thread pool executor.
            key: Cache key
            factory: Factory function to compute fresh value
            ttl: TTL for fresh value
            correlation_id: Optional correlation ID

        """
        # pylint: disable=too-many-branches
        # 14 branches is acceptable for this complex refresh coordination logic
        if correlation_id is None:
            correlation_id = generate_correlation_id("swr")

        # Create pending refresh
        refresh = PendingRefresh(
            key=key,
            factory=factory,
            ttl=ttl,
            status=RefreshStatus.PENDING,
        )

        # Add to registry
        if not self._refresh_registry.add_refresh(refresh):
            # Registry full - skip refresh
            try:
                execute_operation(
                    GatewayInterface.LOGGING, "log_warning",
                    message="Async refresh registry full, skipping refresh",
                    scope="SWR",
                    corr_id=correlation_id,
                    key=key,
                )
            except (ImportError, ValueError, TypeError, AttributeError, KeyError) as e:
                # Expected logging errors
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     message=f"Cache operation failed: {e}",
                                     extra_context=str(e))
                except (ValueError, TypeError, AttributeError, KeyError):
                    # Logging failures - silent fail
                    pass
            except RuntimeError as e:
                # Unexpected logging errors
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     message=f"Cache operation failed unexpectedly: {e}",
                                     extra_context=str(e) + f" (error_type: {type(e).__name__})")
                except (ValueError, TypeError, AttributeError, KeyError):
                    # Logging failures - silent fail
                    pass
                if isinstance(e, ImportError):
                    # Gateway not available - acceptable
                    pass
                else:
                    raise CacheError(f"Cache operation failed in unknown: {e}") from e
            return

        # Update stats
        with self._stats_lock:
            self._stats["async_refreshes_triggered"] += 1

        # Log refresh trigger
        try:
            execute_operation(
                GatewayInterface.LOGGING, "log_info",
                message="Async refresh triggered",
                scope="SWR",
                corr_id=correlation_id,
                key=key,
                ttl=ttl,
            )
        except (ImportError, ValueError, TypeError, AttributeError, KeyError) as e:
            # Expected logging errors
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed: {e}",
                                 extra_context=str(e))
            except (ValueError, TypeError, AttributeError, KeyError):
                # Logging failures - silent fail
                pass
        except RuntimeError as e:
            # Unexpected logging errors
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message=f"Cache operation failed unexpectedly: {e}",
                                 extra_context=str(e) + f" (error_type: {type(e).__name__})")
            except (ValueError, TypeError, AttributeError, KeyError):
                # Logging failures - silent fail
                pass
            if isinstance(e, ImportError):
                # Gateway not available - acceptable
                pass
            else:
                raise CacheError(f"Cache operation failed in unknown: {e}") from e

    def get_with_grace_period(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = 300,
        grace_period: Optional[int] = None,
        correlation_id: str = None,
    ) -> tuple[Any, str]:
        """Get value with stale-while-revalidate grace period.

            key: Cache key
            factory: Factory function to compute value on miss
            ttl: Time-to-live for cached value in seconds
            grace_period: Grace period in seconds (uses default if None)
            correlation_id: Optional correlation ID for tracing

            Tuple of (value, status) where status is:
            - 'fresh': Value was fresh from cache
            - 'stale': Value was stale (within grace period), async refresh triggered
            - 'computed': Value was computed (cache miss)

        Raises:
            Exception: If factory function raises an exception

        Example:
            >>> value, status = swr.get_with_grace_period(
            ...     key='entity:light.bubs_bedroom_inside_light_switch_1',
            ...     factory=lambda: ha_api.get_state('light.bubs_bedroom_inside_light_switch_1'),
            ...     ttl=60,
            ...     grace_period=30
            ... )
            >>> if status == 'stale':
            ...     # Value is stale but still served
            ...     # Async refresh triggered for next request
            ...     pass

        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # 6 arguments is acceptable for this gateway operation
        # pylint: disable=too-many-statements
        # 61 statements is acceptable for this complex cache coordination logic
        # pylint: disable=too-many-branches,too-many-nested-blocks
        # Complex nested logic for cache state handling is unavoidable here
        if correlation_id is None:
            correlation_id = generate_correlation_id("swr")

        if grace_period is None:
            grace_period = self._config.default_grace_period_seconds

        try:
            # pylint: disable=import-outside-toplevel
            from lee.lee_cache.cache_enums import _CACHE_MISS

            # Try to get from cache
            cached_value = execute_operation(
                GatewayInterface.CACHE, "get",
                key=key,
                corr_id=correlation_id,
            )

            # Check if we got a valid cache entry (not miss)
            if cached_value is not _CACHE_MISS:
                # Check if entry has metadata to determine freshness
                metadata = execute_operation(
                    GatewayInterface.CACHE, "mget_metadata",
                    keys=[key],
                    corr_id=correlation_id,
                )

                if metadata is not None:
                    execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")  # Time reference for metadata validation

                    if not metadata.get("is_expired", True):
                        # Fresh value - serve normally
                        with self._stats_lock:
                            self._stats["fresh_serves"] += 1
                        return cached_value, "fresh"

                    # Entry is expired - check grace period
                    if self._config.enable_grace_period:
                        ttl_remaining = metadata.get("ttl_remaining", -grace_period - 1)
                        time_since_expiration = -ttl_remaining if ttl_remaining < 0 else 0

                        if time_since_expiration <= grace_period:
                            # Within grace period - serve stale, trigger refresh
                            with self._stats_lock:
                                self._stats["stale_serves"] += 1

                            # Trigger async refresh
                            if self._config.enable_async_refresh:
                                self._trigger_async_refresh(
                                    key=key,
                                    factory=factory,
                                    ttl=ttl,
                                    correlation_id=correlation_id,
                                )

                            # Record metrics
                            if self._config.enable_metrics:
                                try:
                                    execute_operation(
                                        GatewayInterface.OBSERVABILITY, "increment",
                                        metric_name="swr.stale_serves",
                                        corr_id=correlation_id,
                                    )
                                except (ImportError, ValueError, TypeError, AttributeError, KeyError):
                                    # Optional dependency - continue if unavailable
                                    ...

                            return cached_value, "stale"

                        # Beyond grace period
                        with self._stats_lock:
                            self._stats["grace_period_exceeded"] += 1

            # Cache miss or beyond grace period without stale serve
            with self._stats_lock:
                self._stats["cache_misses"] += 1

            # Compute fresh value
            result = factory()

            # Store in cache
            execute_operation(
                GatewayInterface.CACHE, "set",
                key=key,
                value=result,
                ttl=ttl,
                source_module="stale_while_revalidate",
                corr_id=correlation_id,
            )

            return result, "computed"

        except (ValueError, TypeError, AttributeError, KeyError, ConnectionError, TimeoutError) as e:
            # Expected SWR errors
            try:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Stale-while-revalidate error: {e}",
                    scope="SWR",
                    corr_id=correlation_id,
                    key=key,
                )
            except (ValueError, TypeError, AttributeError):
                # Logging failures - silent fail
                pass
            raise
        except RuntimeError as e:
            # Unexpected SWR errors
            try:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Stale-while-revalidate unexpected error: {e}",
                    scope="SWR",
                    corr_id=correlation_id,
                    key=key,
                    error_type=type(e).__name__,
                )
            except (ImportError, ValueError, TypeError, AttributeError, KeyError) as inner_e:
                # Expected errors
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     message=f"Cache operation failed: {inner_e}",
                                     extra_context=str(inner_e))
                except (ValueError, TypeError, AttributeError):
                    # Logging failures - silent fail
                    pass
            except RuntimeError as inner_e:
                # Unexpected errors
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     message=f"Cache operation failed unexpectedly: {inner_e}",
                                     extra_context=str(inner_e) + f" (error_type: {type(inner_e).__name__})")
                except (ValueError, TypeError, AttributeError):
                    # Logging failures - silent fail
                    pass
                raise
                # Don't re-raise ImportError - gateway is optional
                if isinstance(inner_e, ImportError):
                    # Gateway not available - acceptable
                    pass
                else:
                    raise CacheError(f"Cache operation failed in unknown: {inner_e}") from inner_e
            raise

    def process_pending_refreshes(self, correlation_id: str = None) -> int:
        """Process pending async refreshes.

        In Lambda, call this at the end of request handling to
        process any pending refreshes triggered during the request.


            Number of refreshes processed

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("swr")

        pending = self._refresh_registry.get_all_pending()
        processed = 0

        for refresh in pending:
            try:
                # Mark as in progress
                refresh.status = RefreshStatus.IN_PROGRESS
                refresh.started_at = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")

                # Execute factory
                result = refresh.factory()

                # Store in cache
                execute_operation(
                    GatewayInterface.CACHE, "set",
                    key=refresh.key,
                    value=result,
                    ttl=refresh.ttl,
                    source_module="stale_while_revalidate",
                    corr_id=correlation_id,
                )

                # Mark complete
                refresh.status = RefreshStatus.COMPLETE
                refresh.completed_at = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")

                with self._stats_lock:
                    self._stats["async_refreshes_completed"] += 1

                processed += 1

            except RuntimeError as e:
                # Mark failed
                pass
                refresh.status = RefreshStatus.FAILED
                refresh.error = e
                refresh.completed_at = execute_operation(GatewayInterface.UTILITY, "get_timestamp_numeric")

                with self._stats_lock:
                    self._stats["async_refreshes_failed"] += 1

        # Cleanup
        self._refresh_registry.cleanup_expired()

        return processed

    def get_stats(self) -> dict[str, int]:
        """Get stale-while-revalidate statistics.

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
_swr_instance: Optional[StaleWhileRevalidate] = None
_instance_lock = threading.RLock()


def get_stale_while_revalidate(
    _config: Optional[StaleWhileRevalidateConfig] = None,
    correlation_id: str = None,
) -> StaleWhileRevalidate:
    """Get or create singleton stale-while-revalidate instance.

        config: Optional configuration (only used on first call)
        correlation_id: Optional correlation ID

        StaleWhileRevalidate singleton instance

    """
    # pylint: disable=global-statement
    global _swr_instance

    with _instance_lock:
        if _swr_instance is None:
            _swr_instance = StaleWhileRevalidate(
                config=_config,
            )

        return _swr_instance


__all__ = [
    "AsyncRefreshRegistry",
    "PendingRefresh",
    "RefreshStatus",
    "StaleDataPolicy",
    "StaleWhileRevalidate",
    "StaleWhileRevalidateConfig",
    "get_stale_while_revalidate",
]

# EOF
