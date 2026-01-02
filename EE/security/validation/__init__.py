"""
Validation Interface - Security Domain

Provides input validation and sanitization operations.
"""

from EE.security.validation.validation_interface import execute_validation_operation
from EE.security.validation.validation_factory import ValidationFactory

__all__ = [
    'execute_validation_operation',
    'ValidationFactory',
]
