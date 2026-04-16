"""Light Wrapper Functions Namespace

Provides direct access to light device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import light

    # Get all lights
    lights = light.get_lights()

    # Turn on light
    light.turn_on(entity_id='light.bubs_bedroom_inside_light_switch_1')

    # Set brightness
    light.set_brightness(entity_id='light.bubs_bedroom_inside_light_switch_1', brightness=255)
"""

from lee.home_assistant.wrappers.wrapper_factory import create_device_wrappers

# Create light wrapper using factory
light = create_device_wrappers(
    module_name='light',
    interface_module='interface.ha_light',
    functions=['get_lights', 'turn_on', 'turn_off', 'toggle',
               'set_brightness', 'set_color_temp', 'set_rgb_color']
)

# Export all functions
get_lights = light.get_lights
turn_on = light.turn_on
turn_off = light.turn_off
toggle = light.toggle
set_brightness = light.set_brightness
set_color_temp = light.set_color_temp
set_rgb_color = light.set_rgb_color

__all__ = [
    'get_lights',
    'turn_on',
    'turn_off',
    'toggle',
    'set_brightness',
    'set_color_temp',
    'set_rgb_color',
]
