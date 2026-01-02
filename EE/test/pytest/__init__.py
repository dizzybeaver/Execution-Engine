"""
Pytest Interface - Test Domain

Provides pytest-based testing operations.

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
"""

from __future__ import annotations
from EE.testtest.pytest_interface import create_pytest_interface

__all__ = [
    'create_pytest_interface',
]
