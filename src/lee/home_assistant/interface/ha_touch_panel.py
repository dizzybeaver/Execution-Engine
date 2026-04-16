"""ha_touch_panel.py - Touch Panel Router

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_touch_panel import ha_touch_panel_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _TouchPanelRouter(BaseSimpleDispatchRouter):
    """Router for Touch Panel operations."""

    def __init__(self):
        super().__init__(
            interface_name="Touch Panel",
            core_module=ha_touch_panel_core,
            dispatch_map={
                "navigate": ha_touch_panel_core.navigate_impl,
                "set_brightness": ha_touch_panel_core.set_brightness_impl,
            }
        )


_touch_panel_router = _TouchPanelRouter()


def execute_touch_panel_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Touch Panel operation using dispatch dictionary.

    Args:
        operation: Operation name from TOUCH_PANEL_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _touch_panel_router.execute(operation, **kwargs)
