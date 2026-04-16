"""Device Wrapper Factory

Provides generic factory function to create device wrapper namespaces,
eliminating duplicate LazyFunctionProxy patterns across device modules.

Usage:
    from lee.home_assistant.wrappers.wrapper_factory import (
        create_device_wrappers
    )

    # Create light wrapper
    light = create_device_wrappers(
        module_name='light',
        interface_module='interface.ha_light',
        functions=['get_lights', 'turn_on', 'turn_off', 'toggle',
                  'set_brightness', 'set_color_temp', 'set_rgb_color']
    )

    # Use the wrapper
    light.turn_on(entity_id='light.bubs_bedroom_inside_light_switch_1')
"""

from typing import Any
from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy


def create_device_wrappers(
    module_name: str,
    interface_module: str,
    functions: list[str],
) -> Any:
    """
    Create a device wrapper namespace with lazy-loaded functions.

    This factory function eliminates boilerplate code across device wrappers
    by automatically creating LazyFunctionProxy instances for each function.

    Args:
        module_name: Name of the device module (e.g., 'light', 'switch')
        interface_module: Full interface module path
            (e.g., 'interface.ha_light')
        functions: List of function names to create proxies for

    Returns:
        Namespace object with all function proxies as attributes

    Example:
        light = create_device_wrappers(
            module_name='light',
            interface_module='interface.ha_light',
            functions=['get_lights', 'turn_on', 'turn_off', 'toggle']
        )
        light.turn_on(entity_id='light.bubs_bedroom_inside_light_switch_1')
    """
    # Create a simple namespace object
    class DeviceWrapperNamespace:
        """Namespace for device wrapper functions."""

        __name__ = module_name
        __all__ = functions

    # Add each function as a LazyFunctionProxy
    for func_name in functions:
        proxy = LazyFunctionProxy(interface_module, func_name)
        setattr(DeviceWrapperNamespace, func_name, staticmethod(proxy))

    return DeviceWrapperNamespace


__all__ = [
    'create_device_wrappers',
]
