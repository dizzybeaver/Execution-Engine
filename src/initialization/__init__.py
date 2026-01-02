"""
initialization/__init__.py
Version: 2025-12-13_1
Purpose: Initialization module initialization
License: Apache 2.0
"""

from initialization.initialization_manager import (
    InitializationOperation,
    InitializationCore,
    get_initialization_manager
)
from initialization.initialization_core import (
    execute_initialization_operation,
    initialize_implementation,
    get_config_implementation,
    is_initialized_implementation,
    reset_implementation,
    get_status_implementation,
    get_stats_implementation,
    set_flag_implementation,
    get_flag_implementation
)

__all__ = [
    'InitializationOperation',
    'InitializationCore',
    'get_initialization_manager',
    'execute_initialization_operation',
    'initialize_implementation',
    'get_config_implementation',
    'is_initialized_implementation',
    'reset_implementation',
    'get_status_implementation',
    'get_stats_implementation',
    'set_flag_implementation',
    'get_flag_implementation',
]
