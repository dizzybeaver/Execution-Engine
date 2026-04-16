"""cache/cache_batch_operations.py
Version: 2025-03-03_1
Purpose: Multi-get batch operations for LUGS-integrated cache
License: Apache 2.0

Implements batch operations (mget, mset, mdelete, mget_metadata) extending
LUGSIntegratedCacheOperations with optimized batch processing and proper
SUGA-ISP pattern compliance.
"""

import os
from contextlib import nullcontext as _nullcontext
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_cache.cache_enums import _CACHE_MISS, DEFAULT_CACHE_TTL
from lee.lee_cache.cache_operations import LUGSIntegratedCacheOperations
from lee.singleton import SingletonFactory


class MultiGetOperations(LUGSIntegratedCacheOperations):
    """Extended cache operations with batch multi-get/set/delete capabilities.

    Provides efficient batch operations for cache access patterns:
    - mget: Retrieve multiple keys in a single call
    - mset: Set multiple key-value pairs in a single call
    - mdelete: Delete multiple keys in a single call
    - mget_metadata: Retrieve metadata for multiple keys

    All operations include proper correlation_id propagation and timing
    instrumentation following SUGA-ISP pattern.

    Example:
        cache = MultiGetOperations()
        result = cache.mget(['key1', 'key2', 'key3'], correlation_id='abc123')
        # Returns: {'key1': value1, 'key3': value3} (key2 not found)

        cache.mset({'key1': 'val1', 'key2': 'val2'}, ttl=300)
        # Returns: 2 (number of keys set)

    """

    def mget(self, keys: list[str], correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Batch retrieve multiple keys from cache.

        Retrieves all specified keys and returns a dictionary containing only
        the keys that were found (not expired, not missing). Missing or expired
        keys are silently excluded from the result.

            keys: List of cache keys to retrieve
            correlation_id: Optional correlation ID for tracing. If None,
                generates inline ID using timestamp + random
            **kwargs: Additional context parameters

            Dict[str, Any]: Dictionary mapping found keys to their values.
                Only includes keys that exist and are not expired.

        Example:
            >>> cache.mget(['user:1', 'user:2', 'user:3'])
            {'user:1': {'name': 'Alice'}, 'user:3': {'name': 'Charlie'}}
            # Note: 'user:2' was missing/expired, so not in result
            Each key is checked individually for existence and expiration.

        """
        if correlation_id is None:
            # SUGA-ISP compliant - use utility function
            correlation_id = generate_correlation_id(prefix="cache")

        # SUGA-ISP compliance - all debug through execute_operation
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="mget called", keys=keys, key_count=len(keys))
        except ImportError:
            # Gateway not available - acceptable for standalone usage
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         correlation_id=correlation_id,
                                         operation_name="mget",
                                         key_count=len(keys))
        except ImportError:
            timing_ctx = _nullcontext()  # pylint: disable=reimported

        with timing_ctx:
            result = {}
            for key in keys:
                value = self.get(key, correlation_id=correlation_id, **kwargs)
                if value is not _CACHE_MISS:
                    result[key] = value

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="CACHE",
                                 message="mget completed",
                                 requested=len(keys),
                                 found=len(result))
            except ImportError:
                # Gateway not available - acceptable for standalone usage
                ...

            return result

    def mset(self, items: dict[str, Any], ttl: int = DEFAULT_CACHE_TTL,
             correlation_id: str = None, **kwargs) -> int:
        """Batch set multiple key-value pairs in cache.

        Sets all specified key-value pairs with the provided TTL (Time To Live).
        All items use the same TTL. If different TTLs are needed, call set()
        individually for each key.

            items: Dictionary mapping keys to their values
            ttl: Time-to-live in seconds for all items. Defaults to DEFAULT_CACHE_TTL
            correlation_id: Optional correlation ID for tracing. If None,
                generates inline ID using timestamp + random
            **kwargs: Additional context parameters

            int: Number of keys successfully set (should equal len(items))

        Example:
            >>> cache.mset({'user:1': 'Alice', 'user:2': 'Bob'}, ttl=600)
            2

        """
        if correlation_id is None:
            # SUGA-ISP compliant - use utility function
            correlation_id = generate_correlation_id(prefix="cache")

        # SUGA-ISP compliance - all debug through execute_operation
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="mset called",
                             item_count=len(items),
                             ttl=ttl)
        except ImportError:
            # Gateway not available - acceptable for standalone usage
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         correlation_id=correlation_id,
                                         operation_name="mset",
                                         item_count=len(items),
                                         ttl=ttl)
        except ImportError:
            timing_ctx = _nullcontext()

        with timing_ctx:
            count = 0
            for key, value in items.items():
                # set() doesn't return a value, so we count successful sets by checking if key exists after
                try:
                    self.set(key, value, ttl=ttl, correlation_id=correlation_id, **kwargs)
                    # Verify the key was actually set
                    if key in self._cache:
                        count += 1
                except (OSError, RuntimeError, TypeError, ValueError) as set_error:
                    # Log and continue - individual set failures shouldn't abort entire batch
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_error",
                            message=f"Batch set failed for key {key}: {set_error}",
                            extra_context={"operation": "mset", "key": key, "ttl": ttl},
                        )
                    except ImportError as import_error:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_warning',
                                message=f'Module import failed: {import_error}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="CACHE",
                                 message="mset completed",
                                 requested=len(items),
                                 set_count=count)
            except ImportError:
                # Gateway not available - acceptable for standalone usage
                ...

            return count

    def mdelete(self, keys: list[str], correlation_id: str = None, **kwargs) -> int:
        """Batch delete multiple keys from cache.

        Deletes all specified keys from the cache. Returns the count of keys
        that were actually deleted (i.e., existed before deletion). Keys that
        don't exist are ignored but not counted.

            keys: List of cache keys to delete
            correlation_id: Optional correlation ID for tracing. If None,
                generates inline ID using timestamp + random
            **kwargs: Additional context parameters

            int: Number of keys that were actually deleted (existed in cache)

        Example:
            >>> cache.mdelete(['user:1', 'user:2', 'user:3'])
            2
            # Returns 2 if 'user:2' didn't exist


        """
        if correlation_id is None:
            # SUGA-ISP compliant - use utility function
            correlation_id = generate_correlation_id(prefix="cache")

        # SUGA-ISP compliance - all debug through execute_operation
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="mdelete called",
                             keys=keys,
                             key_count=len(keys))
        except ImportError:
            # Gateway not available - acceptable for standalone usage
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         correlation_id=correlation_id,
                                         operation_name="mdelete",
                                         key_count=len(keys))
        except ImportError:
            timing_ctx = _nullcontext()

        with timing_ctx:
            count = 0
            for key in keys:
                deleted = self.delete(key, correlation_id=correlation_id, **kwargs)
                if deleted:
                    count += 1

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="CACHE",
                                 message="mdelete completed",
                                 requested=len(keys),
                                 deleted_count=count)
            except ImportError:
                # Gateway not available - acceptable for standalone usage
                ...

            return count

    def mget_metadata(self, keys: list[str], correlation_id: str = None, **kwargs) -> dict[str, dict]:
        """Batch retrieve metadata for multiple keys.

        Retrieves metadata (creation time, expiration, size, access count)
        for all specified keys. Returns only keys that exist and are not expired.

        Metadata includes:
        - 'source_module': Module that created the entry (or None)
        - 'timestamp': Unix timestamp when entry was created
        - 'age_seconds': Age of entry in seconds
        - 'ttl': Time-to-live in seconds
        - 'ttl_remaining': Remaining TTL in seconds
        - 'access_count': Number of times this entry has been accessed
        - 'last_access': Unix timestamp of last access
        - 'size_bytes': Approximate size in bytes
        - 'is_expired': Whether entry is expired (always False for non-expired entries)

            keys: List of cache keys to get metadata for
            correlation_id: Optional correlation ID for tracing. If None,
                generates inline ID using timestamp + random
            **kwargs: Additional context parameters

            Dict[str, Dict]: Dictionary mapping found keys to their metadata.
                Only includes keys that exist and are not expired.

        Example:
            >>> cache.mget_metadata(['user:1', 'user:2'])
            {
                'user:1': {
                    'source_module': None,
                    'timestamp': 1735670400.0,
                    'age_seconds': 10.5,
                    'ttl': 300,
                    'ttl_remaining': 289.5,
                    'access_count': 5,
                    'last_access': 1735670410.0,
                    'size_bytes': 431,
                    'is_expired': False
                }
            }
            # Note: 'user:2' was missing/expired, so not in result


        """
        if correlation_id is None:
            # SUGA-ISP compliant - use utility function
            correlation_id = generate_correlation_id(prefix="cache")

        # SUGA-ISP compliance - all debug through execute_operation
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="mget_metadata called",
                             keys=keys,
                             key_count=len(keys))
        except ImportError:
            # Gateway not available - acceptable for standalone usage
            ...

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         correlation_id=correlation_id,
                                         operation_name="mget_metadata",
                                         key_count=len(keys))
        except ImportError:
            timing_ctx = _nullcontext()

        with timing_ctx:
            result = {}
            for key in keys:
                metadata = self.get_metadata(key, correlation_id=correlation_id, **kwargs)
                if metadata is not None:
                    result[key] = metadata

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="CACHE",
                                 message="mget_metadata completed",
                                 requested=len(keys),
                                 found=len(result))
            except ImportError:
                # Gateway not available - acceptable for standalone usage
                ...

            return result


# Singleton factory for batch cache operations
_batch_cache_factory: Optional[SingletonFactory[MultiGetOperations]] = None


def _get_batch_cache_factory() -> SingletonFactory[MultiGetOperations]:
    """Get or create the batch cache singleton factory."""
    global _batch_cache_factory  # pylint: disable=global-statement
    if _batch_cache_factory is None:
        _batch_cache_factory = SingletonFactory(MultiGetOperations)  # pylint: disable=unnecessary-lambda
    return _batch_cache_factory


def _get_batch_cache_instance(**_kwargs) -> "MultiGetOperations":  # pylint: disable=unused-argument
    """Get or create the singleton batch cache instance."""
    return _get_batch_cache_factory().get_instance()


# Convenience functions for batch operations (following pattern from cache_operations.py)

def cache_mget(keys: list[str], correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Convenience function for batch get operations.

        keys: List of cache keys to retrieve
        correlation_id: Optional correlation ID for tracing
        **kwargs: Additional context parameters

        Dict[str, Any]: Dictionary of found keys mapped to their values

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    if debug_enabled:
        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache_batch")
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mget: keys={list(keys)[:5]} count={len(keys)}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    cache = _get_batch_cache_instance(**kwargs)
    result = cache.mget(keys, correlation_id=correlation_id, **kwargs)

    if debug_enabled:
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mget completed: found={len(result)}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    return result


def cache_mset(items: dict[str, Any], ttl: int = DEFAULT_CACHE_TTL,
               correlation_id: str = None, **kwargs) -> int:
    """Convenience function for batch set operations.

        items: Dictionary mapping keys to their values
        ttl: Time-to-live in seconds for all items
        correlation_id: Optional correlation ID for tracing
        **kwargs: Additional context parameters

        int: Number of keys successfully set

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    if debug_enabled:
        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache_batch")
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mset: items={list(items.keys())[:5]} count={len(items)} ttl={ttl}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    cache = _get_batch_cache_instance(**kwargs)
    result = cache.mset(items, ttl=ttl, correlation_id=correlation_id, **kwargs)

    if debug_enabled:
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mset completed: set_count={result}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    return result


def cache_mdelete(keys: list[str], correlation_id: str = None, **kwargs) -> int:
    """Convenience function for batch delete operations.

        keys: List of cache keys to delete
        correlation_id: Optional correlation ID for tracing
        **kwargs: Additional context parameters

        int: Number of keys that were actually deleted

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    if debug_enabled:
        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache_batch")
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mdelete: keys={list(keys)[:5]} count={len(keys)}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    cache = _get_batch_cache_instance(**kwargs)
    result = cache.mdelete(keys, correlation_id=correlation_id, **kwargs)

    if debug_enabled:
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mdelete completed: deleted_count={result}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    return result


def cache_mget_metadata(keys: list[str], correlation_id: str = None, **kwargs) -> dict[str, dict]:
    """Convenience function for batch metadata retrieval.

        keys: List of cache keys to get metadata for
        correlation_id: Optional correlation ID for tracing
        **kwargs: Additional context parameters

        Dict[str, Dict]: Dictionary of found keys mapped to their metadata

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    if debug_enabled:
        if correlation_id is None:
            correlation_id = generate_correlation_id(prefix="cache_batch")
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mget_metadata: keys={list(keys)[:5]} count={len(keys)}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    cache = _get_batch_cache_instance(**kwargs)
    result = cache.mget_metadata(keys, correlation_id=correlation_id, **kwargs)

    if debug_enabled:
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Cache mget_metadata completed: found={len(result)}",
                         scope='CACHE_BATCH',
                         corr_id=correlation_id)

    return result


__all__ = [
    "MultiGetOperations",
    "cache_mdelete",
    "cache_mget",
    "cache_mget_metadata",
    "cache_mset",
]

# EOF
