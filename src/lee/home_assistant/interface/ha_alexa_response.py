"""ha_alexa_response.py - Router for AlexaResponse Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AlexaResponseRouter(BaseFallbackRouter):
    """Router for AlexaResponse interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AlexaResponse",
            import_path="lee.home_assistant.ha_alexa_response.ha_alexa_response_core",
            function_names=[]
        )


_alexa_response_router = _AlexaResponseRouter()


def execute_alexa_response_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch AlexaResponse interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _alexa_response_router.execute(operation, **kwargs)


def list_alexa_response_operations() -> list[str]:
    """List all available AlexaResponse operations.

    Returns:
        List of operation names
    """
    return _alexa_response_router.list_operations()


__all__ = [
    "execute_alexa_response_operation",
    "list_alexa_response_operations",
]
