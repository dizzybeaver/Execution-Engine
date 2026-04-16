"""circuit_breaker/__init__.py
Version: 2025-12-13_1
Enhanced: 2026-03-04 (Config system exports)
Updated: 2026-03-28 (CBFuse system exports)
Updated: 2026-03-28 (LoggingFuse health exports)
Purpose: Circuit breaker module initialization
License: Apache 2.0
"""

from .circuit_breaker_config import (
    CircuitBreakerConfig,
    get_alexa_cache_l2_config,
    get_alexa_ha_api_config,
    get_alexa_oauth_config,
    get_alexa_websocket_config,
    get_default_config,
)

# Import CBFuse-enabled CircuitBreaker (replaces legacy)
from .circuit_breaker_core import CircuitBreaker
from .circuit_breaker_manager import (
    CircuitBreakerCore,
    execute_with_breaker_implementation,
    get_all_states_implementation,
    get_breaker_implementation,
    get_circuit_breaker_manager,
    get_stats_implementation,
    reset_all_implementation,
    reset_implementation,
)
from .circuit_breaker_state import (
    CircuitState,
    FailureRecord,
)

# Import LoggingFuse for simple failure tracking
from .logging_fuse import LoggingFuse

# Import LoggingFuse health reporting
from .logging_fuse_health import (
    get_all_logging_fuses,
    get_logging_fuse_health,
)

__all__ = [
    # Core classes
    "CircuitState",
    "CircuitBreaker",
    "FailureRecord",
    "CircuitBreakerCore",
    "get_circuit_breaker_manager",
    # Configuration system (NEW)
    "CircuitBreakerConfig",
    "get_default_config",
    "get_alexa_ha_api_config",
    "get_alexa_oauth_config",
    "get_alexa_websocket_config",
    "get_alexa_cache_l2_config",
    # Gateway implementations
    "get_breaker_implementation",
    "execute_with_breaker_implementation",
    "get_all_states_implementation",
    "reset_all_implementation",
    "get_stats_implementation",
    "reset_implementation",
    # Simple failure tracking
    "LoggingFuse",
    # LoggingFuse health reporting
    "get_all_logging_fuses",
    "get_logging_fuse_health",
]
