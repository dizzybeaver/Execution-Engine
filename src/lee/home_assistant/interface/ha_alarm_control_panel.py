"""ha_alarm_control_panel.py - Alarm Control Panel Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AlarmControlPanelRouter(BaseFallbackRouter):
    """Router for Alarm Control Panel interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AlarmControlPanel",
            import_path="lee.home_assistant.ha_alarm_control_panel.ha_alarm_control_panel_core",
            function_names=[
                "list_alarm_control_panels_impl",
                "alarm_arm_away_impl",
                "alarm_arm_home_impl",
                "alarm_arm_night_impl",
                "alarm_arm_custom_bypass_impl",
                "alarm_disarm_impl",
                "alarm_trigger_impl",
            ]
        )


_alarm_control_panel_router = _AlarmControlPanelRouter()


def execute_alarm_control_panel_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Alarm Control Panel interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _alarm_control_panel_router.execute(operation, **kwargs)
