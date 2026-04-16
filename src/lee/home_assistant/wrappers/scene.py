"""Scene Wrapper Functions Namespace

Provides direct access to scene device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import scene

    # Get all scenes
    scenes = scene.get_scenes()

    # Activate scene
    scene.turn_on(entity_id='scene.movie_night')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for scene operations
get_scenes = LazyFunctionProxy('interface.ha_scene', 'list')
turn_on = LazyFunctionProxy('interface.ha_scene', 'turn_on')
reload = LazyFunctionProxy('interface.ha_scene', 'reload')

__all__ = [
    'get_scenes',
    'turn_on',
    'reload',
]
