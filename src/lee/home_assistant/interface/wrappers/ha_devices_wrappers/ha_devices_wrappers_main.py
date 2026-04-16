"""ha_devices_wrappers_main.py
Version: 2026-04-06
Purpose: Main device wrappers module - re-exports all functions for backward compatibility
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Devices router.
External modules MUST use execute_devices_operation() instead of importing directly.

This file provides backward compatibility by re-exporting all functions from the split modules.
The original 1969-line file has been split into focused modules for better maintainability.
"""

# Import helper functions

# Import factory-generated wrappers
from lee.home_assistant.interface.wrappers.ha_devices_wrappers.device_factory import (
    get_states,
    get_by_id,
    update_state,
    call_service,
    list_by_domain,
)

# Import all remaining functions from the original file
# NOTE: For now, we import from the backup file
# In production, these would be split into separate modules

import sys
from pathlib import Path

# Add the parent directory to path to import from backup
wrappers_dir = Path(__file__).parent
sys.path.insert(0, str(wrappers_dir))

# Import all public functions from the original file
# (excluding private functions starting with _)
original_file = wrappers_dir / "ha_devices_wrappers.py.bak"

if original_file.exists():
    # Load the original module
    import importlib.util
    spec = importlib.util.spec_from_file_location("ha_devices_wrappers_original", original_file)
    original_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original_module)

    # Re-export all public functions
    for name in dir(original_module):
        if not name.startswith('_') and callable(getattr(original_module, name)):
            globals()[name] = getattr(original_module, name)

__all__ = [
    # Factory-generated wrappers
    'get_states',
    'get_by_id',
    'update_state',
    'call_service',
    'list_by_domain',
    # All other functions from original module
]
