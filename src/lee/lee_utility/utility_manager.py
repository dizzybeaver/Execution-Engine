"""utility/utility_manager.py
Version: 2025-12-21_1
Purpose: Main utility manager interface with SUGA-ISP compliance
License: Apache 2.0
"""

from typing import Any, Optional

from lee.lee_utility.utility_core import SharedUtilityCore
from lee.lee_utility.utility_stats import get_utility_manager as _get_utility_manager
from lee.lee_utility.utility_stats import get_utility_stats


class UtilityManager:
    """Main utility manager interface.

    Provides unified access to all utility operations while maintaining
    SUGA-ISP architecture compliance.
    """

    def __init__(self):
        self._core = _get_utility_manager()
        self._stats = get_utility_stats(self._core)

    # === UUID AND TIMESTAMP ===

    def generate_uuid(self, correlation_id: str = None) -> str:
        """Generate UUID with pool optimization."""
        return self._core.generate_uuid(correlation_id)

    def get_timestamp(self, correlation_id: str = None) -> str:
        """Get current timestamp as ISO string."""
        return self._core.get_timestamp(correlation_id)

    def get_timestamp_numeric(self, correlation_id: str = None) -> float:
        """Get current timestamp as Unix timestamp (seconds since epoch)."""
        return self._core.get_timestamp_numeric(correlation_id)

    def generate_correlation_id_impl(self, prefix: Optional[str] = None,
                                     correlation_id: str = None) -> str:
        """Generate correlation ID with optional prefix."""
        return self._core.generate_correlation_id_impl(prefix, correlation_id)

    # === TEMPLATE RENDERING ===

    def render_template_impl(self, template: dict, data: dict,
                            correlation_id: str = None, **kwargs) -> dict:
        """Render template with {placeholder} substitution."""
        return self._core.render_template_impl(template, data, correlation_id, **kwargs)

    # === CONFIG RETRIEVAL ===

    def config_get_impl(self, key: str, default=None,
                       correlation_id: str = None, **kwargs) -> Any:
        """Get typed configuration value from environment."""
        return self._core.config_get_impl(key, default, correlation_id, **kwargs)

    # === PERFORMANCE AND STATS ===

    def get_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get utility statistics."""
        return self._stats.get_stats(correlation_id)

    def get_performance_stats(self, correlation_id: str = None) -> dict[str, Any]:
        """Get utility performance statistics."""
        return self._stats.get_performance_stats(correlation_id)

    def reset(self, correlation_id: str = None) -> bool:
        """Reset UTILITY manager state."""
        return self._stats.reset(correlation_id)

    # === SAFE SUBPROCESS ===

    def safe_subprocess_run(  # pylint: disable=too-many-arguments too-many-positional-arguments
        self, command: list, timeout: int = 30,
        capture_output: bool = True, check: bool = False,
        cwd: str = None, env: dict = None,
        correlation_id: str = None, **_kwargs
    ) -> dict:
        """Safely execute subprocess with comprehensive security validation."""
        return self._core.safe_subprocess_run_implementation(
            command=command, timeout=timeout, capture_output=capture_output,
            check=check, cwd=cwd, env=env, correlation_id=correlation_id,
        )


def get_utility_manager() -> UtilityManager:
    """Get the utility manager instance (SINGLETON pattern).

    Returns:
        UtilityManager instance with SUGA-ISP compliance

    """
    return UtilityManager()


__all__ = [
    "SharedUtilityCore",  # Export for backward compatibility
    "UtilityManager",
    "get_utility_manager",
]
