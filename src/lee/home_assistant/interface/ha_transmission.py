"""ha_transmission.py - BitTorrent Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_transmission import ha_transmission_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _TransmissionRouter(BaseSimpleDispatchRouter):
    """Router for Transmission interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Transmission",
            core_module=ha_transmission_core,
            dispatch_map={
                "add_torrent": ha_transmission_core.add_torrent_impl,
                "get_torrents": ha_transmission_core.get_torrents_impl,
                "remove_torrent": ha_transmission_core.remove_torrent_impl,
                "start_torrent": ha_transmission_core.start_torrent_impl,
                "stop_torrent": ha_transmission_core.stop_torrent_impl,
            }
        )


_transmission_router = _TransmissionRouter()


def execute_transmission_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Transmission interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _transmission_router.execute(operation, **kwargs)
