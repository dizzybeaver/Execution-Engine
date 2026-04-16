"""Cache warming strategies for Alexa Smart Home data.

Implements three warming strategies to prevent cold-start penalties:
1. Static Warming - Pre-load known static data
2. Predictive Warming - Analyze access patterns to predict next requests
3. Trace-Based Warming - Replay recent access patterns

All operations use Python Standard Library only and are thread-safe.
"""

from typing import Optional
import bisect
import threading
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from lee.lee_cache.cache_enums import CacheError

try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    GatewayInterface = None
    execute_operation = None

# pylint: disable=unused-import


class CacheWarmer:
    """Cache warming manager for predictive pre-loading."""

    # Configuration constants
    # pylint: disable=import-outside-toplevel
    from lee.lee_config.variables import (
        CACHE_WARMING_MAX_ACCESS_HISTORY,
        CACHE_WARMING_MAX_TEMPORAL_PATTERNS,
        CACHE_WARMING_MAX_TOP_KEYS,
        CACHE_WARMING_MAX_USER_PATTERNS,
    )

    MAX_ACCESS_HISTORY = CACHE_WARMING_MAX_ACCESS_HISTORY  # Maximum access records
    MAX_TEMPORAL_PATTERNS = CACHE_WARMING_MAX_TEMPORAL_PATTERNS  # Maximum temporal patterns (hour of day)
    MAX_USER_PATTERNS = CACHE_WARMING_MAX_USER_PATTERNS  # Maximum user-specific patterns
    MAX_TOP_KEYS = CACHE_WARMING_MAX_TOP_KEYS  # Top keys to track
    PREDICTION_CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence for prediction
    BATCH_SIZE = 20  # Keys to fetch per batch
    MAX_WORKERS = 4  # Maximum concurrent warming threads

    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        """Initialize cache warmer."""
        self._lock = threading.RLock()
        self._access_history = deque(maxlen=self.MAX_ACCESS_HISTORY)
        self._key_frequency = defaultdict(int)
        self._temporal_patterns = defaultdict(lambda: defaultdict(int))
        self._user_patterns = defaultdict(lambda: defaultdict(int))
        self._top_keys = []
        self._last_warm_time = {}
        self._warming_stats = {
            "static_warms": 0,
            "predictive_warms": 0,
            "trace_based_warms": 0,
            "success_warms": 0,
            "failed_warms": 0,
            "total_warmed_keys": 0,
            "last_warm_time": None,
        }

    def warm_static_data(
        self,
        keys: list[str],
        factory: Callable,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Warm static cache entries.

            keys: List of cache keys to warm
            factory: Function to fetch data for missing keys
            correlation_id: Optional correlation ID for logging

            Number of keys successfully warmed

        """
        warmed_count = 0

        try:
            # Check which keys need warming (not in cache or expired)
            missing_keys = []
            for key in keys:
                cache_result = execute_operation(
                    GatewayInterface.CACHE,
                    "get_with_grace_period",
                    key=key,
                    factory=lambda: None,  # Check without warming
                    ttl=3600,  # 1 hour TTL
                    grace_period=300,  # 5 minute grace
                )

                # If key is missing or stale, add to warming list
                if cache_result[1] == "computed":  # Not in cache
                    missing_keys.append(key)

            if missing_keys:
                # Warm in batches to avoid blocking
                for i in range(0, len(missing_keys), self.BATCH_SIZE):
                    batch = missing_keys[i:i + self.BATCH_SIZE]
                    self._warm_batch(batch, factory, correlation_id)
                    warmed_count += len(batch)

            # Update stats
            with self._lock:
                self._warming_stats["static_warms"] += 1
                self._warming_stats["success_warms"] += warmed_count
                self._warming_stats["total_warmed_keys"] += warmed_count
                self._warming_stats["last_warm_time"] = datetime.now().isoformat()

        except (ValueError, TypeError, AttributeError, KeyError, OSError, ConnectionError, TimeoutError) as e:
            # Expected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Static warming failed: {e!s}",
                    corr_id=correlation_id,
                )
        except RuntimeError as e:
            # Unexpected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Static warming failed unexpectedly: {e!s}",
                    corr_id=correlation_id,
                )

        return warmed_count

    def warm_predictive_data(
        self,
        user_id: str,
        context: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Warm predicted cache entries based on patterns.

            user_id: User ID for pattern analysis
            context: Context information (time, location, etc.)
            correlation_id: Optional correlation ID for logging

            Number of keys successfully warmed

        """
        warmed_count = 0

        try:
            # Get predictions based on patterns
            predicted_keys = self._get_predictions(user_id, context)

            if predicted_keys:
                # Define a factory for prediction-based warming
                def predictive_factory(_key):
                    # For prediction warming, we don't need real data
                    # The actual data will be fetched when requested
                    return None

                # Warm predicted keys
                for key in predicted_keys:
                    cache_result = execute_operation(
                        GatewayInterface.CACHE,
                        "get_with_grace_period",
                        key=key,
                        factory=predictive_factory,
                        ttl=1800,  # 30 minutes TTL for predictions
                        grace_period=300,  # 5 minute grace
                    )

                    if cache_result[1] == "computed":
                        warmed_count += 1

            # Update stats
            with self._lock:
                self._warming_stats["predictive_warms"] += 1
                self._warming_stats["success_warms"] += warmed_count
                self._warming_stats["total_warmed_keys"] += warmed_count
                self._warming_stats["last_warm_time"] = datetime.now().isoformat()

        except (ValueError, TypeError, AttributeError, KeyError, OSError, ConnectionError, TimeoutError) as e:
            # Expected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Predictive warming failed: {e!s}",
                    corr_id=correlation_id,
                )
        except RuntimeError as e:
            # Unexpected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Predictive warming failed unexpectedly: {e!s}",
                    corr_id=correlation_id,
                )

        return warmed_count

    def warm_trace_based(
        self,
        trace_size: int = 100,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Warm cache based on recent access traces.

            trace_size: Number of recent accesses to analyze
            correlation_id: Optional correlation ID for logging

            Number of keys successfully warmed

        """
        warmed_count = 0

        try:
            # Get recent access traces
            with self._lock:
                recent_traces = list(self._access_history)[-trace_size:]

            if not recent_traces:
                return 0

            # Get top accessed keys
            top_keys = self.get_top_keys(trace_size)

            # Define a factory for trace-based warming
            def trace_factory(_key):
                # For trace warming, we don't need real data yet
                return None

            # Warm top keys
            for key in top_keys:
                cache_result = execute_operation(
                    GatewayInterface.CACHE,
                    "get_with_grace_period",
                    key=key,
                    factory=trace_factory,
                    ttl=3600,  # 1 hour TTL for trace-based
                    grace_period=300,  # 5 minute grace
                )

                if cache_result[1] == "computed":
                    warmed_count += 1

            # Update stats
            with self._lock:
                self._warming_stats["trace_based_warms"] += 1
                self._warming_stats["success_warms"] += warmed_count
                self._warming_stats["total_warmed_keys"] += warmed_count
                self._warming_stats["last_warm_time"] = datetime.now().isoformat()

        except (ValueError, TypeError, AttributeError, KeyError, OSError, ConnectionError, TimeoutError) as e:
            # Expected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Trace-based warming failed: {e!s}",
                    corr_id=correlation_id,
                )
        except RuntimeError as e:
            # Unexpected warming errors
            with self._lock:
                self._warming_stats["failed_warms"] += 1
            if correlation_id:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message=f"Trace-based warming failed unexpectedly: {e!s}",
                    corr_id=correlation_id,
                )

        return warmed_count

    def record_access(
        self,
        key: str,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Record cache access for pattern analysis.

            key: Cache key that was accessed
            user_id: Optional user ID
            correlation_id: Optional correlation ID for logging

        """
        try:
            with self._lock:
                # Record access time
                access_time = datetime.now()
                self._access_history.append((key, access_time, user_id))

                # Update key frequency
                self._key_frequency[key] += 1

                # Update temporal patterns
                hour = access_time.hour
                self._temporal_patterns[hour][key] += 1

                # Update user patterns
                if user_id:
                    self._user_patterns[user_id][key] += 1

                # Update top keys
                self._update_top_keys(key)

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            # Expected access recording errors
            if correlation_id:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_error",
                        message=f"Access recording failed: {e!s}",
                        corr_id=correlation_id,
                    )
                except (ValueError, TypeError, AttributeError, KeyError):
                    # Logging failures - don't break access recording
                    ...
        except Exception as e:
            # Unexpected access recording errors
            if correlation_id:
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     message=f"Cache operation failed unexpectedly: {e}",
                                     extra_context=str(e) + f" (error_type: {type(e).__name__})")
                except (ValueError, TypeError, AttributeError, KeyError):
                    # Logging failures - don't break access recording
                    ...
            raise CacheError(f"Cache operation failed unexpectedly: {e}") from e

    def get_top_keys(self, n: int = 50) -> list[str]:
        """Get top-N most accessed keys.

            n: Number of top keys to return

            List of top keys sorted by frequency

        """
        with self._lock:
            # Get keys sorted by frequency
            sorted_keys = sorted(
                self._key_frequency.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            return [key for key, _ in sorted_keys[:n]]

    def get_stats(self) -> dict:
        """Get warming statistics.

            Dictionary with warming statistics

        """
        with self._lock:
            stats = self._warming_stats.copy()

            # Add additional stats
            stats["total_access_records"] = len(self._access_history)
            stats["unique_keys"] = len(self._key_frequency)
            stats["temporal_patterns_count"] = len(self._temporal_patterns)
            stats["user_patterns_count"] = len(self._user_patterns)

            # Calculate hit rate for top keys
            top_keys = self.get_top_keys(50)
            if top_keys:
                total_top_access = sum(self._key_frequency[key] for key in top_keys)
                total_all_access = sum(self._key_frequency.values())
                stats["top_keys_hit_rate"] = total_top_access / total_all_access if total_all_access > 0 else 0
            else:
                stats["top_keys_hit_rate"] = 0

            return stats

    def _warm_batch(self, keys: list[str], factory: Callable,
                   correlation_id: Optional[str] = None) -> None:
        """Warm a batch of keys concurrently."""
        import sys

        # Determine thread count from lambda_preload if available
        if 'lambda_preload' in sys.modules:
            import lambda_preload
            threads = getattr(lambda_preload, 'cache_warming_threads', self.MAX_WORKERS)
        else:
            threads = self.MAX_WORKERS

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for key in keys:
                future = executor.submit(
                    execute_operation,
                    GatewayInterface.CACHE,
                    "get_with_grace_period",
                    key=key,
                    factory=factory,
                    ttl=3600,
                    grace_period=300,
                )
                futures.append(future)

            # Wait for all futures to complete
            for future in futures:
                try:
                    future.result()  # Will raise exception if failed
                except (ValueError, TypeError, AttributeError, KeyError, RuntimeError, OSError, TimeoutError) as e:
                    # Expected warming errors
                    if correlation_id:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_error",
                            message=f"Key warming failed: {e!s}",
                            corr_id=correlation_id,
                        )

    def _get_predictions(self, user_id: str, _context: Optional[dict] = None) -> list[str]:
        """Get predicted keys based on patterns.

            user_id: User ID for prediction
            context: Context information

            List of predicted keys sorted by confidence

        """
        current_hour = datetime.now().hour

        # Get temporal predictions for current hour
        temporal_scores = {}
        if current_hour in self._temporal_patterns:
            for key, count in self._temporal_patterns[current_hour].items():
                temporal_scores[key] = count / sum(self._temporal_patterns[current_hour].values())

        # Get user-specific predictions
        user_scores = {}
        if user_id in self._user_patterns:
            for key, count in self._user_patterns[user_id].items():
                user_scores[key] = count / sum(self._user_patterns[user_id].values())

        # Combine predictions
        combined_scores = {}

        # Add temporal predictions with weight 0.6
        for key, score in temporal_scores.items():
            combined_scores[key] = score * 0.6

        # Add user predictions with weight 0.4
        for key, score in user_scores.items():
            if key in combined_scores:
                combined_scores[key] += score * 0.4
            else:
                combined_scores[key] = score * 0.4

        # Filter by confidence threshold
        filtered_predictions = [
            (key, score) for key, score in combined_scores.items()
            if score >= self.PREDICTION_CONFIDENCE_THRESHOLD
        ]

        # Sort by confidence and return top keys
        filtered_predictions.sort(key=lambda x: x[1], reverse=True)
        return [key for key, _ in filtered_predictions[:self.MAX_TOP_KEYS]]

    def _update_top_keys(self, key: str) -> None:
        """Update top keys tracking efficiently."""
        if key not in self._top_keys:
            # Add new key with frequency 1
            bisect.insort(self._top_keys, (key, self._key_frequency[key]))
        else:
            # Update existing key's frequency
            for i, (k, _freq) in enumerate(self._top_keys):
                if k == key:
                    self._top_keys[i] = (key, self._key_frequency[key])
                    # Re-sort
                    self._top_keys.sort(key=lambda x: x[1], reverse=True)
                    break

        # Keep only top MAX_TOP_KEYS
        self._top_keys = self._top_keys[:self.MAX_TOP_KEYS]


