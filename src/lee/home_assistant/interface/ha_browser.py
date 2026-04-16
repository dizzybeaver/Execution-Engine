"""ha_browser.py - Browser Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _BrowserRouter(BaseFallbackRouter):
    """Router for Browser interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Browser",
            import_path="lee.home_assistant.ha_browser.ha_browser_core",
            function_names=[
                "browse_url_impl",
            ]
        )


_browser_router = _BrowserRouter()


def execute_browser_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Browser interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _browser_router.execute(operation, **kwargs)
