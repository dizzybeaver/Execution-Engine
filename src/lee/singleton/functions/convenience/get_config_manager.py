"""get_config_manager.py
Extracted from: singleton_convenience.py
Function: get_config_manager
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_config_manager() -> Optional[Any]:
    """Get config manager singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="config_manager",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get config manager: {e}",
        )
        return None
