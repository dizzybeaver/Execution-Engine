# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface_validation.py - Router for Validation Interface

Version: 2026-04-11_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.validation')
def _import_validation():
    from lee.validation import (
        sanitize_input as _sanitize_input,
    )
    from lee.validation import (
        validate_alexa_directive as _validate_alexa_directive,
    )
    from lee.validation import (
        validate_schema as _validate_schema,
    )
    return {
        'sanitize_input': _sanitize_input,
        'validate_alexa_directive': _validate_alexa_directive,
        'validate_schema': _validate_schema,
    }


_validation_funcs = _import_validation()
_VALIDATION_AVAILABLE = _import_validation.__dict__.get('_VALIDATION_AVAILABLE', False)

if _VALIDATION_AVAILABLE:
    _sanitize_input = _validation_funcs['sanitize_input']
    _validate_alexa_directive = _validation_funcs['validate_alexa_directive']
    _validate_schema = _validation_funcs['validate_schema']
else:
    def _validate_alexa_directive(**_kwargs):
        return {"success": False, "error": "Validation not available"}

    def _sanitize_input(**_kwargs):
        return {"success": False, "error": "Validation not available"}

    def _validate_schema(**_kwargs):
        return {"success": False, "error": "Validation not available"}

# Dispatch dictionary for O(1) operation routing
_VALIDATION_DISPATCH = {
    "validate_alexa_directive": _validate_alexa_directive,
    "sanitize_input": _sanitize_input,
    "validate_schema": _validate_schema,
}


class _ValidationRouter(BaseSimpleDispatchRouter):
    """Router for Validation interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            """Dummy module for BaseSimpleDispatchRouter initialization."""

            pass

        super().__init__(
            interface_name="Validation",
            core_module=DummyModule(),
            dispatch_map=_VALIDATION_DISPATCH
        )


_validation_router = _ValidationRouter()


def execute_validation_operation(operation: str, **kwargs) -> Any:
    """Execute Validation operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The Validation operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Validation implementation
    """
    return _validation_router.execute(operation, **kwargs)


def list_validation_operations() -> list[str]:
    """List all available Validation operations."""
    return _validation_router.dispatch_map.keys()


__all__ = [
    "execute_validation_operation",
    "list_validation_operations",
    "_VALIDATION_AVAILABLE"
]
