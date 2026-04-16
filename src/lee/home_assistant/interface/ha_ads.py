"""ha_ads.py - Router for Ads Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AdsRouter(BaseFallbackRouter):
    """Router for Ads interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Ads",
            import_path="lee.home_assistant.ha_ads.ha_ads_core",
            function_names=[]
        )


_ads_router = _AdsRouter()


def execute_ads_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Ads interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _ads_router.execute(operation, **kwargs)


def list_ads_operations() -> list[str]:
    """List all available Ads operations.

    Returns:
        List of operation names
    """
    return _ads_router.list_operations()


__all__ = [
    "execute_ads_operation",
    "list_ads_operations",
]
