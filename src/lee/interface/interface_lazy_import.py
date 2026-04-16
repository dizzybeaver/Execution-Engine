# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface_lazy_import.py
Version: 2026-04-11_2
Date: 2026-04-11
Purpose: Lazy Import Gateway System interface router (SUGA-ISP Implementation)
License: Apache 2.0

Refactored to use @graceful_import decorator.
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.lee_ligs')
def _import_ligs():
    from lee.lee_ligs import get_lazy_import_registry
    return {'get_lazy_import_registry': get_lazy_import_registry}


_ligs_funcs = _import_ligs()
_LIGS_AVAILABLE = _import_ligs.__dict__.get('_LIGS_AVAILABLE', False)

if _LIGS_AVAILABLE:
    get_lazy_import_registry = _ligs_funcs['get_lazy_import_registry']
else:
    def get_lazy_import_registry():
        raise RuntimeError("Lazy import system unavailable")


# Implementation functions
def _ligs_register(**kwargs) -> None:
    """Register a lazy module."""
    registry = get_lazy_import_registry()
    registry.register(
        name=kwargs["name"],
        module_path=kwargs["module_path"],
        factory=kwargs["factory"]
    )


def _ligs_get(**kwargs) -> Any:
    """Get lazy module (loads if needed)."""
    registry = get_lazy_import_registry()
    return registry.get(kwargs["name"])


def _ligs_preload(**kwargs) -> None:
    """Preload specific modules."""
    registry = get_lazy_import_registry()
    registry.preload(kwargs["names"])


def _ligs_is_loaded(**kwargs) -> bool:
    """Check if module loaded."""
    registry = get_lazy_import_registry()
    return registry.is_loaded(kwargs["name"])


def _ligs_get_all_loaded(**_kwargs) -> set:
    """Get all loaded module names."""
    registry = get_lazy_import_registry()
    return registry.get_all_loaded()


def _ligs_get_all_registered(**_kwargs) -> set:
    """Get all registered module names."""
    registry = get_lazy_import_registry()
    return registry.get_all_registered()


def _ligs_get_load_time(**kwargs) -> float:
    """Get load time for specific module."""
    registry = get_lazy_import_registry()
    return registry.get_load_time_ms(kwargs["name"])


def _ligs_get_stats(**_kwargs) -> dict[str, Any]:
    """Get registry statistics."""
    registry = get_lazy_import_registry()
    return registry.get_stats()


def _ligs_clear(**_kwargs) -> int:
    """Clear all registered modules."""
    registry = get_lazy_import_registry()
    return registry.clear()


# Dispatch dictionary for O(1) operation routing
_LIGS_DISPATCH = {
    "register": _ligs_register,
    "get": _ligs_get,
    "preload": _ligs_preload,
    "is_loaded": _ligs_is_loaded,
    "get_all_loaded": _ligs_get_all_loaded,
    "get_all_registered": _ligs_get_all_registered,
    "get_load_time": _ligs_get_load_time,
    "get_stats": _ligs_get_stats,
    "clear": _ligs_clear,
}


class _LazyImportRouter(BaseSimpleDispatchRouter):
    """Router for lazy import interface operations.

    This router handles lazy import operations including module registration,
    retrieval, preloading, and statistics tracking.
    """

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="LazyImport",
            core_module=DummyModule(),
            dispatch_map=_LIGS_DISPATCH
        )


_lazy_import_router = _LazyImportRouter()


def execute_lazy_import_operation(operation: str, **kwargs) -> Any:
    """Execute lazy import operation via dispatch.

    Args:
        operation: The lazy import operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from lazy import implementation

    Raises:
        RuntimeError: If lazy import interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    if not _LIGS_AVAILABLE:
        raise RuntimeError(
            "Lazy import interface unavailable: lee_ligs module not found",
        )

    return _lazy_import_router.execute(operation, **kwargs)


def list_lazy_import_operations() -> list[str]:
    """List all available lazy import operations."""
    return list(_lazy_import_router.dispatch_map.keys())


__all__ = [
    "execute_lazy_import_operation",
    "list_lazy_import_operations",
    "_LIGS_AVAILABLE",
    "_LIGS_DISPATCH",
]
