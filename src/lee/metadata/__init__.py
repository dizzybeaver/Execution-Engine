"""metadata package - METADATA interface core modules
Version: 2026-03-18
License: Apache 2.0

This package provides the core implementations for the METADATA gateway interface.
Modules are imported lazily by interface_metadata.py to follow SUGA-ISP architecture.

Public API:
- EventBus: Thread-safe event storage and management
- get_event_bus(): Get singleton EventBus instance
- Various _*_implementation functions for gateway routing
"""

# Re-exports for public API
from lee.metadata.event_bus import (
    EventBus,
    _add_event_implementation,
    _clear_events_implementation,
    _get_all_events_implementation,
    _get_event_count_implementation,
    _get_events_by_type_implementation,
    _get_recent_events_implementation,
    get_event_bus,
)
from lee.metadata.metadata_io import (
    _export_data_implementation,
    _export_to_file_implementation,
    _get_statistics_implementation,
    _import_data_implementation,
    _import_from_file_implementation,
)
from lee.metadata.metadata_store import (
    _clear_metadata_implementation,
    _delete_metadata_implementation,
    _get_all_metadata_implementation,
    _get_metadata_implementation,
    _set_metadata_implementation,
    _update_metadata_implementation,
)
from lee.metadata.system_collector import (
    _get_platform_info_implementation,
    _get_python_info_implementation,
    _get_system_info_implementation,
)

__all__ = [
    # Event bus
    "EventBus",
    "get_event_bus",
    # Event implementations
    "_add_event_implementation",
    "_clear_events_implementation",
    "_get_all_events_implementation",
    "_get_event_count_implementation",
    "_get_events_by_type_implementation",
    "_get_recent_events_implementation",
    # Metadata store implementations
    "_clear_metadata_implementation",
    "_delete_metadata_implementation",
    "_get_all_metadata_implementation",
    "_get_metadata_implementation",
    "_set_metadata_implementation",
    "_update_metadata_implementation",
    # System info implementations
    "_get_platform_info_implementation",
    "_get_python_info_implementation",
    "_get_system_info_implementation",
    # I/O implementations
    "_export_data_implementation",
    "_export_to_file_implementation",
    "_get_statistics_implementation",
    "_import_data_implementation",
    "_import_from_file_implementation",
]
