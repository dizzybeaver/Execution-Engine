"""ha_repairs.py - Repairs Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _RepairsRouter(BaseFallbackRouter):
    """Router for Repairs interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Repairs",
            import_path="lee.home_assistant.ha_repairs.ha_repairs_core",
            function_names=[
                "list_issues_impl",
                "get_issue_data_impl",
                "ignore_issue_impl",
            ]
        )


_repairs_router = _RepairsRouter()


def execute_repairs_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Repairs interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _repairs_router.execute(operation, **kwargs)
