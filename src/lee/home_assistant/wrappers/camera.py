"""Camera Wrapper Functions Namespace

Provides direct access to camera device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import camera

    # Get all cameras
    cameras = camera.get_cameras()

    # Take snapshot
    camera.snapshot(entity_id='camera.front_door')

    # Enable motion detection
    camera.enable_motion_detection(entity_id='camera.front_door')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for camera operations
get_cameras = LazyFunctionProxy('interface.ha_camera', 'list')
turn_on = LazyFunctionProxy('interface.ha_camera', 'turn_on')
turn_off = LazyFunctionProxy('interface.ha_camera', 'turn_off')
enable_motion_detection = LazyFunctionProxy('interface.ha_camera', 'enable_motion_detection')
disable_motion_detection = LazyFunctionProxy('interface.ha_camera', 'disable_motion_detection')
snapshot = LazyFunctionProxy('interface.ha_camera', 'snapshot')
play_stream = LazyFunctionProxy('interface.ha_camera', 'play_stream')
record = LazyFunctionProxy('interface.ha_camera', 'record')

__all__ = [
    'get_cameras',
    'turn_on',
    'turn_off',
    'enable_motion_detection',
    'disable_motion_detection',
    'snapshot',
    'play_stream',
    'record',
]
