"""get_response_metrics_manager.py
Extracted from: singleton_convenience.py
Function: get_response_metrics_manager
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_response_metrics_manager() -> Optional[Any]:
    """Get response metrics manager singleton.

    Returns:
        Response metrics manager instance or None if not found
    """
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="response_metrics_manager",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get response metrics manager: {e}",
        )
        return None
