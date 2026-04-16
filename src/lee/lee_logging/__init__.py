"""logging/__init__.py
Version: 2025-12-13_1
Purpose: Logging interface module initialization
License: Apache 2.0

Module Structure:
- logging_types.py - Type definitions and enums
- logging_manager.py - LoggingCore class with singleton
- logging_generic.py - Core implementation functions (PRIVATE)
- logging_operations.py - Operation dispatcher

Import Pattern:
- Public API: Use execute_logging_operation() via interface
- Internal use: Private _execute_* functions available for interface_logging.py
"""

# Private implementation functions - NOT exported in __all__
# Available for internal use by interface_logging.py
from lee.lee_logging.logging_generic import (  # noqa: F401
    _execute_log_critical_implementation,
    _execute_log_debug_implementation,
    _execute_log_error_implementation,
    _execute_log_info_implementation,
    _execute_log_operation_failure_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_reset_implementation,
    _execute_log_warning_implementation,
)
from lee.lee_logging.logging_manager import (
    LoggingCore,
    RateLimitTracker,
    get_logging_core,
)
from lee.lee_logging.logging_operations import (
    execute_logging_operation,
)
from lee.lee_logging.logging_types import (
    ErrorEntry,
    ErrorLogEntry,
    ErrorLogLevel,
    LogOperation,
    LogTemplate,
)

__all__ = [
    # Types
    "LogOperation",
    "LogTemplate",
    "ErrorLogLevel",
    "ErrorEntry",
    "ErrorLogEntry",

    # Manager
    "LoggingCore",
    "get_logging_core",
    "RateLimitTracker",

    # Public Operations
    "execute_logging_operation",
]

__version__ = "2025-12-13_1"
