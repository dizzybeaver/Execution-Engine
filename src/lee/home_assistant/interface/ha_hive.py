"""ha_hive.py - Hive Heating Interface Router

Version: 2026-04-02_1 (Refactored to use BaseFallbackRouter)
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _HiveRouter(BaseFallbackRouter):
    """Router for Hive heating interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Hive",
            import_path="lee.home_assistant.ha_hive.ha_hive_core",
            function_names=[
                "boost_heating_on_impl",
                "boost_heating_off_impl",
                "boost_hot_water_impl",
            ]
        )


_hive_router = _HiveRouter()


def execute_hive_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Hive heating interface operations using DD-1 pattern."""
    return _hive_router.execute(operation, **kwargs)
