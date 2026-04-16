"""ha_mqtt.py - MQTT Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_mqtt import ha_mqtt_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _MqttRouter(BaseSimpleDispatchRouter):
    """Router for MQTT interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="MQTT",
            core_module=ha_mqtt_core,
            dispatch_map={
                "publish": ha_mqtt_core.publish_impl,
                "dump": ha_mqtt_core.dump_impl,
                "reload": ha_mqtt_core.reload_impl,
            }
        )


_mqtt_router = _MqttRouter()


def execute_mqtt_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch MQTT interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _mqtt_router.execute(operation, **kwargs)
