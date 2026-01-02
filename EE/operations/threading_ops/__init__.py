"""
Threading Interface - Operations Domain

Thread pool management and concurrent execution.

Migrated from EE/src/infrastructure/threading/
"""

from EE.operations.threading_ops.threading_interface import execute_threading_operation
from EE.operations.threading_ops.threading_factory import ThreadingFactory

__all__ = [
    'execute_threading_operation',
    'ThreadingFactory',
]
