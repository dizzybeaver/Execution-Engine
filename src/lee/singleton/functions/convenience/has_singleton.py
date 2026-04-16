"""has_singleton.py
Extracted from: singleton_convenience.py
Function: has_singleton
"""

from lee.gateway import GatewayInterface, execute_operation


def has_singleton(name: str) -> bool:
    """Check if a singleton exists."""

    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "has",
            name=name,
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to check singleton '{name}': {e}",
            error_type=type(e).__name__,
        )
        return False
