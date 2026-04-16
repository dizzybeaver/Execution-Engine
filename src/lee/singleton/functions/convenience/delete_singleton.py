"""delete_singleton.py
Extracted from: singleton_convenience.py
Function: delete_singleton
"""

from lee.gateway import GatewayInterface, execute_operation


def delete_singleton(name: str) -> bool:
    """Delete a specific singleton."""

    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "delete",
            name=name,
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to delete singleton '{name}': {e}",
            error_type=type(e).__name__,
        )
        return False
