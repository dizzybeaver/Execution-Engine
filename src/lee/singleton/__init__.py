"""Singleton management infrastructure for LEE."""

# Thread-safe singleton base class
# Classes
from lee.singleton.classes.SingletonCore import SingletonCore

# Enums
from lee.singleton.enums.SingletonOperation import SingletonOperation

# Convenience functions
from lee.singleton.functions.convenience.clear_all_singletons import (
    clear_all_singletons,
)
from lee.singleton.functions.convenience.delete_singleton import delete_singleton
from lee.singleton.functions.convenience.get_cache_manager import get_cache_manager
from lee.singleton.functions.convenience.get_circuit_breaker_manager import (
    get_circuit_breaker_manager,
)
from lee.singleton.functions.convenience.get_config_manager import get_config_manager
from lee.singleton.functions.convenience.get_cost_protection import get_cost_protection
from lee.singleton.functions.convenience.get_lambda_cache import get_lambda_cache
from lee.singleton.functions.convenience.get_lambda_optimizer import (
    get_lambda_optimizer,
)
from lee.singleton.functions.convenience.get_memory_manager import get_memory_manager
from lee.singleton.functions.convenience.get_named_singleton import get_named_singleton
from lee.singleton.functions.convenience.get_response_cache import get_response_cache
from lee.singleton.functions.convenience.get_response_metrics_manager import (
    get_response_metrics_manager,
)
from lee.singleton.functions.convenience.get_response_processor import (
    get_response_processor,
)
from lee.singleton.functions.convenience.get_security_validator import (
    get_security_validator,
)
from lee.singleton.functions.convenience.get_singleton_stats import get_singleton_stats
from lee.singleton.functions.convenience.get_unified_validator import (
    get_unified_validator,
)
from lee.singleton.functions.convenience.has_singleton import has_singleton

# Memory functions
from lee.singleton.functions.memory.check_lambda_memory_compliance import (
    check_lambda_memory_compliance,
)
from lee.singleton.functions.memory.emergency_memory_preserve import (
    emergency_memory_preserve,
)
from lee.singleton.functions.memory.force_comprehensive_memory_cleanup import (
    force_comprehensive_memory_cleanup,
)
from lee.singleton.functions.memory.force_memory_cleanup import force_memory_cleanup
from lee.singleton.functions.memory.get_comprehensive_memory_stats import (
    get_comprehensive_memory_stats,
)
from lee.singleton.functions.memory.get_memory_stats import get_memory_stats
from lee.singleton.functions.memory.get_singleton_memory_status_implementation import (
    _get_singleton_memory_status_implementation as get_singleton_memory_status_implementation,
)
from lee.singleton.functions.memory.optimize_memory import optimize_memory

# Singleton management functions
from lee.singleton.functions.singleton_management.clear_implementation import (
    clear_implementation,
)
from lee.singleton.functions.singleton_management.delete_implementation import (
    delete_implementation,
)
from lee.singleton.functions.singleton_management.execute_singleton_operation import (
    execute_singleton_operation,
)
from lee.singleton.functions.singleton_management.get_implementation import (
    get_implementation,
)
from lee.singleton.functions.singleton_management.get_stats_implementation import (
    get_stats_implementation,
)
from lee.singleton.functions.singleton_management.has_implementation import (
    has_implementation,
)
from lee.singleton.functions.singleton_management.reset_implementation import (
    reset_implementation,
)
from lee.singleton.functions.singleton_management.set_implementation import (
    set_implementation,
)
from lee.singleton.thread_safe_singleton import (
    SingletonFactory,
    ThreadSafeSingleton,
    singleton,
)

__all__ = [
    # Thread-safe singleton base class
    "ThreadSafeSingleton",
    "SingletonFactory",
    "singleton",
    # Memory functions
    "check_lambda_memory_compliance",
    "emergency_memory_preserve",
    "force_comprehensive_memory_cleanup",
    "force_memory_cleanup",
    "get_comprehensive_memory_stats",
    "get_memory_stats",
    "get_singleton_memory_status_implementation",
    "optimize_memory",
    # Convenience functions
    "clear_all_singletons",
    "delete_singleton",
    "get_cache_manager",
    "get_circuit_breaker_manager",
    "get_config_manager",
    "get_cost_protection",
    "get_lambda_cache",
    "get_lambda_optimizer",
    "get_memory_manager",
    "get_named_singleton",
    "get_response_cache",
    "get_response_metrics_manager",
    "get_response_processor",
    "get_security_validator",
    "get_singleton_stats",
    "get_unified_validator",
    "has_singleton",
    # Singleton management functions
    "clear_implementation",
    "delete_implementation",
    "execute_singleton_operation",
    "get_implementation",
    "get_stats_implementation",
    "has_implementation",
    "reset_implementation",
    "set_implementation",
    # Classes
    "SingletonCore",
    # Enums
    "SingletonOperation",
]
