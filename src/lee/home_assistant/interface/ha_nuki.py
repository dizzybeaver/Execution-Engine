"""ha_nuki.py - Nuki Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_nuki import ha_nuki_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _NukiRouter(BaseSimpleDispatchRouter):
    """Router for Nuki interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Nuki",
            core_module=ha_nuki_core,
            dispatch_map={
                "lock_n_go": ha_nuki_core.lock_n_go_impl,
                "set_continuous_mode": ha_nuki_core.set_continuous_mode_impl,
            }
        )


_nuki_router = _NukiRouter()


def execute_nuki_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Nuki interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _nuki_router.execute(operation, **kwargs)
