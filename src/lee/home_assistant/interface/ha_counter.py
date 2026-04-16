"""ha_counter.py - Counter Interface Router

Version: 2026-04-01_6
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _CounterRouter(BaseFallbackRouter):
    """Router for Counter interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Counter",
            import_path="lee.home_assistant.counter.ha_counter_core",
            function_names=[
                "list_counters_impl",
                "increment_counter_impl",
                "reset_counter_impl",
            ]
        )


_counter_router = _CounterRouter()


def execute_counter_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Execute Counter operation through dispatch dictionary.

    Args:
        operation: The operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Dict with success status and operation result
    """
    return _counter_router.execute(operation, **kwargs)


def list_counter_operations() -> list[str]:
    """List all available Counter operations.

    Returns:
        List of operation names
    """
    return _counter_router.list_operations()


__all__ = [
    "execute_counter_operation",
    "list_counter_operations",
]
