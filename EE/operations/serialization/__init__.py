"""
Serialization Interface - Operations Domain

Data serialization (JSON, pickle, etc.).
"""

from EE.operations.serialization.serialization_interface import execute_serialization_operation
from EE.operations.serialization.serialization_factory import SerializationFactory

__all__ = [
    'execute_serialization_operation',
    'SerializationFactory',
]
