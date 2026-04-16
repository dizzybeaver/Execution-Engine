"""ha_neato.py - Neato Robot Vacuum Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_neato import ha_neato_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _NeatoRouter(BaseSimpleDispatchRouter):
    """Router for Neato vacuum interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Neato vacuum",
            core_module=ha_neato_core,
            dispatch_map={
                "custom_cleaning": ha_neato_core.custom_cleaning_impl,
            }
        )


_neato_router = _NeatoRouter()


def execute_neato_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Neato vacuum interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _neato_router.execute(operation, **kwargs)
