"""
cache/cache_enums.py
Version: 2025-12-08_1
Purpose: Cache enums, types, and constants
License: Apache 2.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Configuration constants
DEFAULT_CACHE_TTL = 300  # 5 minutes default TTL
MAX_CACHE_BYTES = 100 * 1024 * 1024  # 100MB limit
RATE_LIMIT_WINDOW_MS = 1000  # 1 second window
RATE_LIMIT_MAX_OPS = 1000  # Max operations per window


class _CacheMiss:
    """Sentinel value for cache misses."""
    def __repr__(self):
        return '<CACHE_MISS>'


# Singleton sentinel instance
_CACHE_MISS = _CacheMiss()


class CacheOperation(str, Enum):
    """Cache operation types for metrics."""
    GET = 'get'
    SET = 'set'
    DELETE = 'delete'
    CLEAR = 'clear'
    CLEANUP = 'cleanup'


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    source_module: Optional[str]
    access_count: int
    last_access: float
    value_size_bytes: int


__all__ = [
    'DEFAULT_CACHE_TTL',
    'MAX_CACHE_BYTES',
    'RATE_LIMIT_WINDOW_MS',
    'RATE_LIMIT_MAX_OPS',
    '_CacheMiss',
    '_CACHE_MISS',
    'CacheOperation',
    'CacheEntry',
]

# EOF