# Singleton instance
_cache_warmer = None
_lock = threading.RLock()


def get_cache_warmer() -> CacheWarmer:
    """Get the cache warmer singleton instance."""
    # pylint: disable=global-statement
    global _cache_warmer
    with _lock:
        if _cache_warmer is None:
            _cache_warmer = CacheWarmer()
        return _cache_warmer


# Gateway operations for cache warming
def warm_static_data(
    keys: list[str],
    factory: Callable,
    correlation_id: Optional[str] = None,
) -> int:
    """Gateway operation for static cache warming."""
    warmer = get_cache_warmer()
    return warmer.warm_static_data(keys, factory, correlation_id)


def warm_predictive_data(
    user_id: str,
    context: Optional[dict] = None,
    correlation_id: Optional[str] = None,
) -> int:
    """Gateway operation for predictive cache warming."""
    warmer = get_cache_warmer()
    return warmer.warm_predictive_data(user_id, context, correlation_id)


def warm_trace_based(
    trace_size: int = 100,
    correlation_id: Optional[str] = None,
) -> int:
    """Gateway operation for trace-based cache warming."""
    warmer = get_cache_warmer()
    return warmer.warm_trace_based(trace_size, correlation_id)


def record_access(
    key: str,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> None:
    """Gateway operation for recording cache access."""
    warmer = get_cache_warmer()
    warmer.record_access(key, user_id, correlation_id)


def get_cache_warming_stats(_correlation_id: Optional[str] = None) -> dict:
    """Gateway operation for getting cache warming statistics."""
    warmer = get_cache_warmer()
    return warmer.get_stats()


# Alexa-specific warming strategies
def warm_alexa_discovery_data(
    user_id: str,
    correlation_id: Optional[str] = None,
) -> int:
    """Warm Alexa discovery data for a user."""
    # Define discovery data keys (this would be user-specific in real implementation)
    discovery_keys = [
        f"alexa:discovery:user:{user_id}",
        f"alexa:entities:user:{user_id}",
        f"alexa:endpoints:user:{user_id}",
    ]

    def discovery_factory(_key):
        # In real implementation, this would fetch from Home Assistant
        return {
            "discovery_data": "placeholder",  # Real implementation would fetch
            "last_updated": datetime.now().isoformat(),
        }

    warmer = get_cache_warmer()
    return warmer.warm_static_data(discovery_keys, discovery_factory, correlation_id)


def warm_alexa_entity_states(
    _user_id: str,
    top_n: int = 100,
    correlation_id: Optional[str] = None,
) -> int:
    """Warm top N most accessed entity states for a user."""
    warmer = get_cache_warmer()
    top_keys = warmer.get_top_keys(top_n)

    # Filter to include only entity state keys
    entity_keys = [key for key in top_keys if key.startswith("entity:")]

    def entity_factory(_key):
        # In real implementation, this would fetch from Home Assistant
        return {"state": "unknown", "last_updated": datetime.now().isoformat()}

    return warmer.warm_static_data(entity_keys, entity_factory, correlation_id)


def warm_alexa_capacities(correlation_id: Optional[str] = None) -> int:
    """Warm Alexa capability mappings (static data)."""
    capability_keys = [
        "alexa:capabilities:light",
        "alexa:capabilities:switch",
        "alexa:capabilities:scene",
        "alexa:capabilities:fan",
        "alexa:capabilities:lock",
        "alexa:capabilities:cover",
        "alexa:capabilities:sensor",
    ]

    def capability_factory(_key):
        return {
            "capabilities": "placeholder",  # Real implementation would have full schema
            "schema_version": "2021-10-05",
        }

    warmer = get_cache_warmer()
    return warmer.warm_static_data(capability_keys, capability_factory, correlation_id)
