"""ha_blueprint.py - Blueprint Interface Router
Version: 2026-04-01_6
Description: Router for Blueprint operations (STUB)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


def _reload_blueprints_impl(**kwargs):
    return {
        "success": False,
        "error": "Blueprint operations not available - Home Assistant Blueprints require Home Assistant OS Supervisor",
        "available": False,
    }


def _list_blueprints_impl(**kwargs):
    return {
        "success": False,
        "error": "Blueprint operations not available - Home Assistant Blueprints require Home Assistant OS Supervisor",
        "available": False,
        "blueprints": [],
    }


def _get_blueprint_impl(**kwargs):
    return {
        "success": False,
        "error": "Blueprint operations not available - Home Assistant Blueprints require Home Assistant OS Supervisor",
        "available": False,
    }


_BLUEPRINT_DISPATCH = {
    "reload_blueprints": _reload_blueprints_impl,
    "list_blueprints": _list_blueprints_impl,
    "get_blueprint": _get_blueprint_impl,
}


class _BlueprintRouter(BaseSimpleDispatchRouter):
    """Router for Blueprint interface operations."""

    def __init__(self):
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="Blueprint",
            core_module=DummyModule(),
            dispatch_map=_BLUEPRINT_DISPATCH
        )


_blueprint_router = _BlueprintRouter()


def execute_blueprint_operation(operation: str, **kwargs) -> Any:
    """Execute Blueprint operation via dispatch (STUB).

    Args:
        operation: The Blueprint operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from Blueprint implementation
    """
    return _blueprint_router.execute(operation, **kwargs)


__all__ = ["execute_blueprint_operation"]
