"""
Debug Interface - Observability Domain

Debug logging, correlation tracking, and diagnostics.
"""

from EE.observability.debug.debug_interface import execute_debug_operation
from EE.observability.debug.debug_factory import DebugFactory

__all__ = [
    'execute_debug_operation',
    'DebugFactory',
]
