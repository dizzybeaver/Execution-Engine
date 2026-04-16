"""ha_calendar.py - Calendar Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _CalendarRouter(BaseFallbackRouter):
    """Router for Calendar interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Calendar",
            import_path="lee.home_assistant.ha_calendar.ha_calendar_core",
            function_names=[
                "list_calendars_impl",
                "create_event_impl",
                "get_calendar_events_impl",
                "update_calendar_event_impl",
                "delete_calendar_event_impl",
            ]
        )


_calendar_router = _CalendarRouter()


def execute_calendar_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Calendar interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _calendar_router.execute(operation, **kwargs)
