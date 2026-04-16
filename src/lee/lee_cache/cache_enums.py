"""cache/cache_enums.py
Version: 2025-12-08_1
Purpose: Cache enums, types, and constants
License: Apache 2.0
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional

from lee.lee_config.variables import (
    CACHE_DEFAULT_TTL_SECONDS,
    CACHE_MAX_BYTES,
)


class CacheError(Exception):
    """Base exception for cache operations."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            return f"{super().__str__()} (caused by: {type(self.original_exception).__name__}: {self.original_exception})"
        return super().__str__()


# Configuration constants
DEFAULT_CACHE_TTL = CACHE_DEFAULT_TTL_SECONDS  # 5 minutes default TTL
MAX_CACHE_BYTES = CACHE_MAX_BYTES  # 100MB limit
RATE_LIMIT_WINDOW_MS = 1000  # 1 second window
RATE_LIMIT_MAX_OPS = 1000  # Max operations per window


class _CacheMiss:
    """Sentinel value for cache misses."""

    def __repr__(self):
        return "<CACHE_MISS>"


# Singleton sentinel instance
_CACHE_MISS = _CacheMiss()


class CacheOperation(StrEnum):
    """Cache operation types for metrics."""

    GET = "get"
    SET = "set"
    DELETE = "delete"
    CLEAR = "clear"
    CLEANUP = "cleanup"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    # pylint: disable=too-many-instance-attributes
    __slots__ = ['value', 'timestamp', 'ttl', 'source_module', 'access_count',
                  'last_access', 'value_size_bytes', 'compression_metadata']

    value: Any
    timestamp: float
    ttl: int
    source_module: Optional[str]
    access_count: int
    last_access: float
    value_size_bytes: int
    compression_metadata: Optional[Any]


__all__ = [
    "DEFAULT_CACHE_TTL",
    "MAX_CACHE_BYTES",
    "RATE_LIMIT_MAX_OPS",
    "RATE_LIMIT_WINDOW_MS",
    "_CACHE_MISS",
    "CacheEntry",
    "CacheError",
    "CacheOperation",
    "_CacheMiss",
]

# EOF
