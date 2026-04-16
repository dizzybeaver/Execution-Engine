"""ha_webostv.py - LG webOS TV Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_webostv import ha_webostv_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _WebostvRouter(BaseSimpleDispatchRouter):
    """Router for LG webOS TV interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="LG webOS TV",
            core_module=ha_webostv_core,
            dispatch_map={
                "button": ha_webostv_core.button_impl,
                "command": ha_webostv_core.command_impl,
                "select_sound_output": ha_webostv_core.select_sound_output_impl,
            }
        )


_webostv_router = _WebostvRouter()


def execute_webostv_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch LG webOS TV interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _webostv_router.execute(operation, **kwargs)
