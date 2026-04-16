"""ha_config.py - Config Interface Router (INT-HA-05)
Version: 2026-04-01_6
Description: Router for Home Assistant configuration operations

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


def _get_config_core_functions():
    """Lazy import Config core functions (SUGA-ISP compliant)."""
    try:
        from lee.home_assistant.ha_config import (
            get_ha_config,
        )
        return {
            "get_ha_config": get_ha_config,
            "get_config": get_ha_config,  # Alias
        }
    except ImportError as e:
        raise RuntimeError(f"Failed to import Config core functions: {e}")


# Dispatch dictionary for O(1) operation routing
_CONFIG_DISPATCH = {
    "get_ha_config": lambda **kw: _get_config_core_functions()["get_ha_config"](**kw),
    "get_config": lambda **kw: _get_config_core_functions()["get_config"](**kw),
}


class _ConfigRouter(BaseSimpleDispatchRouter):
    """Router for Config interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Config",
            core_module=DummyModule(),
            dispatch_map=_CONFIG_DISPATCH
        )

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute Config interface operation with SUGA-ISP routing.

        Args:
            operation: The Config operation to execute
            **kwargs: Operation-specific parameters

        Returns:
            Operation result
        """
        # Generate correlation ID for tracking
        corr_id = generate_correlation_id("ha")

        # Validate operation exists
        if operation not in self.dispatch_map:
            error_msg = f"Unknown Config operation: {operation}"
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=corr_id, scope="HOME_ASSISTANT",
                                 message=error_msg, op_name=operation)
            except (AttributeError, KeyError, TypeError, RuntimeError, ImportError):
                # Gracefully degrade if debug unavailable (optional debug output)
                pass
            raise ValueError(error_msg)

        # Get handler
        handler = self.dispatch_map[operation]

        # Execute with debug support
        try:
            # Log operation start
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=corr_id, scope="HOME_ASSISTANT",
                             message=f"Starting Config operation: {operation}",
                             op_name=operation, param_count=len(kwargs))

            # Execute operation
            result = handler(**kwargs)

            # Log successful completion
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=corr_id, scope="HOME_ASSISTANT",
                             message=f"Completed Config operation: {operation}",
                             op_name=operation, success=True)

            return result

        except (AttributeError, KeyError, TypeError, ValueError, RuntimeError) as e:
            # Log error with context
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=corr_id, scope="HOME_ASSISTANT",
                             message=f"Error in Config operation: {operation}",
                             op_name=operation, error=str(e),
                             error_type=type(e).__name__)
            except (AttributeError, KeyError, TypeError, RuntimeError, ImportError):
                # Gracefully degrade if debug unavailable (optional debug output)
                pass
            raise


_config_router = _ConfigRouter()


def execute_config_operation(operation: str, **kwargs) -> Any:
    """Execute Config interface operation with SUGA-ISP routing.

    Args:
        operation: The Config operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result
    """
    return _config_router.execute(operation, **kwargs)


__all__ = ["execute_config_operation"]
