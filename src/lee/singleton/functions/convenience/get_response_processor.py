"""get_response_processor.py
Extracted from: singleton_convenience.py
Function: get_response_processor
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_response_processor() -> Optional[Any]:
    """Get response processor singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="response_processor",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get response processor: {e}",
        )
        return None
