"""utility/utility_stats.py
Version: 2025-12-21_1
Purpose: Utility statistics and performance monitoring
License: Apache 2.0
"""

# pylint: disable=protected-access
# We access protected members of SharedUtilityCore as this is an internal
# statistics module that is part of the same utility package.

from typing import TYPE_CHECKING, Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_utility.utility_types import DEFAULT_MAX_JSON_CACHE_SIZE

if TYPE_CHECKING:
    from lee.lee_utility.utility_core import SharedUtilityCore
else:
    from lee.lee_utility.utility_core import SharedUtilityCore


# SINGLETON pattern (LESS-18)
_manager_core = None


class UtilityStats:
    """Utility statistics and performance monitoring.

    SUGA-ISP compliant: All operations route through Gateway.
    """
    def __init__(self, core_manager: "SharedUtilityCore") -> None:
        self._core = core_manager

    def get_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get utility statistics."""

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._core._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Rate limit exceeded in get_stats()")
            return {"error": "Rate limit exceeded"}

        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Getting statistics")
        return self.get_performance_stats(correlation_id)

    def get_performance_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get utility performance statistics."""

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._core._check_rate_limit():
            return {"error": "Rate limit exceeded"}

        operation_stats = {}

        for op_type, metrics in self._core._metrics.items():
            cache_hit_rate = 0.0
            if metrics.cache_hits + metrics.cache_misses > 0:
                cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100

            error_rate = 0.0
            if metrics.call_count > 0:
                error_rate = metrics.error_count / metrics.call_count * 100

            template_usage_rate = 0.0
            if metrics.call_count > 0:
                template_usage_rate = metrics.template_usage / metrics.call_count * 100

            operation_stats[op_type] = {
                "call_count": metrics.call_count,
                "avg_duration_ms": round(metrics.avg_duration_ms, 2),
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "error_rate_percent": round(error_rate, 2),
                "template_usage_percent": round(template_usage_rate, 2),
                "cache_hits": metrics.cache_hits,
                "cache_misses": metrics.cache_misses,
                "error_count": metrics.error_count,
                "template_usage": metrics.template_usage,
            }

        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Performance statistics retrieved",
                        operation_count=len(operation_stats))

        return {
            "overall_stats": self._core._stats,
            "operation_stats": operation_stats,
            "id_pool_size": len(self._core._id_pool),
            "json_cache_size": len(self._core._json_cache),
            "json_cache_limit": DEFAULT_MAX_JSON_CACHE_SIZE,
            "cache_enabled": self._core._cache_enabled,
            "rate_limited_count": self._core._rate_limited_count,
        }

    def reset(self, correlation_id: str = None) -> bool:
        """Reset UTILITY manager state."""

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._core._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Rate limit exceeded in reset()")
            return False

        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Resetting utility manager state")

        try:
            self._core._metrics.clear()
            self._core._stats = {
                "template_hits": 0,
                "template_fallbacks": 0,
                "cache_optimizations": 0,
                "id_pool_reuse": 0,
                "lugs_integrations": 0,
                "templates_rendered": 0,
                "configs_retrieved": 0,
            }
            self._core._json_cache.clear()
            self._core._json_cache_order.clear()
            self._core._id_pool.clear()
            self._core._rate_limiter.clear()
            self._core._rate_limited_count = 0

            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Utility manager reset complete")
            return True
        except (ValueError, TypeError, KeyError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message=f"Reset failed: {e}")
            return False
        except (AttributeError, RuntimeError, OSError):
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Reset failed")
            return False


def get_utility_stats(core_manager: "SharedUtilityCore", correlation_id: str = None) -> UtilityStats:
    """Get utility statistics instance."""
    _ = correlation_id  # Reserved for future use
    return UtilityStats(core_manager)


def get_utility_manager() -> "SharedUtilityCore":
    """Get the utility manager instance (SINGLETON pattern).

    Uses gateway SINGLETON registry with fallback to module-level instance.

        SharedUtilityCore instance

    """
    global _manager_core

    try:

        manager = execute_operation(GatewayInterface.SINGLETON, "get",
                                  name="utility_manager")
        if manager is None:
            if _manager_core is None:
                _manager_core = SharedUtilityCore()
            execute_operation(GatewayInterface.SINGLETON, "register",
                            name="utility_manager", instance=_manager_core)
            manager = _manager_core

        return manager
    except Exception:
        if _manager_core is None:
            _manager_core = SharedUtilityCore()
        return _manager_core


__all__ = [
    "UtilityStats",
    "get_utility_manager",
    "get_utility_stats",
]
