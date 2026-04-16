"""gateway/__init__.py - Gateway Package (SUGA-ISP Implementation)
Version: 2025-12-17_1
Purpose: Central gateway entry point following SUGA-ISP networking pattern
License: Apache 2.0

SUGA-ISP Architecture:
- Gateway = ISP (Internet Service Provider) - Central routing hub
- Interface = Router - Routes to specific service networks
- External modules = Computers - Access services through gateway

External modules MUST use:
    from lee.gateway import execute_operation, GatewayInterface
    execute_operation(GatewayInterface.SINGLETON, 'get', name='key')

NEVER import wrapper functions directly!
"""

# Import wrapper submodule
from lee.gateway import wrappers
from lee.gateway.gateway_core import (
    create_error_response,
    create_success_response,
    execute_operation,
    generate_correlation_id,
    get_gateway_stats,
    reset_gateway_state,
)
from lee.gateway.gateway_enums import GatewayInterface

# SUGA-ISP Core: export core gateway functions and wrapper submodule
__all__ = [
    # Core gateway functions
    "GatewayInterface",
    "execute_operation",
    "generate_correlation_id",
    "get_gateway_stats",
    "reset_gateway_state",
    "create_error_response",
    "create_success_response",
    # Wrapper submodule (NEW: user-facing API)
    "wrappers",
]

__version__ = "2025-12-17_1"
