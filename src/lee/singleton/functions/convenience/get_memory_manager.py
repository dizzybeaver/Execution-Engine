"""get_memory_manager.py
Extracted from: singleton_convenience.py
Function: get_memory_manager
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_memory_manager() -> Optional[Any]:
    """Get memory manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="memory_manager",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get memory manager: {e}",
        )
        return None
