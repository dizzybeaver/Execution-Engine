"""ha_google_assistant.py - Google Assistant Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _GoogleAssistantRouter(BaseFallbackRouter):
    """Router for Google Assistant interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Google Assistant",
            import_path="lee.home_assistant.ha_google_assistant.ha_google_assistant_core",
            function_names=[
                "request_sync_impl",
            ]
        )


_google_assistant_router = _GoogleAssistantRouter()


def execute_google_assistant_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Google Assistant interface operations using DD-1 pattern."""
    return _google_assistant_router.execute(operation, **kwargs)
