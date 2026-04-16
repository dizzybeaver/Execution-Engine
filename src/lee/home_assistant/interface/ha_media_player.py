"""ha_media_player.py - Media Player Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _MediaPlayerRouter(BaseFallbackRouter):
    """Router for Media Player interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="MediaPlayer",
            import_path="lee.home_assistant.ha_media_player.ha_media_player_core",
            function_names=[
                "list_media_players_impl",
                "turn_on_media_player_impl",
                "turn_off_media_player_impl",
                "play_media_impl",
                "media_pause_impl",
                "media_stop_impl",
                "volume_set_impl",
            ]
        )


_media_player_router = _MediaPlayerRouter()


def execute_media_player_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Media Player interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _media_player_router.execute(operation, **kwargs)
