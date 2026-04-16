"""ha_image_processing.py - Router for ImageProcessing Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ImageProcessingRouter(BaseFallbackRouter):
    """Router for ImageProcessing interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="ImageProcessing",
            import_path="lee.home_assistant.ha_image_processing.ha_image_processing_core",
            function_names=[]
        )


_ha_image_processing_router = _ImageProcessingRouter()


def execute_ha_image_processing_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch ImageProcessing interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_image_processing_router.execute(operation, **kwargs)


def list_ha_image_processing_operations() -> list[str]:
    """List all available ImageProcessing operations.

    Returns:
        List of operation names
    """
    return _ha_image_processing_router.list_operations()


__all__ = [
    "execute_ha_image_processing_operation",
    "list_ha_image_processing_operations",
]
