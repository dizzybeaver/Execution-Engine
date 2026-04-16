"""ha_utility_meter.py - UTILITY_METER Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_utility_meter import ha_utility_meter_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _UtilityMeterRouter(BaseSimpleDispatchRouter):
    """Router for UTILITY_METER interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="UTILITY_METER",
            core_module=ha_utility_meter_core,
            dispatch_map={
                "reset": ha_utility_meter_core.reset_impl,
                "calibrate": ha_utility_meter_core.calibrate_impl,
            }
        )


_utility_meter_router = _UtilityMeterRouter()


def execute_utility_meter_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch UTILITY_METER interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _utility_meter_router.execute(operation, **kwargs)
