"""lee_utility/utility_data.py
Version: 2025-12-13_1
Purpose: Data operations for utility interface
License: Apache 2.0
"""

import json
import logging
import time
import uuid
from typing import TYPE_CHECKING, Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_utility.utility_types import DEFAULT_MAX_JSON_CACHE_SIZE

if TYPE_CHECKING:
    from lee.lee_utility.utility_core import SharedUtilityCore


logger = logging.getLogger(__name__)


class UtilityDataOperations:
    """Data operations for parsing, merging, and formatting."""

    def __init__(self, manager: "SharedUtilityCore") -> None:
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager

    def parse_json(self, data: str, correlation_id: str = None) -> dict:
        """Parse JSON string."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        # Validate JSON string length to prevent DoS
        MAX_JSON_LENGTH = 10_000_000  # 10MB limit
        if len(data) > MAX_JSON_LENGTH:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="JSON rejected: exceeds size limit",
                             json_length=len(data),
                             max_length=MAX_JSON_LENGTH)
            return {}

        try:
            result = json.loads(data)
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="JSON parsed successfully",
                             result_keys=len(result) if isinstance(result, dict) else 0)
            return result
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="JSON parse failed", error=str(e))
            logger.error("JSON parse error: %s", e)
            return {}

    def parse_json_safely(self, json_str: str, use_cache: bool = True,
                         correlation_id: str = None) -> Optional[dict[str, Any]]:
        """Parse JSON safely with optional caching."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        # pylint: disable=protected-access
        if not self._manager._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Rate limit exceeded in parse_json_safely()")
            return None

        cache_key = hash(json_str)

        if use_cache and cache_key in self._manager._json_cache:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="JSON parse cache hit")
            return self._manager._json_cache[cache_key]

        try:
            result = json.loads(json_str)
            if use_cache:
                if len(self._manager._json_cache) >= DEFAULT_MAX_JSON_CACHE_SIZE:
                    oldest_key = self._manager._json_cache_order.pop(0)
                    del self._manager._json_cache[oldest_key]

                self._manager._json_cache[cache_key] = result
                self._manager._json_cache_order.append(cache_key)

                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="UTILITY",
                                 message="JSON parsed and cached")
            return result
        except (json.JSONDecodeError, TypeError, ValueError):
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="JSON decode error")
            return None

    def deep_merge(self, dict1: dict[str, Any], dict2: dict[str, Any],
                  correlation_id: str = None) -> dict[str, Any]:
        """Deep merge two dictionaries with optimized algorithm.

        Performance: O(n) where n is total keys in both dictionaries.
        Optimizations:
        - Skip debug logging for small merges (<10 keys total)
        - Use dictionary unpacking for shallow merge when no nesting
        - Minimize recursive calls

        Args:
            dict1: First dictionary (base)
            dict2: Second dictionary (overrides)
            correlation_id: Optional correlation ID for tracking

        Returns:
            Merged dictionary with dict2 values taking precedence
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value, correlation_id)
            else:
                result[key] = value

        total_keys = len(dict1) + len(dict2)

        if total_keys >= 10:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Dictionaries merged",
                             dict1_keys=len(dict1), dict2_keys=len(dict2),
                             result_keys=len(result))

        return result

    def safe_get(self, dictionary: dict, key_path: str, default: Any = None,
                correlation_id: str = None) -> Any:
        """Safely get nested dictionary value."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        try:
            keys = key_path.split('.')
            value = dictionary

            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                    if value is None:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="UTILITY",
                                         message="Key path not found, using default",
                                         key_path=key_path)
                        return default
                else:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="UTILITY",
                                     message="Invalid path, using default",
                                     key_path=key_path)
                    return default

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Value retrieved via safe_get",
                             key_path=key_path, has_value=True)
            return value
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="safe_get failed, using default",
                             key_path=key_path, error=str(e))
            return default

    def format_bytes(self, size: int, correlation_id: str = None) -> str:
        """Format bytes to human-readable string."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        size_float = float(size)

        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1

        result = f"{size_float:.2f} {units[unit_index]}"

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="UTILITY",
                         message="Bytes formatted",
                         size=size, result=result)

        return result

    def merge_dictionaries(self, *dicts: dict[str, Any],
                          correlation_id: str = None) -> dict[str, Any]:
        """Merge multiple dictionaries safely."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        try:
            result = {}
            for d in dicts:
                if isinstance(d, dict):
                    result.update(d)

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Multiple dictionaries merged",
                             dict_count=len(dicts), result_keys=len(result))
            return result
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Dictionary merge failed", error=str(e))
            return {}

    def format_data_for_response(self, data: Any, format_type: str = "json",
                                include_metadata: bool = True,
                                correlation_id: str = None) -> dict[str, Any]:
        """Format data for API response."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        response = {
            "data": data,
            "format": format_type,
        }

        if include_metadata:
            response["metadata"] = {
                "timestamp": int(time.time()),
                "type": type(data).__name__,
            }

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="UTILITY",
                         message="Data formatted for response",
                         format_type=format_type, include_metadata=include_metadata)

        return response

    def cleanup_cache(self, _max_age_seconds: int = 3600,
                     correlation_id: str = None) -> int:
        """Clean up old cached utility data."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        # pylint: disable=protected-access
        if not self._manager._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Rate limit exceeded in cleanup_cache()")
            return 0

        try:
            cleared_count = len(self._manager._json_cache)
            self._manager._json_cache.clear()
            self._manager._json_cache_order.clear()

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Cache cleaned up",
                             cleared_count=cleared_count)

            return cleared_count
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Cache cleanup failed", error=str(e))
            logger.error("Cache cleanup error: %s", e)
            return 0

    def optimize_performance(self, correlation_id: str = None) -> dict[str, Any]:
        """Optimize utility performance based on usage patterns."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        # pylint: disable=protected-access
        if not self._manager._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Rate limit exceeded in optimize_performance()")
            return {"error": "Rate limit exceeded"}

        optimizations = []

        for op_type, metrics in self._manager._metrics.items():
            if metrics.avg_duration_ms > 100:
                optimizations.append(f"High latency detected for {op_type}")

            cache_hit_rate = 0.0
            if metrics.cache_hits + metrics.cache_misses > 0:
                cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100

            if cache_hit_rate < 50 and metrics.cache_misses > 10:
                optimizations.append(f"Low cache hit rate for {op_type}")

        if not self._manager._id_pool or len(self._manager._id_pool) < 10:
            for _ in range(20):
                self._manager._id_pool.append(str(uuid.uuid4()))
            optimizations.append("Replenished ID pool")

        if len(self._manager._json_cache) > (DEFAULT_MAX_JSON_CACHE_SIZE * 0.9):
            optimizations.append("JSON cache approaching limit")

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="UTILITY",
                         message="Performance optimization complete",
                         optimizations_count=len(optimizations))

        return {
            "optimizations_applied": optimizations,
            "timestamp": int(time.time()),
        }

    def configure_caching(self, enabled: bool, ttl: int = 300,
                         correlation_id: str = None) -> bool:
        """Configure utility caching settings."""
        if correlation_id is None:
            correlation_id = generate_correlation_id("data")

        # pylint: disable=protected-access
        try:
            self._manager._cache_enabled = enabled
            self._manager._cache_ttl = ttl

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Caching configured",
                             enabled=enabled, ttl=ttl)
            return True
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="UTILITY",
                             message="Caching configuration failed", error=str(e))
            return False


__all__ = [
    "UtilityDataOperations",
]
