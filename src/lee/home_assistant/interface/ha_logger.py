"""ha_logger.py - Logger Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _LoggerRouter(BaseFallbackRouter):
    """Router for Logger interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Logger",
            import_path="lee.home_assistant.ha_logger.ha_logger_core",
            function_names=[
                "get_log_info_impl",
                "set_integration_log_level_impl",
                "set_module_log_level_impl",
            ]
        )


_logger_router = _LoggerRouter()


def execute_logger_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Logger interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _logger_router.execute(operation, **kwargs)
