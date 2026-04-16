"""ha_shelly.py - Shelly Smart Home Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_shelly import ha_shelly_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _ShellyRouter(BaseSimpleDispatchRouter):
    """Router for Shelly smart home interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Shelly",
            core_module=ha_shelly_core,
            dispatch_map={
                "get_kvs_value": ha_shelly_core.get_kvs_value_impl,
                "set_kvs_value": ha_shelly_core.set_kvs_value_impl,
            }
        )


_shelly_router = _ShellyRouter()


def execute_shelly_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Shelly smart home interface operations using DD-1 pattern."""
    return _shelly_router.execute(operation, **kwargs)
