"""
DI Interface - Foundation Domain

Dependency injection container and AOP support.

UG-ISP Compliant:
- Interface uses DISPATCH dictionary pattern
- Factory contains actual implementation
- Cross-domain calls via call_operation callback
"""

from EE.foundation.di.di_interface import DIInterface

__all__ = [
    "DIInterface",
]
