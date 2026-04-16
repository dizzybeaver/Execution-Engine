"""singleton/singleton_manager.py
Version: 2025.12.13.01
Purpose: Singleton instance manager with rate limiting (thread-safe)
License: Apache 2.0

Thread Safety Fix (2026-04-09):
- Added threading.Lock with double-checked locking pattern
- Lambda CAN have concurrent executions (AP-08 was incorrect)
- Fast path: check without lock (read-only, safe in Python)
- Slow path: acquire lock only when initialization needed
"""

import threading

# Import extracted SingletonCore class
from lee.singleton.classes.SingletonCore import SingletonCore

# Import enums for backward compatibility
from lee.singleton.enums.SingletonOperation import SingletonOperation

# SINGLETON pattern (LESS-18) with thread-safe initialization
# Lambda CAN have concurrent executions - lock required (2026-04-09 fix)
_manager_core = None
_manager_lock = threading.Lock()


def get_singleton_manager() -> SingletonCore:
    """Get the singleton manager instance (SINGLETON pattern) with thread-safe lazy initialization.

    Ironic: SINGLETON interface using SINGLETON pattern for itself!

    Uses module-level singleton to avoid circular reference through gateway.
    Thread-safe: Uses double-checked locking for Lambda concurrent execution.

    Returns:
        SingletonCore instance

    """
    # pylint: disable=global-statement
    global _manager_core

    # Fast path: check without lock (read-only, safe in Python)
    if _manager_core is not None:
        return _manager_core

    # Slow path: acquire lock for initialization
    with _manager_lock:
        # Double-check: another thread may have initialized while we waited
        if _manager_core is not None:
            return _manager_core

        # Initialize singleton
        _manager_core = SingletonCore()

    return _manager_core


__all__ = [
    "SingletonCore",
    "SingletonOperation",
    "get_singleton_manager",
]
