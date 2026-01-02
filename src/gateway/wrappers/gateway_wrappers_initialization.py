"""
gateway_wrappers_initialization.py - INITIALIZATION Interface Wrappers
Version: 2025.10.22.03
Description: Convenience wrappers for INITIALIZATION interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


def initialize_system(**kwargs) -> Dict[str, Any]:
    """Initialize system."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'initialize', **kwargs)


def get_initialization_status() -> Dict[str, Any]:
    """Get initialization status."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_status')


def initialization_get_stats() -> Dict[str, Any]:
    """Get initialization statistics (alias for initialization_get_status)."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_stats')


def set_initialization_flag(flag: str, value: bool) -> None:
    """Set initialization flag."""
    execute_operation(GatewayInterface.INITIALIZATION, 'set_flag', flag=flag, value=value)


def get_initialization_flag(flag: str) -> bool:
    """Get initialization flag."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_flag', flag=flag)


__all__ = [
    'initialize_system',
    'get_initialization_status',
    'initialization_get_stats',
    'set_initialization_flag',
    'get_initialization_flag',
]
