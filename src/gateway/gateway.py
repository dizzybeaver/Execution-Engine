"""
gateway.py - Central Gateway Entry Point (LEGACY - use __init__.py instead)
Version: 2025-12-13_1
Purpose: Single entry point for all LEE operations
License: Apache 2.0

NOTE: This file is legacy. The gateway package now uses __init__.py.
      This file is kept for backwards compatibility only.
      Import from 'gateway' package, not 'gateway.gateway'.
"""

# Import everything from package __init__.py
from gateway import *

# Re-export everything
__all__ = [
    'GatewayInterface',
    'execute_operation',
    'get_gateway_stats',
    'reset_gateway_state',
    'create_error_response',
    'create_success_response',
    # All wrapper functions are imported from __init__.py
]
