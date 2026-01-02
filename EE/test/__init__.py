"""
Test Domain - UG-ISP Compliant

Provides testing capabilities through multiple interfaces:
- pytest: Pytest-based testing operations
- scanner: Scanner test operations
- report: Test report generation and export

UG-ISP Architecture:
    External Code -> TestGateway -> Interface -> Factory -> Implementation
"""

from __future__ import annotations
from EE.test.test_gateway import TestGateway

__all__ = [
    'TestGateway',
]
