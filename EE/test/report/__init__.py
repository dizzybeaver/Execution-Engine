"""
Report Interface - Test Domain

Provides test report generation and export operations.

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
"""

from __future__ import annotations
from EE.test.report.report_interface import create_report_interface

__all__ = [
    'create_report_interface',
]
