"""ha_roku.py - Roku Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_roku import ha_roku_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _RokuRouter(BaseSimpleDispatchRouter):
    """Router for Roku interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Roku",
            core_module=ha_roku_core,
            dispatch_map={
                "search": ha_roku_core.search_impl,
            }
        )


_roku_router = _RokuRouter()


def execute_roku_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Roku interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _roku_router.execute(operation, **kwargs)
