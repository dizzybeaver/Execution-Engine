"""
Singleton Interface - Foundation Domain

Instance management and memory tracking.

UG-ISP Compliant:
- Interface uses DISPATCH dictionary pattern
- Factory contains actual implementation
- Cross-domain calls via call_operation callback
"""

from EE.foundation.singleton.singleton_interface import SingletonInterface

__all__ = [
    "SingletonInterface",
]
