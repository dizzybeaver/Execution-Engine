"""singleton_generic.py - Compatibility shim for refactored singleton functions.

This module provides backward compatibility by re-exporting generic singleton operations
from their new locations in the functions/ subdirectory.

The singleton module has been refactored to move individual operations into
separate files in singleton/functions/singleton_management/. This shim maintains
backward compatibility for existing imports.
"""

# Re-export all generic singleton operations
from lee.singleton.functions.singleton_management.clear_implementation import (
    clear_implementation,
)
from lee.singleton.functions.singleton_management.delete_implementation import (
    delete_implementation,
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

__all__ = [
    "get_implementation",
    "set_implementation",
    "has_implementation",
    "delete_implementation",
    "clear_implementation",
    "get_stats_implementation",
    "reset_implementation",
]
