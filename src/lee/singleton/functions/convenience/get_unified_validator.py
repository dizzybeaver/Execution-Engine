"""get_unified_validator.py
Extracted from: singleton_convenience.py
Function: get_unified_validator
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


def get_unified_validator() -> Optional[Any]:
    """Get unified validator singleton."""
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            "get",
            name="unified_validator",
        )
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_error",
            message=f"Failed to get unified validator: {e}",
        )
        return None
