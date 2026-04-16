"""Metadata Module

Provides event tracking, system information collection, and key-value metadata storage.

Ported from UGA observability foundation (2026-03-08)
Ref: ee-obs-metadata
"""

from .event_bus import EventBus, get_event_bus
from .metadata_store import MetadataStore, get_metadata_store
from .system_collector import SystemCollector, get_system_collector

__all__ = [
    "EventBus",
    "MetadataStore",
    "SystemCollector",
    "get_event_bus",
    "get_metadata_store",
    "get_system_collector",
]
