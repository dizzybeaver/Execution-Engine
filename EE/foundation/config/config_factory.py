"""
Config Factory - Foundation Domain

Configuration management implementation.

EE 2.1 Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside foundation domain (except stdlib)
- All cross-domain calls via call_operation callback
- Cache maintained in factory instance (not module-level)
"""

import os
import logging
import threading
from typing import Any, Dict, Optional, Callable


class ConfigFactory:
    """Configuration management factory.

    Provides configuration operations with the following priority:
    1. SSM Parameter Store (production secrets)
    2. Environment Variables (deployment settings)
    3. Code defaults (safe fallbacks)

    EE 2.1 Compliance:
    - ONLY this factory may use os.getenv()
    - All other code MUST use execute_operation("config.get")
    - Cross-domain calls via call_operation callback
    - Uses instance-level cache (not module-level)
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize config factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # MODIFIED: Instance-level cache (was module-level)
        self._config_cache: Dict[str, Any] = {}
        self._config_lock = threading.RLock()
        self._config_loaded = False

        # Load global config
        self._load_global_config()

    # =============================================================================
    # Helper functions for environment variable parsing (instance methods)
    # =============================================================================

    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _get_env_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _get_env_float(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _get_env_list(self, key: str, default: list, separator: str = ",") -> list:
        """Get list environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(separator) if item.strip()]

    def _load_global_config(self) -> None:
        """Load global configuration from environment."""
        with self._config_lock:
            if self._config_loaded:
                return

            # Cache configuration
            self._config_cache["cache"] = {
                "total_cache_allocation_mb": self._get_env_float("EE_CACHE_TOTAL_MB", 16.0),
                "lambda_cache_mb": self._get_env_float("EE_CACHE_LAMBDA_MB", 8.0),
                "response_cache_mb": self._get_env_float("EE_CACHE_RESPONSE_MB", 6.0),
                "utility_cache_mb": self._get_env_float("EE_CACHE_UTILITY_MB", 2.0),
                "default_ttl_seconds": self._get_env_int("EE_CACHE_DEFAULT_TTL", 300),
                "lambda_ttl_seconds": self._get_env_int("EE_CACHE_LAMBDA_TTL", 300),
                "response_ttl_seconds": self._get_env_int("EE_CACHE_RESPONSE_TTL", 180),
                "utility_ttl_seconds": self._get_env_int("EE_CACHE_UTILITY_TTL", 600),
                "max_entries_per_pool": self._get_env_int("EE_CACHE_MAX_ENTRIES", 500),
                "eviction_policy": os.getenv("EE_CACHE_EVICTION_POLICY", "lru"),
            }

            # Logging configuration
            self._config_cache["logging"] = {
                "default_level": os.getenv("EE_LOGGING_LEVEL", "INFO"),
                "structured_logging": self._get_env_bool("EE_LOGGING_STRUCTURED", True),
                "console_enabled": self._get_env_bool("EE_LOGGING_CONSOLE", True),
                "file_enabled": self._get_env_bool("EE_LOGGING_FILE", False),
            }

            # Metrics configuration
            self._config_cache["metrics"] = {
                "core_metrics": self._get_env_list(
                    "EE_METRICS_CORE",
                    ["memory_usage", "error_count", "invocation_count", "duration"]
                ),
                "optional_metrics": self._get_env_list(
                    "EE_METRICS_OPTIONAL",
                    ["cache_hit_rate", "circuit_breaker_status", "ha_api_latency"]
                ),
                "collection_interval_seconds": self._get_env_int("EE_METRICS_INTERVAL", 30),
            }

            # Network configuration
            self._config_cache["network"] = {
                "redis": {
                    "host": os.getenv("EE_REDIS_HOST", "localhost"),
                    "port": self._get_env_int("EE_REDIS_PORT", 6379),
                    "db": self._get_env_int("EE_REDIS_DB", 0),
                    "password": os.getenv("EE_REDIS_PASSWORD"),
                },
                "mqtt": {
                    "broker": os.getenv("EE_MQTT_BROKER", "localhost"),
                    "port": self._get_env_int("EE_MQTT_PORT", 1883),
                    "username": os.getenv("EE_MQTT_USERNAME"),
                    "password": os.getenv("EE_MQTT_PASSWORD"),
                },
            }

            # Home Assistant configuration
            self._config_cache["home_assistant"] = {
                "enabled": self._get_env_bool("HOME_ASSISTANT_ENABLE", True),
                "url": os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123"),
                "token": os.getenv("HOME_ASSISTANT_TOKEN"),
                "timeout_seconds": self._get_env_int("HA_TIMEOUT_MS", 30000) // 1000,
            }

            self._config_loaded = True

    # =============================================================================
    # Public API
    # =============================================================================

    def get(self, category: str, key: Optional[str] = None, default: Any = None, **kwargs) -> Any:
        """Get configuration value.

        Args:
            category: Configuration category (e.g., "cache", "logging")
            key: Optional sub-key within category
            default: Default value if not found
            **kwargs: Additional parameters

        Returns:
            Configuration value or default
        """
        with self._config_lock:
            config = self._config_cache.get(category)

            if config is None:
                self.logger.warning(f"Configuration category not found: {category}")
                return default

            if key is None:
                # Return a copy to avoid external mutations
                return config.copy() if isinstance(config, dict) else config

            return config.get(key, default)

    def get_value(self, path: str, default: Any = None, **kwargs) -> Any:
        """Get configuration value by dot-notation path.

        Args:
            path: Dot-notation path (e.g., "cache.default_ttl_seconds")
            default: Default value if not found
            **kwargs: Additional parameters

        Returns:
            Configuration value or default
        """
        keys = path.split(".")

        with self._config_lock:
            value = self._config_cache

            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                    if value is None:
                        self.logger.warning(f"Configuration path not found: {path}")
                        return default
                else:
                    self.logger.warning(f"Configuration path invalid at {key}: {path}")
                    return default

            return value

    def set(self, category: str, key: str, value: Any, **kwargs) -> bool:
        """Set configuration value at runtime.

        Args:
            category: Configuration category
            key: Configuration key
            value: Value to set
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._config_lock:
            if category not in self._config_cache:
                self._config_cache[category] = {}

            self._config_cache[category][key] = value

        self.logger.info(f"Configuration updated: {category}.{key} = {value}")
        return True

    def delete(self, category: str, key: Optional[str] = None, **kwargs) -> bool:
        """Delete configuration value.

        Args:
            category: Configuration category
            key: Optional key to delete (if None, deletes entire category)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._config_lock:
            if category not in self._config_cache:
                return False

            if key is None:
                del self._config_cache[category]
            else:
                if key in self._config_cache[category]:
                    del self._config_cache[category][key]
                else:
                    return False

        return True

    def get_all(self, **kwargs) -> Dict[str, Any]:
        """Get all configuration.

        Args:
            **kwargs: Additional parameters

        Returns:
            All configuration dictionary
        """
        with self._config_lock:
            return self._config_cache.copy()

    def reload(self, **kwargs) -> Dict[str, Any]:
        """Reload configuration from environment.

        Args:
            **kwargs: Additional parameters

        Returns:
            Reloaded configuration
        """
        self.logger.info("Reloading configuration from environment")

        with self._config_lock:
            self._config_cache.clear()
            self._config_loaded = False
            self._load_global_config()
            return self._config_cache.copy()

    def validate(self, **kwargs) -> bool:
        """Validate configuration.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if configuration is valid
        """
        with self._config_lock:
            # Validate cache allocation
            cache = self._config_cache.get("cache", {})
            total = (
                cache.get("lambda_cache_mb", 0) +
                cache.get("response_cache_mb", 0) +
                cache.get("utility_cache_mb", 0)
            )
            expected = cache.get("total_cache_allocation_mb", 0)
            if abs(total - expected) > 0.01:
                self.logger.warning(
                    f"Cache allocation mismatch: sum={total}MB, total={expected}MB"
                )
                return False

            return True


__all__ = [
    "ConfigFactory",
]
