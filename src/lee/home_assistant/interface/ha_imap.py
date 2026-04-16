"""ha_imap.py - IMAP Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.ha_imap import ha_imap_core
from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter


class _ImapRouter(BaseSimpleDispatchRouter):
    """Router for IMAP interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="IMAP",
            core_module=ha_imap_core,
            dispatch_map={
                "seen": ha_imap_core.seen_impl,
                "move": ha_imap_core.move_impl,
                "delete": ha_imap_core.delete_impl,
                "fetch": ha_imap_core.fetch_impl,
                "fetch_part": ha_imap_core.fetch_part_impl,
            }
        )


_imap_router = _ImapRouter()


def execute_imap_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch IMAP interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _imap_router.execute(operation, **kwargs)
