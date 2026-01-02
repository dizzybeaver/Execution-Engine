"""
Cache Interface - Operations Domain

Caching operations with LRU eviction.
"""

from EE.operations.cache.cache_interface import execute_cache_operation
from EE.operations.cache.cache_factory import CacheFactory

__all__ = [
    'execute_cache_operation',
    'CacheFactory',
]
