"""Person Wrapper Functions Namespace

Provides direct access to person device control functions.
All functions load lazily via LazyFunctionProxy.

Example:
    from lee.home_assistant.wrappers import person

    # Get all persons
    persons = person.get_persons()

    # Update person location
    person.update_location(entity_id='person.john', location='home')
"""

from lee.home_assistant.lazy_wrapper_proxy import LazyFunctionProxy

# Create proxy objects for person operations
get_persons = LazyFunctionProxy('interface.ha_person', 'list_persons')
get_person_state = LazyFunctionProxy('interface.ha_person', 'get_person_state')
update_location = LazyFunctionProxy('interface.ha_person', 'update_person_location')
reload = LazyFunctionProxy('interface.ha_person', 'reload')

__all__ = [
    'get_persons',
    'get_person_state',
    'update_location',
    'reload',
]
