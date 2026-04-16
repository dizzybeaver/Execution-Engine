"""ha_simplisafe.py - SimpliSafe Security Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_simplisafe import ha_simplisafe_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _SimplisafeRouter(BaseSimpleDispatchRouter):
    """Router for SimpliSafe security interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="SimpliSafe",
            core_module=ha_simplisafe_core,
            dispatch_map={
                "remove_pin": ha_simplisafe_core.remove_pin_impl,
                "set_pin": ha_simplisafe_core.set_pin_impl,
                "set_system_properties": ha_simplisafe_core.set_system_properties_impl,
            }
        )


_simplisafe_router = _SimplisafeRouter()


def execute_simplisafe_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch SimpliSafe security interface operations using DD-1 pattern."""
    return _simplisafe_router.execute(operation, **kwargs)
