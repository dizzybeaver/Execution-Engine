# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Add multi-mode configuration loading

"""
ha_config.py - Home Assistant Configuration

Version: 2026-03-26_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0

This module provides feature flags and configuration settings for Home Assistant integration
with multi-mode configuration loading support.
"""

from __future__ import annotations

import collections
import os
import threading
from typing import Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.decorators import cached_gateway_operation
from lee.lee_security import InputSanitizer, SanitizeLevel
from lee.lee_config.config_schema import (
    safe_bool_parameter,
    safe_int_parameter,
    safe_str_parameter,
)


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


# Feature flag for consolidated response utilities
# When True: Uses consolidated utilities from ha_common.alexa_response_utils
# When False: Uses legacy controller-based response generation
CONSOLIDATED_RESPONSE_ENABLED = True


class HAConfigPool:
    """Object pool for HAConfig instances to reduce creation overhead.

    Reuses HAConfig objects instead of creating new ones repeatedly.
    Thread-safe with lock-free operations using LRU pattern.

    Example:
        pool = HAConfigPool.get_instance()
        config = pool.acquire()
        try:
            # Use config
            ...
        finally:
            pool.release(config)
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_size: int = 10):
        """Initialize HAConfigPool.

        Args:
            max_size: Maximum number of pooled objects
        """
        self._pool: collections.deque[HAConfig] = collections.deque(maxlen=max_size)
        self._max_size = max_size

    def acquire(self) -> HAConfig:
        """Acquire a config object from the pool.

        Returns a recycled config object or creates new one if pool empty.

        Returns:
            HAConfig instance ready for use
        """
        with HAConfigPool._lock:
            try:
                return self._pool.popleft()
            except IndexError:
                # Pool empty - create new instance
                return HAConfig()

    def release(self, config: HAConfig) -> None:
        """Release a config object back to the pool.

        Args:
            config: HAConfig instance to recycle
        """
        with HAConfigPool._lock:
            # Reset config to default state
            config.source = 'defaults'
            config.HOME_ASSISTANT_URL = None
            config.HOME_ASSISTANT_API_KEY = None
            config.REGISTRY_ENABLED = None
            config.REGISTRY_TIMEOUT = None
            config.WEBSOCKET_POOL_SIZE = None
            config.WEBSOCKET_IDLE_TIMEOUT = None
            config.WEBSOCKET_CONNECTION_TIMEOUT = None

            # Add back to pool (deque handles max size automatically)
            self._pool.append(config)

    @staticmethod
    def get_instance() -> HAConfigPool:
        """Get singleton HAConfigPool instance.

        Returns:
            Shared HAConfigPool instance
        """
        if HAConfigPool._instance is None:
            with HAConfigPool._lock:
                if HAConfigPool._instance is None:
                    HAConfigPool._instance = HAConfigPool()
        return HAConfigPool._instance


class HAConfig:
    """
    Home Assistant configuration container.

    Attributes:
        source: Configuration source ('environment', 'config_file', 'parameter_store', 'defaults')
        HOME_ASSISTANT_URL: Home Assistant instance URL
        HOME_ASSISTANT_API_KEY: Home Assistant authentication token (long-lived access token)
    """

    def __init__(self, source: str = 'defaults'):
        """
        Initialize HAConfig.

        Args:
            source: Configuration source identifier
        """
        # pylint: disable=too-many-instance-attributes
        self.source = source
        self.HOME_ASSISTANT_URL: Optional[str] = None
        self.HOME_ASSISTANT_API_KEY: Optional[str] = None
        self.REGISTRY_ENABLED: Optional[bool] = None
        self.REGISTRY_TIMEOUT: Optional[int] = None
        self.WEBSOCKET_POOL_SIZE: Optional[int] = None
        self.WEBSOCKET_IDLE_TIMEOUT: Optional[int] = None
        self.WEBSOCKET_CONNECTION_TIMEOUT: Optional[int] = None


def _validate_and_log_config(config: HAConfig, source: str) -> bool:
    """Validate configuration and log warnings for missing values.

    Args:
        config: HAConfig object to validate
        source: Configuration source name for logging

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if not config.HOME_ASSISTANT_URL and not config.HOME_ASSISTANT_API_KEY:
        try:
            # pylint: disable=reimported,redefined-outer-name
            execute_operation(
                GatewayInterface.LOGGING,
                "log_warning",
                message=f"HA configuration from {source} is incomplete: "
                       f"both HOME_ASSISTANT_URL and HOME_ASSISTANT_API_KEY are empty",
                source=source,
            )
        except (ImportError, AttributeError, RuntimeError) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'Exception occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return False

    if not config.HOME_ASSISTANT_URL:
        try:
            # pylint: disable=reimported,redefined-outer-name
            execute_operation(
                GatewayInterface.LOGGING,
                "log_warning",
                message=f"HA configuration from {source} is incomplete: "
                       f"HOME_ASSISTANT_URL is empty or too short",
                source=source,
            )
        except (ImportError, AttributeError, RuntimeError) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'Exception occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return False

    if not config.HOME_ASSISTANT_API_KEY:
        try:
            # pylint: disable=reimported,redefined-outer-name
            execute_operation(
                GatewayInterface.LOGGING,
                "log_warning",
                message=f"HA configuration from {source} is incomplete: "
                       f"HOME_ASSISTANT_API_KEY is empty",
                source=source,
            )
        except (ImportError, AttributeError, RuntimeError) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'Exception occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return False

    return True


