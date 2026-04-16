# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-08 - Added _is_debug_mode, replaced print statements with gateway debug calls

"""config/config_parameters.py
Version: 2025-12-09_1
Purpose: Configuration parameter operations with SSM-first priority
License: Apache 2.0
"""

import os
import time
import uuid
from contextlib import nullcontext
from typing import Any, Optional

# Cache environment variable at module load time
# For AWS Lambda: Read from environment variable set by Lambda configuration
# For local testing: .env file should set this via environment variable
_USE_PARAMETER_STORE_FLAG = os.getenv("USE_PARAMETER_STORE", "false").lower() == "true"

# Cache debug mode check at module load time
_DEBUG_MODE_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled (cached value)."""
    return _DEBUG_MODE_ENABLED


def _get_gateway():
    """Lazy import gateway to avoid circular dependency."""
    from lee.gateway import GatewayInterface, execute_operation
    return GatewayInterface, execute_operation


def _debug_log(**kwargs):
    """Helper for debug logging with lazy import."""
    if not _is_debug_mode():
        return
    try:
        GatewayInterface, execute_operation = _get_gateway()
        execute_operation(GatewayInterface.DEBUG, "log", **kwargs)
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Optional dependency - continue if unavailable
        pass


def _debug_log_warning(**kwargs):
    """Helper for warning logging with lazy import."""
    if not _is_debug_mode():
        return
    try:
        GatewayInterface, execute_operation = _get_gateway()
        execute_operation(GatewayInterface.LOGGING, "log_warning", **kwargs)
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Optional dependency - continue if unavailable
        pass


def _debug_log_error(**kwargs):
    """Helper for error logging with lazy import."""
    try:
        GatewayInterface, execute_operation = _get_gateway()
        execute_operation(GatewayInterface.LOGGING, "log_error", **kwargs)
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Optional dependency - continue if unavailable
        pass


def initialize_config() -> dict[str, Any]:
    """Initialize configuration system."""
    if _is_debug_mode():
        start_time = time.perf_counter()
        _debug_log(message="initialize_config ENTRY",
                  scope="CONFIG",
                  use_parameter_store=_USE_PARAMETER_STORE_FLAG)

    # SUGA-ISP compliant correlation ID generation (local implementation)
    corr_id = f"cfg_{uuid.uuid4().hex[:12]}"

    # Get config manager through gateway pattern
    try:
        GatewayInterface, execute_operation = _get_gateway()
        manager = execute_operation(GatewayInterface.CONFIG, 'get_config_manager')
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Fallback to direct import if gateway unavailable
        from lee.lee_config.config_generic import get_config_manager
        manager = get_config_manager()

    try:
        # SUGA-ISP compliant timing
        try:
            GatewayInterface, execute_operation = _get_gateway()
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=corr_id, scope="CONFIG",
                                         operation="initialize")
        except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
            timing_ctx = nullcontext()

        with timing_ctx:
            # Check USE_PARAMETER_STORE flag (cached at module level)
            # For AWS Lambda: Read from environment variable set by Lambda configuration
            # For local testing: .env file should set this via environment variable
            manager._use_parameter_store = _USE_PARAMETER_STORE_FLAG

            _debug_log(corr_id=corr_id, scope="CONFIG",
                      message="Initializing config",
                      use_ssm=_USE_PARAMETER_STORE_FLAG,
                      prefix=manager._parameter_prefix)

            # Load environment config
            from lee.lee_config.config_loader import load_from_environment
            env_config = load_from_environment()
            manager._config.update(env_config)

            manager._initialized = True

            result = {
                "success": True,
                "use_parameter_store": _USE_PARAMETER_STORE_FLAG,
                "parameter_count": len(manager._config),
            }

            if _is_debug_mode():
                duration_ms = (time.perf_counter() - start_time) * 1000
                _debug_log(message="initialize_config EXIT",
                          scope="CONFIG",
                          parameter_count=len(manager._config),
                          duration_ms=f"{duration_ms:.2f}")

            return result

    except (ValueError, TypeError, KeyError, AttributeError, ImportError, OSError) as init_error:
        _debug_log_error(message=f"Config initialization failed: {init_error}",
                        error_type=type(init_error).__name__)
        return {"success": False, "error": str(init_error)}


def get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter with SSM-first priority.

    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. Environment variable
    3. Default value
    """
    if _is_debug_mode():
        start_time = time.perf_counter()
        _debug_log(message="get_parameter ENTRY",
                  scope="CONFIG",
                  key=key,
                  default=default)

    # SUGA-ISP compliant correlation ID generation (local implementation)
    corr_id = f"cfg_{uuid.uuid4().hex[:12]}"

    # Get config manager through gateway pattern
    try:
        GatewayInterface, execute_operation = _get_gateway()
        manager = execute_operation(GatewayInterface.CONFIG, 'get_config_manager')
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Fallback to direct import if gateway unavailable
        from lee.lee_config.config_generic import get_config_manager
        manager = get_config_manager()

    if manager._check_rate_limit():
        _debug_log_warning(message=f"Config get_parameter rate limited: {key}")
        return default

    _debug_log(corr_id=corr_id, scope="CONFIG",
              message="Getting parameter", key=key)

    # Check cache first
    if key in manager._config:
        value = manager._config[key]
        if value is not None:
            if _is_debug_mode():
                duration_ms = (time.perf_counter() - start_time) * 1000
                _debug_log(message="get_parameter EXIT",
                          scope="CONFIG",
                          key=key,
                          source="cache",
                          duration_ms=f"{duration_ms:.2f}")
            _debug_log(corr_id=corr_id, scope="CONFIG",
                      message="Cache hit", key=key)
            return value

    # SSM Parameter Store (if enabled)
    if manager._use_parameter_store:
        try:
            ssm_key = f"{manager._parameter_prefix}/{key}"
            _debug_log(corr_id=corr_id, scope="CONFIG",
                      message="Checking SSM", ssm_key=ssm_key)

            value = _get_ssm_parameter(ssm_key)
            if value is not None:
                manager._config[key] = value
                if _is_debug_mode():
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    _debug_log(message="get_parameter EXIT",
                              scope="CONFIG",
                              key=key,
                              source="ssm",
                              duration_ms=f"{duration_ms:.2f}")
                _debug_log(corr_id=corr_id, scope="CONFIG",
                          message="SSM hit", key=key)
                return value

        except (ConnectionError, TimeoutError, OSError, KeyError, ValueError, TypeError, ImportError, RuntimeError) as ssm_error:
            _debug_log_warning(message=f"SSM get failed for {key}: {ssm_error}",
                              error_type=type(ssm_error).__name__)

    # Environment variable fallback
    env_value = os.getenv(key)
    if env_value is not None:
        manager._config[key] = env_value
        if _is_debug_mode():
            duration_ms = (time.perf_counter() - start_time) * 1000
            _debug_log(message="get_parameter EXIT",
                      scope="CONFIG",
                      key=key,
                      source="env",
                      duration_ms=f"{duration_ms:.2f}")
        _debug_log(corr_id=corr_id, scope="CONFIG",
                  message="Environment hit", key=key)
        return env_value

    # Default value
    if _is_debug_mode():
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_log(message="get_parameter EXIT",
                  scope="CONFIG",
                  key=key,
                  source="default",
                  duration_ms=f"{duration_ms:.2f}")
    _debug_log(corr_id=corr_id, scope="CONFIG",
              message="Using default", key=key, default=default)
    return default


