"""
Object Pool Interface - Operations Domain

Generic object pooling for resource management.

Merges functionality from:
- EE/src/operations/object_pool/
- EE/src/object_pool/
"""

from EE.operations.object_pool.object_pool_interface import execute_object_pool_operation
from EE.operations.object_pool.object_pool_factory import (
    ObjectPoolFactory,
    ObjectPool,
    PoolConfig,
    PoolEntry,
    PoolStats
)

__all__ = [
    'execute_object_pool_operation',
    'ObjectPoolFactory',
    'ObjectPool',
    'PoolConfig',
    'PoolEntry',
    'PoolStats',
]
