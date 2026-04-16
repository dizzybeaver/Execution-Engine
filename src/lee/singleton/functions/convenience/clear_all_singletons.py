"""clear_all_singletons.py
Extracted from: singleton_convenience.py
Function: clear_all_singletons
"""

from lee.gateway import GatewayInterface, execute_operation


def clear_all_singletons() -> int:
    """Clear all singletons. Returns count cleared."""

    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "clear",
        )
    except (RuntimeError, ValueError, AttributeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to clear singletons: {e}",
            error_type=type(e).__name__,
        )
        return 0
