"""ha_zha.py - ZHA Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_zha import ha_zha_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _ZhaRouter(BaseSimpleDispatchRouter):
    """Router for ZHA interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="ZHA",
            core_module=ha_zha_core,
            dispatch_map={
                "permit": ha_zha_core.permit_impl,
                "remove": ha_zha_core.remove_impl,
                "reconfigure_device": ha_zha_core.reconfigure_device_impl,
                "set_zigbee_cluster_attribute": ha_zha_core.set_zigbee_cluster_attribute_impl,
                "issue_zigbee_cluster_command": ha_zha_core.issue_zigbee_cluster_command_impl,
                "issue_zigbee_group_command": ha_zha_core.issue_zigbee_group_command_impl,
                "warning_device_squawk": ha_zha_core.warning_device_squawk_impl,
                "warning_device_warn": ha_zha_core.warning_device_warn_impl,
                "clear_lock_user_code": ha_zha_core.clear_lock_user_code_impl,
                "enable_lock_user_code": ha_zha_core.enable_lock_user_code_impl,
                "disable_lock_user_code": ha_zha_core.disable_lock_user_code_impl,
                "set_lock_user_code": ha_zha_core.set_lock_user_code_impl,
            }
        )


_zha_router = _ZhaRouter()


def execute_zha_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch ZHA interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _zha_router.execute(operation, **kwargs)
