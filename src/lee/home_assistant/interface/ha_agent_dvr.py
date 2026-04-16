"""ha_agent_dvr.py - Router for AgentDvr Interface

Version: 2026-04-01_5
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _AgentDvrRouter(BaseFallbackRouter):
    """Router for AgentDvr interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="AgentDvr",
            import_path="lee.home_assistant.ha_agent_dvr.ha_agent_dvr_core",
            function_names=[]
        )


_agent_dvr_router = _AgentDvrRouter()


def execute_agent_dvr_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch AgentDvr interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _agent_dvr_router.execute(operation, **kwargs)


def list_agent_dvr_operations() -> list[str]:
    """List all available AgentDvr operations.

    Returns:
        List of operation names
    """
    return _agent_dvr_router.list_operations()


__all__ = [
    "execute_agent_dvr_operation",
    "list_agent_dvr_operations",
]
