"""
singleton/__init__.py
Version: 2025-12-13_1
Purpose: Singleton module initialization
License: Apache 2.0
"""

from singleton.singleton_manager import (
    SingletonOperation,
    SingletonCore,
    get_singleton_manager
)
from singleton.singleton_core import (
    execute_singleton_operation,
    get_implementation,
    set_implementation,
    has_implementation,
    delete_implementation,
    clear_implementation,
    get_stats_implementation,
    reset_implementation
)

__all__ = [
    'SingletonOperation',
    'SingletonCore',
    'get_singleton_manager',
    'execute_singleton_operation',
    'get_implementation',
    'set_implementation',
    'has_implementation',
    'delete_implementation',
    'clear_implementation',
    'get_stats_implementation',
    'reset_implementation',
]
