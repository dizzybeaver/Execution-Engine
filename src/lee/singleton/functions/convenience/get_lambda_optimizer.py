"""get_lambda_optimizer.py
Extracted from: singleton_convenience.py
Function: get_lambda_optimizer
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_lambda_optimizer() -> Optional[Any]:
    """Get lambda optimizer singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="lambda_optimizer",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get lambda optimizer: {e}",
        )
        return None
