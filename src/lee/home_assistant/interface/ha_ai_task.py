"""ha_ai_task.py - Router for AiTask Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AiTaskRouter(BaseFallbackRouter):
    """Router for AiTask interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AiTask",
            import_path="lee.home_assistant.ha_ai_task.ha_ai_task_core",
            function_names=[]
        )


_ai_task_router = _AiTaskRouter()


def execute_ai_task_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch AiTask interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ai_task_router.execute(operation, **kwargs)


def list_ai_task_operations() -> list[str]:
    """List all available AiTask operations.

    Returns:
        List of operation names
    """
    return _ai_task_router.list_operations()


__all__ = [
    "execute_ai_task_operation",
    "list_ai_task_operations",
]
