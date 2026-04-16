"""base_routers.py - Base classes for Home Assistant interface routers

Version: 2026-04-01_1
Description: Consolidated router patterns to reduce code duplication

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from abc import ABC
from typing import Any
from collections.abc import Callable


class BaseSimpleDispatchRouter(ABC):
    """Base router for simple dispatch pattern (DD-1).

    Used by 55+ HA interface files that follow the simple dispatch pattern:
    - Dispatch table maps operation names to implementation functions
    - Returns error dict for unknown operations
    - No fallback logic or debug logging

    Example:
        class AbodeRouter(BaseSimpleDispatchRouter):
            def __init__(self):
                super().__init__(
                    interface_name="Abode",
                    core_module=ha_abode_core,
                    dispatch_map={
                        "capture_image": ha_abode_core.capture_image_impl,
                        "change_setting": ha_abode_core.change_setting_impl,
                    }
                )

        router = AbodeRouter()
        result = router.execute("capture_image", entity_id="sensor.abode")
    """

    def __init__(
        self,
        interface_name: str,
        core_module: Any,
        dispatch_map: dict[str, Callable],
    ):
        """Initialize router with dispatch configuration.

        Args:
            interface_name: Human-readable interface name
            core_module: Module containing implementation functions
            dispatch_map: Dictionary mapping operation names to functions
        """
        self.interface_name = interface_name
        self.core_module = core_module
        self.dispatch_map = dispatch_map

    def execute(self, operation: str, **kwargs) -> dict[str, Any]:
        """Execute operation using dispatch table.

        Args:
            operation: Operation name to execute
            **kwargs: Operation-specific parameters

        Returns:
            Operation result dictionary

        Raises:
            ValueError: If operation not found in dispatch map
        """
        func = self.dispatch_map.get(operation)
        if func is None:
            return {
                "success": False,
                "error_code": "UNKNOWN_OPERATION",
                "error_message": (
                    f"Unknown {self.interface_name} operation: {operation}"
                ),
                "available_operations": list(self.dispatch_map.keys()),
            }

        return func(**kwargs)


class BaseFallbackRouter(ABC):
    """Base router for fallback dispatch pattern with optional imports.

    Used by 11+ HA interface files that need graceful degradation:
    - Tries to import implementation functions
    - Provides fallback if import fails
    - Sets HAS_* flag for availability checking

    Example:
        class AlarmControlPanelRouter(BaseFallbackRouter):
            def __init__(self):
                super().__init__(
                    interface_name="AlarmControlPanel",
                    import_path="lee.home_assistant.ha_alarm_control_panel.ha_alarm_control_panel_core",
                    function_names=[
                        "list_alarm_control_panels_impl",
                        "alarm_arm_away_impl",
                    ]
                )

        router = AlarmControlPanelRouter()
        result = router.execute("alarm_arm_away", code="1234")
        if router.is_available():
            print("Interface loaded successfully")
    """

    def __init__(
        self,
        interface_name: str,
        import_path: str,
        function_names: list[str],
    ):
        """Initialize router with fallback configuration.

        Args:
            interface_name: Human-readable interface name
            import_path: Python import path for core module
            function_names: List of function names to import
        """
        self.interface_name = interface_name
        self.import_path = import_path
        self.function_names = function_names
        self.functions: dict[str, Callable] = {}
        self.is_available_flag = False

        self._try_import()

    def _try_import(self):
        """Attempt to import implementation functions."""
        try:
            module = __import__(self.import_path, fromlist=self.function_names)
            for func_name in self.function_names:
                func = getattr(module, func_name, None)
                if func is not None:
                    self.functions[func_name] = func
            self.is_available_flag = bool(self.functions)
        except ImportError:
            self.is_available_flag = False

    def _get_fallback_function(self) -> Callable:
        """Return fallback function for unavailable interface."""

        def fallback(**kwargs) -> dict[str, Any]:
            return {
                "status": "not_implemented",
                "error": (
                    f"HA {self.interface_name.lower()} "
                    f"interface not yet implemented"
                ),
                "interface": f"ha_{self.interface_name.lower()}",
            }

        return fallback

    def _get_function(self, func_name: str) -> Callable:
        """Get implementation function or fallback.

        Tries both the exact operation name and operation_name + '_impl' suffix
        to support both calling conventions.
        """
        # Try exact match first
        if func_name in self.functions:
            return self.functions[func_name]

        # Try with _impl suffix (common naming pattern)
        impl_name = f"{func_name}_impl"
        if impl_name in self.functions:
            return self.functions[impl_name]

        # Return fallback if not found
        return self._get_fallback_function()

    def execute(self, operation: str, **kwargs) -> dict[str, Any]:
        """Execute operation through dispatch dictionary.

        Args:
            operation: Operation name to execute
            **kwargs: Operation-specific parameters

        Returns:
            dict with operation result
        """
        impl = self._get_function(operation)
        return impl(**kwargs)

    def is_available(self) -> bool:
        """Check if interface implementation is available."""
        return self.is_available_flag

    def list_operations(self) -> list[str]:
        """List all available operations."""
        return list(self.function_names)


__all__ = [
    "BaseSimpleDispatchRouter",
    "BaseFallbackRouter",
]
