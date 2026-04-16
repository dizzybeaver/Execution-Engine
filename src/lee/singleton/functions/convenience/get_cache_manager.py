"""get_cache_manager.py
Extracted from: singleton_convenience.py
Function: get_cache_manager
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_cache_manager() -> Optional[Any]:
    """Get cache manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="cache_manager",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get cache manager: {e}",
            error_type=type(e).__name__,
        )
        return None
