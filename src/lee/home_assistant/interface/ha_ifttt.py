"""ha_ifttt.py - IFTTT Webhook Automation Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_ifttt import ha_ifttt_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _IftttRouter(BaseSimpleDispatchRouter):
    """Router for IFTTT webhook automation interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="IFTTT",
            core_module=ha_ifttt_core,
            dispatch_map={
                "push_alarm_state": ha_ifttt_core.push_alarm_state_impl,
                "trigger": ha_ifttt_core.trigger_impl,
            }
        )


_ifttt_router = _IftttRouter()


def execute_ifttt_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch IFTTT webhook automation interface operations using DD-1 pattern."""
    return _ifttt_router.execute(operation, **kwargs)
