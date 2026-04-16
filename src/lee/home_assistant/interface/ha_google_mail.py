"""ha_google_mail.py - Gmail Integration Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _GoogleMailRouter(BaseFallbackRouter):
    """Router for Gmail integration interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Gmail",
            import_path="lee.home_assistant.ha_google_mail.ha_google_mail_core",
            function_names=[
                "set_vacation_impl",
            ]
        )


_google_mail_router = _GoogleMailRouter()


def execute_google_mail_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Gmail integration interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _google_mail_router.execute(operation, **kwargs)
