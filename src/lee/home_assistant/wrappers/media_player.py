"""Media Player Wrapper Functions Namespace

Provides direct access to media player device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import media_player

    # Get all media players
    players = media_player.get_media_players()

    # Play media
    media_player.play_media(entity_id='media_player.living_room', media_id='spotify:track:123')

    # Pause
    media_player.pause(entity_id='media_player.living_room')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for media player operations
get_media_players = LazyFunctionProxy('interface.ha_media_player', 'get_media_players')
turn_on = LazyFunctionProxy('interface.ha_media_player', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_media_player', 'turn_off')
play_media = LazyFunctionProxy('interface.ha_media_player', 'play_media')
pause = LazyFunctionProxy('interface.ha_media_player', 'pause')
stop = LazyFunctionProxy('interface.ha_media_player', 'stop')
volume_set = LazyFunctionProxy('interface.ha_media_player', 'volume_set')

__all__ = [
    'get_media_players',
    'turn_on',
    'turn_off',
    'play_media',
    'pause',
    'stop',
    'volume_set',
]