def set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    if _is_debug_mode():
        start_time = time.perf_counter()
        _debug_log(message="set_parameter ENTRY",
                  scope="CONFIG",
                  key=key,
                  value_type=type(value).__name__)

    # SUGA-ISP compliant correlation ID generation (local implementation)
    corr_id = f"cfg_{uuid.uuid4().hex[:12]}"

    # Get config manager through gateway pattern
    try:
        GatewayInterface, execute_operation = _get_gateway()
        manager = execute_operation(GatewayInterface.CONFIG, 'get_config_manager')
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Fallback to direct import if gateway unavailable
        from lee.lee_config.config_generic import get_config_manager
        manager = get_config_manager()

    if manager._check_rate_limit():
        _debug_log_warning(message=f"Config set_parameter rate limited: {key}")
        return False

    try:
        # SUGA-ISP compliant timing
        if _is_debug_mode():
            try:
                GatewayInterface, execute_operation = _get_gateway()
                timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                             corr_id=corr_id, scope="CONFIG",
                                             operation="set_parameter")
            except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
                timing_ctx = nullcontext()
        else:
            timing_ctx = nullcontext()

        with timing_ctx:
            _debug_log(corr_id=corr_id, scope="CONFIG",
                      message="Setting parameter",
                      key=key, value_type=type(value).__name__)

            manager._config[key] = value
            if _is_debug_mode():
                duration_ms = (time.perf_counter() - start_time) * 1000
                _debug_log(message="set_parameter EXIT",
                          scope="CONFIG",
                          key=key,
                          success=True,
                          duration_ms=f"{duration_ms:.2f}")
            return True

    except (ValueError, TypeError, KeyError, AttributeError, OSError) as set_error:
        _debug_log_error(message=f"Config set_parameter failed for {key}: {set_error}",
                        error_type=type(set_error).__name__)
        return False


