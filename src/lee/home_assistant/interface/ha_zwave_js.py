"""ha_zwave_js.py - Z-Wave JS Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_zwave_js import ha_zwave_js_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _ZwaveJsRouter(BaseSimpleDispatchRouter):
    """Router for Z-Wave JS interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Z-Wave JS",
            core_module=ha_zwave_js_core,
            dispatch_map={
                "clear_lock_usercode": ha_zwave_js_core.clear_lock_usercode_impl,
                "get_lock_usercode": ha_zwave_js_core.get_lock_usercode_impl,
                "set_lock_usercode": ha_zwave_js_core.set_lock_usercode_impl,
            }
        )


_zwave_js_router = _ZwaveJsRouter()


def execute_zwave_js_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Z-Wave JS interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _zwave_js_router.execute(operation, **kwargs)
