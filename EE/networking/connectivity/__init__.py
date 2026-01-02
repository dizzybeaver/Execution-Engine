"""Connectivity Interface - Networking Domain

Provides network connectivity operations:
- scan: Scan network targets (IP addresses, ranges, ports)
- discover: Discover network resources and services
- test_connection: Test connectivity to network hosts
- get_config: Get connectivity configuration
- set_config: Set connectivity configuration

All operations follow EE 2.1 patterns with dependency injection.
"""

from EE.networking.connectivity.connectivity_interface import execute_connectivity_operation

__all__ = [
    'execute_connectivity_operation',
]
