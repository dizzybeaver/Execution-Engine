"""Zone Wrapper Functions Namespace

Provides direct access to zone device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import zone

    # Get all zones
    zones = zone.get_zones()

    # Get zone entities
    zone.get_entities(entity_id='zone.home')

    # Update zone
    zone.update(entity_id='zone.home')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for zone operations
get_zones = LazyFunctionProxy('interface.ha_zone', 'list_zones')
get_zone_state = LazyFunctionProxy('interface.ha_zone', 'get_zone_state')
get_zone_entities = LazyFunctionProxy('interface.ha_zone', 'get_zone_entities')
update = LazyFunctionProxy('interface.ha_zone', 'update_zone')

__all__ = [
    'get_zones',
    'get_zone_state',
    'get_zone_entities',
    'update',
]
