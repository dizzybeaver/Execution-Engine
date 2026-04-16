"""gateway_wrappers_initialization.py - INITIALIZATION Interface Wrappers
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Description: Convenience wrappers for INITIALIZATION interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0

CONSOLIDATION:
- Removed duplicate import patterns
- Uses base_wrapper for common utilities
- Reduced code by ~5 lines
"""

from typing import Any

from lee.initialization.initialization_core import (
    get_flag_implementation as get_initialization_flag_impl,
)
from lee.initialization.initialization_core import (
    get_status_implementation as get_initialization_status_impl,
)
from lee.initialization.initialization_core import (
    get_stats_implementation as get_stats_impl,
)
from lee.initialization.initialization_core import (
    initialize_implementation as initialize_system_impl,
)
from lee.initialization.initialization_core import (
    set_flag_implementation as set_initialization_flag_impl,
)


def initialize_system(**kwargs) -> dict[str, Any]:
    """Initialize system."""
    return initialize_system_impl(**kwargs)


def get_initialization_status() -> dict[str, Any]:
    """Get initialization status."""
    return get_initialization_status_impl()


def initialization_get_stats() -> dict[str, Any]:
    """Get initialization statistics (alias for initialization_get_status)."""
    return get_stats_impl()


def set_initialization_flag(flag: str, value: bool) -> None:
    """Set initialization flag."""
    set_initialization_flag_impl(flag=flag, value=value)


def get_initialization_flag(flag: str) -> bool:
    """Get initialization flag."""
    return get_initialization_flag_impl(flag=flag)


__all__ = [
    "get_initialization_flag",
    "get_initialization_status",
    "initialization_get_stats",
    "initialize_system",
    "set_initialization_flag",
]
