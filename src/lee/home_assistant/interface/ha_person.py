"""ha_person.py - Person Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _PersonRouter(BaseFallbackRouter):
    """Router for Person interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Person",
            import_path="lee.home_assistant.ha_person.ha_person_core",
            function_names=[
                "list_persons_impl",
                "get_person_state_impl",
                "update_person_location_impl",
                "reload_persons_impl",
            ]
        )


_person_router = _PersonRouter()


def execute_person_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Person interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _person_router.execute(operation, **kwargs)
