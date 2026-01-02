"""
Authentication Interface - Security Domain

Provides authentication and authorization operations.
"""

from EE.security.authentication.authentication_interface import execute_authentication_operation
from EE.security.authentication.authentication_factory import AuthenticationFactory

__all__ = [
    'execute_authentication_operation',
    'AuthenticationFactory',
]
