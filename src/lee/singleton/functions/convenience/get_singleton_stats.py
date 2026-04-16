"""get_singleton_stats.py
Extracted from: singleton_convenience.py
Function: get_singleton_stats
"""

from lee.gateway import GatewayInterface, execute_operation


def get_singleton_stats() -> dict:
    """Get singleton statistics."""

    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get_stats",
        )
    except (RuntimeError, ValueError, AttributeError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get singleton stats: {e}",
            error_type=type(e).__name__,
        )
        return {}
