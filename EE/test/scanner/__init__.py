"""
Scanner Test Interface - Test Domain

Provides scanner test operations.

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
"""

from __future__ import annotations
from EE.test.scanner.scanner_test_interface import create_scanner_test_interface

__all__ = [
    'create_scanner_test_interface',
]
