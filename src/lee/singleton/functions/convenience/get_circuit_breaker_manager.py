"""get_circuit_breaker_manager.py
Extracted from: singleton_convenience.py
Function: get_circuit_breaker_manager
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_circuit_breaker_manager() -> Optional[Any]:
    """Get circuit breaker manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="circuit_breaker_manager",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get circuit breaker manager: {e}",
            error_type=type(e).__name__,
        )
        return None
