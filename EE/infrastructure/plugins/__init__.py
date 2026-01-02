"""
Plugins Interface - Infrastructure Domain

Provides plugin loading and management operations.

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
"""

from __future__ import annotations
from EE.infrastructure.plugins.plugins_interface import create_plugins_interface

__all__ = [
    'create_plugins_interface',
]
