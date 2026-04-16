"""get_named_singleton.py
Extracted from: singleton_convenience.py
Function: get_named_singleton
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_named_singleton(name: str, factory_func: Optional[Any] = None) -> Optional[Any]:
    """Get named singleton instance.

    Args:
        name: Singleton instance name
        factory_func: Optional factory function to create singleton if it doesn't exist

    Returns:
        Singleton instance or None if not found and no factory provided
    """

    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name=name,
            factory_func=factory_func,
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get singleton '{name}': {e}",
            error_type=type(e).__name__,
        )
        return None
