"""get_cost_protection.py
Extracted from: singleton_convenience.py
Function: get_cost_protection
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_cost_protection() -> Optional[Any]:
    """Get cost protection singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="cost_protection",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get cost protection: {e}",
        )
        return None
