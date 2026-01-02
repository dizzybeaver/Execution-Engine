"""
Initialization Interface - Foundation Domain

System bootstrap and initialization.

UG-ISP Compliant:
- Interface uses DISPATCH dictionary pattern
- Factory contains actual implementation
"""

from EE.foundation.initialization.initialization_interface import InitializationInterface

__all__ = [
    "InitializationInterface",
]
