"""ha_template.py - Router for Template Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _TemplateRouter(BaseFallbackRouter):
    """Router for Template interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Template",
            import_path="lee.home_assistant.ha_template.ha_template_core",
            function_names=[]
        )


_ha_template_router = _TemplateRouter()


def execute_ha_template_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Template interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ha_template_router.execute(operation, **kwargs)


def list_ha_template_operations() -> list[str]:
    """List all available Template operations.

    Returns:
        List of operation names
    """
    return _ha_template_router.list_operations()


__all__ = [
    "execute_ha_template_operation",
    "list_ha_template_operations",
]
