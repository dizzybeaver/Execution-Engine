"""
interface/__init__.py - Interface Package Initialization
Version: 2025-12-13_1
Purpose: Central import point for all LEE interface modules
License: Apache 2.0

This package contains all 14 LEE interface router modules that dispatch
operations to their respective implementations following SUGA pattern.
"""

# Interface modules are imported directly, not re-exported
# Users should call through gateway, not directly through interfaces

__all__ = []

__version__ = '2025-12-13_1'