@cached_gateway_operation(ttl_seconds=60)
def get_ha_config() -> HAConfig:
    """
    Get Home Assistant configuration using mode-aware source priority.

    Lambda mode priority: env -> parameter_store -> defaults
    Local/WSGI mode priority: dotenv -> env -> defaults

    Returns:
        HAConfig: Configuration object with source attribute
    """
    # pylint: disable=import-outside-toplevel
    from lee.home_assistant.ha_deployment_mode import get_config_source_priority

    priority = get_config_source_priority()

    for source in priority:
        config = _load_config_from_source(source)
        if config is not None:
            return config

    # Fallback to defaults
    return _load_defaults()


def _load_config_from_source(source: str) -> Optional[HAConfig]:
    """
    Load configuration from specified source.

    Args:
        source: Configuration source name ('environment', 'config_file', 'parameter_store', 'defaults')

    Returns:
        HAConfig: Configuration object or None if source not available
    """
    loaders = {
        'environment': _load_from_env,
        'config_file': _load_from_dotenv,
        'parameter_store': _load_from_parameter_store,
        'defaults': _load_defaults
    }

    loader = loaders.get(source)
    if loader:
        return loader()

    # Return defaults for unknown sources
    return _load_defaults()


def _load_from_env() -> Optional[HAConfig]:
    """
    Load configuration from environment variables.

    Returns:
        HAConfig: Configuration object if env vars found, None otherwise
    """
    config = HAConfig(source='environment')

    # Load HOME_ASSISTANT_URL with validation
    config.HOME_ASSISTANT_URL = safe_str_parameter(
        'HOME_ASSISTANT_URL',
        '',  # Empty default - will return None if not set
        min_length=10,
        max_length=2000,
    )

    # Load HOME_ASSISTANT_API_KEY with validation
    # Also check HOME_ASSISTANT_TOKEN for compatibility with test scripts
    config.HOME_ASSISTANT_API_KEY = safe_str_parameter(
        'HOME_ASSISTANT_API_KEY',
        '',  # Empty default - will return None if not set
        min_length=1,
        max_length=500,
    )

    # Fallback to HOME_ASSISTANT_TOKEN if HOME_ASSISTANT_API_KEY not set
    if not config.HOME_ASSISTANT_API_KEY:
        config.HOME_ASSISTANT_API_KEY = safe_str_parameter(
            'HOME_ASSISTANT_TOKEN',
            '',  # Empty default - will return None if not set
            min_length=1,
            max_length=500,
        )

    # Load registry configuration with safe type conversion
    config.REGISTRY_ENABLED = safe_bool_parameter('HOME_ASSISTANT_REGISTRY_ENABLED', True)
    config.REGISTRY_TIMEOUT = safe_int_parameter('HOME_ASSISTANT_REGISTRY_TIMEOUT', 30, min_val=1, max_val=300)

    # Load WebSocket configuration with safe type conversion
    config.WEBSOCKET_POOL_SIZE = safe_int_parameter('WEBSOCKET_POOL_SIZE', 5, min_val=1, max_val=50)
    config.WEBSOCKET_IDLE_TIMEOUT = safe_int_parameter('WEBSOCKET_IDLE_TIMEOUT', 300, min_val=60, max_val=3600)
    config.WEBSOCKET_CONNECTION_TIMEOUT = safe_int_parameter('HOME_ASSISTANT_WEBSOCKET_TIMEOUT', 10, min_val=1, max_val=120)

    # Validate configuration
    if not _validate_and_log_config(config, 'environment'):
        return None

    return config


