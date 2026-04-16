"""Alarm Control Panel Wrapper Functions Namespace

Provides direct access to alarm control panel device control functions.
All functions load lazily via LazyFunctionProxy.

Note: Core implementation for alarm control panel is not yet complete.
These wrappers are provided for API consistency but may not function until
core implementation is added.

Example:
    from lee.home_assistant.wrappers import alarm_control_panel

    # Get all alarm control panels
    panels = alarm_control_panel.get_alarm_control_panels()

    # Arm alarm away
    alarm_control_panel.arm_away(entity_id='alarm_control_panel.home')

    # Disarm alarm
    alarm_control_panel.disarm(entity_id='alarm_control_panel.home', code='1234')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for alarm control panel operations
get_alarm_control_panels = LazyFunctionProxy('interface.ha_alarm_control_panel', 'list_alarm_control_panels')
arm_away = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_arm_away')
arm_home = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_arm_home')
arm_night = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_arm_night')
arm_custom_bypass = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_arm_custom_bypass')
disarm = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_disarm')
trigger = LazyFunctionProxy('interface.ha_alarm_control_panel', 'alarm_trigger')

__all__ = [
    'get_alarm_control_panels',
    'arm_away',
    'arm_home',
    'arm_night',
    'arm_custom_bypass',
    'disarm',
    'trigger',
]