def get_category_config(category: str) -> dict[str, Any]:
    """Get configuration for a category."""
    if _is_debug_mode():
        start_time = time.perf_counter()
        _debug_log(message="get_category_config ENTRY",
                  scope="CONFIG",
                  category=category)

    # SUGA-ISP compliant correlation ID generation (local implementation)
    corr_id = f"cfg_{uuid.uuid4().hex[:12]}"

    # Get config manager through gateway pattern
    try:
        GatewayInterface, execute_operation = _get_gateway()
        manager = execute_operation(GatewayInterface.CONFIG, 'get_config_manager')
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Fallback to direct import if gateway unavailable
        from lee.lee_config.config_generic import get_config_manager
        manager = get_config_manager()

    _debug_log(corr_id=corr_id, scope="CONFIG",
              message="Getting category config", category=category)

    # Filter config keys by category prefix
    category_config = {}
    prefix = f"{category}."

    for key, value in manager._config.items():
        if key.startswith(prefix):
            # Remove category prefix from key
            short_key = key[len(prefix):]
            category_config[short_key] = value

    _debug_log(corr_id=corr_id, scope="CONFIG",
              message="Category config retrieved",
              category=category, key_count=len(category_config))

    if _is_debug_mode():
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_log(message="get_category_config EXIT",
                  scope="CONFIG",
                  category=category,
                  key_count=len(category_config),
                  duration_ms=f"{duration_ms:.2f}")

    return category_config


def get_state() -> dict[str, Any]:
    """Get configuration state."""
    # Get config manager through gateway pattern
    try:
        GatewayInterface, execute_operation = _get_gateway()
        manager = execute_operation(GatewayInterface.CONFIG, 'get_config_manager')
    except (ImportError, RuntimeError, TypeError, KeyError, AttributeError, ValueError, OSError):
        # Fallback to direct import if gateway unavailable
        from lee.lee_config.config_generic import get_config_manager
        manager = get_config_manager()

    return {
        "initialized": manager._initialized,
        "use_parameter_store": manager._use_parameter_store,
        "parameter_prefix": manager._parameter_prefix,
        "config_keys": list(manager._config.keys()),
        "rate_limited_count": manager._rate_limited_count,
    }


def _get_ssm_parameter(key: str) -> Optional[Any]:
    """Get parameter from SSM Parameter Store."""
    try:
        import boto3
        ssm_client = boto3.client("ssm")

        response = ssm_client.get_parameter(
            Name=key,
            WithDecryption=True,
        )

        return response["Parameter"]["Value"]

    except (KeyError, ImportError, ConnectionError, RuntimeError, ValueError, TypeError, AttributeError, OSError):
        return None


__all__ = [
    "get_category_config",
    "get_parameter",
    "get_state",
    "initialize_config",
    "set_parameter",
]
