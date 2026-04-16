"""ha_squeezebox.py - Squeezebox Router

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_squeezebox import ha_squeezebox_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _SqueezeboxRouter(BaseSimpleDispatchRouter):
    """Router for Squeezebox operations."""

    def __init__(self):
        super().__init__(
            interface_name="Squeezebox",
            core_module=ha_squeezebox_core,
            dispatch_map={
                "call_method": ha_squeezebox_core.call_method_impl,
                "play_path": ha_squeezebox_core.play_path_impl,
            }
        )


_squeezebox_router = _SqueezeboxRouter()


def execute_squeezebox_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Squeezebox operation using dispatch dictionary.

    Args:
        operation: Operation name from SQUEEZEBOX_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _squeezebox_router.execute(operation, **kwargs)
