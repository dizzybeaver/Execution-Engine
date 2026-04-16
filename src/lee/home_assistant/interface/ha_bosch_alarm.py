"""ha_bosch_alarm.py - Bosch Alarm Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BoschAlarmRouter(BaseFallbackRouter):
    """Router for Bosch Alarm operations."""

    def __init__(self):
        super().__init__(
            interface_name="Bosch Alarm",
            import_path="lee.home_assistant.ha_bosch_alarm.ha_bosch_alarm_core",
            function_names=[
                "set_date_time_impl",
            ]
        )


_bosch_alarm_router = _BoschAlarmRouter()


def execute_bosch_alarm_operation(operation: str, **kwargs: Any) -> Any:
    """Execute Bosch Alarm operation using dispatch dictionary.

    Args:
        operation: Operation name from BOSCH_ALARM_DISPATCH
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from implementation function

    Raises:
        ValueError: If operation unknown
    """
    return _bosch_alarm_router.execute(operation, **kwargs)
