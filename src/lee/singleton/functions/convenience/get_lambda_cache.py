"""get_lambda_cache.py
Extracted from: singleton_convenience.py
Function: get_lambda_cache
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_lambda_cache() -> Optional[Any]:
    """Get lambda cache singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="lambda_cache",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get lambda cache: {e}",
        )
        return None
