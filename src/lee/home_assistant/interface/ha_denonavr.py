"""ha_denonavr.py - Denon AVR Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _DenonavrRouter(BaseFallbackRouter):
    """Router for Denon AVR interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Denon AVR",
            import_path="lee.home_assistant.ha_denonavr.ha_denonavr_core",
            function_names=[
                "get_command_impl",
                "set_dynamic_eq_impl",
                "update_audyssey_impl",
            ]
        )


_denonavr_router = _DenonavrRouter()


def execute_denonavr_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Denon AVR interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _denonavr_router.execute(operation, **kwargs)