def _load_from_dotenv() -> Optional[HAConfig]:
    """
    Load configuration from .env file.

    Returns:
        HAConfig: Configuration object if .env found, None otherwise
    """
    # pylint: disable=import-outside-toplevel
    try:
        from dotenv import find_dotenv, load_dotenv

        # Find .env file in current directory or parent directories
        env_path = find_dotenv(usecwd=True)

        if not env_path:
            # No .env file found
            return None

        # Load the .env file
        loaded = load_dotenv(env_path, override=True)

        if not loaded:
            return None

        config = HAConfig(source='config_file')

        # Load from environment (now populated by dotenv) with validation
        config.HOME_ASSISTANT_URL = safe_str_parameter(
            'HOME_ASSISTANT_URL',
            '',  # Empty default - will return None if not set
            min_length=10,
            max_length=2000,
        )
        config.HOME_ASSISTANT_API_KEY = safe_str_parameter(
            'HOME_ASSISTANT_API_KEY',
            '',  # Empty default - will return None if not set
            min_length=1,
            max_length=500,
        )

        # Load registry configuration with safe type conversion
        config.REGISTRY_ENABLED = safe_bool_parameter('HOME_ASSISTANT_REGISTRY_ENABLED', True)
        config.REGISTRY_TIMEOUT = safe_int_parameter('HOME_ASSISTANT_REGISTRY_TIMEOUT', 30, min_val=1, max_val=300)

        # Load WebSocket configuration with safe type conversion
        config.WEBSOCKET_POOL_SIZE = safe_int_parameter('WEBSOCKET_POOL_SIZE', 5, min_val=1, max_val=50)
        config.WEBSOCKET_IDLE_TIMEOUT = safe_int_parameter('WEBSOCKET_IDLE_TIMEOUT', 300, min_val=60, max_val=3600)
        config.WEBSOCKET_CONNECTION_TIMEOUT = safe_int_parameter('HOME_ASSISTANT_WEBSOCKET_TIMEOUT', 10, min_val=1, max_val=120)

        # Validate configuration
        if not _validate_and_log_config(config, '.env file'):
            return None

        return config

    except ImportError as e:
        # python-dotenv not available, log and return None to fall back to next source
        try:
            execute_operation(GatewayInterface.LOGGING, "log_warning",
                             message="python-dotenv not available for HA config loading",
                             error=str(e))
        except (KeyError, AttributeError, RuntimeError):
            # Gateway unavailable - logging is optional
            pass
        return None
    except (OSError, ValueError) as e:
        # Error loading .env file, log and return None to fall back to next source
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message="Failed to load HA configuration from .env file",
                             error=str(e), error_type=type(e).__name__)
        except (KeyError, AttributeError, RuntimeError):
            # Gateway unavailable - logging is optional
            pass
        return None


def _load_from_parameter_store() -> Optional[HAConfig]:
    """
    Load configuration from AWS SSM Parameter Store (Lambda only).

    Returns:
        HAConfig: Configuration object if parameters found, None otherwise
    """
    # pylint: disable=import-outside-toplevel
    from lee.home_assistant.ha_deployment_mode import is_lambda_mode

    # Only available in Lambda mode
    if not is_lambda_mode():
        return None

    try:
        import boto3

        config = HAConfig(source='parameter_store')

        # Initialize SSM client
        ssm = boto3.client('ssm')

        # Get parameters
        response = ssm.get_parameters(
            Names=[
                '/lee/home_assistant_url',
                '/lee/home_assistant_token'
            ],
            WithDecryption=True
        )

        # Extract parameters with sanitization
        parameters = {param['Name']: param['Value'] for param in response.get('Parameters', [])}

        sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
        config.HOME_ASSISTANT_URL = sanitizer.sanitize_url(parameters.get('/lee/home_assistant_url'))
        config.HOME_ASSISTANT_API_KEY = sanitizer.sanitize_token(parameters.get('/lee/home_assistant_token'))

        # Return config even if empty - caller will decide whether to use it
        return config

    except (ImportError, OSError, ValueError) as e:
        # Error accessing Parameter Store - log and return None to fall back
        try:
            execute_operation(GatewayInterface.LOGGING, "log_warning",
                             message="Failed to load HA configuration from AWS SSM Parameter Store",
                             error=str(e), error_type=type(e).__name__)
        except (KeyError, AttributeError, RuntimeError):
            # Gateway unavailable - logging is optional
            pass
        return None


def _load_defaults() -> HAConfig:
    """
    Load default configuration values.

    Returns:
        HAConfig: Configuration object with default values

    Note:
        All defaults come from environment variables. No hard-coded values.
        Configuration should be set via environment variables or .env file.
    """
    config = HAConfig(source='defaults')

    # Load from environment variables with validation
    # HA_DEFAULT_URL and HA_DEFAULT_TOKEN are optional fallbacks
    config.HOME_ASSISTANT_URL = safe_str_parameter(
        'HA_DEFAULT_URL',
        '',  # Empty default - no hard-coded URL
        min_length=10,
        max_length=2000,
    )
    config.HOME_ASSISTANT_API_KEY = safe_str_parameter(
        'HA_DEFAULT_TOKEN',
        '',  # Empty default - no hard-coded token
        min_length=1,
        max_length=500,
    )

    return config
