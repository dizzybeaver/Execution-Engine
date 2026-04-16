"""ha_ps4.py - PlayStation 4 Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_ps4 import ha_ps4_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _Ps4Router(BaseSimpleDispatchRouter):
    """Router for PS4 interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="PS4",
            core_module=ha_ps4_core,
            dispatch_map={
                "send_command": ha_ps4_core.send_command_impl,
            }
        )


_ps4_router = _Ps4Router()


def execute_ps4_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch PS4 interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ps4_router.execute(operation, **kwargs)
