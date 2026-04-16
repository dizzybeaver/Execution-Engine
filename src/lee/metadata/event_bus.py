"""Event Bus

Thread-safe event storage and management for request correlation and tracking.

Ported from UGA observability foundation (2026-03-08)
Ref: ee-obs-metadata-events-core

Security Considerations:
- Thread-safe event storage using threading.Lock
- FIFO eviction when max_events limit reached
- Automatic timestamp addition if not provided
- No sensitive data logging (avoid OAuth tokens, passwords)
"""

# pylint: disable=global-statement
# Global variable is used for singleton pattern with thread-safe initialization

from typing import Optional
import threading
from datetime import datetime, UTC


class EventBus:
    """Thread-safe event storage and management.

    Provides FIFO event buffer with automatic eviction when max_events limit
    is reached. Suitable for request correlation, debugging, and audit trails.

    Attributes:
        _events: Internal event storage list
        _max_events: Maximum number of events to store (default: 1000)
        _data_lock: Thread safety lock for event operations

    Thread Safety:
        All operations are thread-safe using threading.Lock
        Suitable for Lambda single-threaded execution but safe for multi-threaded

    Lambda Impact:
        Memory: ~500KB for 1000 events (estimate)
        Cold start: +10ms
        Runtime: <1ms per operation

    """

    def __init__(self, max_events: int = 1000):
        """Initialize EventBus with event storage.

        Args:
            max_events: Maximum number of events to store (default 1000)

        Note:
            When max_events limit is reached, oldest events are evicted (FIFO)

        """
        self._events = []
        self._max_events = max_events
        self._data_lock = threading.Lock()

    def add(self, event: dict) -> None:
        """Add event to storage.

        Args:
            event: Event dictionary (may include timestamp, type, data)

        Example:
            >>> event_bus.add({
            ...     'type': 'request_received',
            ...     'data': {'request_id': 'abc123', 'endpoint': '/api/devices'}
            ... })

        """
        event_with_timestamp = {
            "timestamp": event.get("timestamp", datetime.now(UTC).isoformat()),
            "type": event.get("type", "unknown"),
            "data": event.get("data", {}),
        }

        with self._data_lock:
            self._events.append(event_with_timestamp)

            # Keep only last N events (FIFO eviction)
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

    def get_all(self) -> list[dict]:
        """Get all events.

        Returns:
            List of all event dictionaries

        Thread Safety:
            Returns a copy of events list to avoid external modification

        """
        with self._data_lock:
            return list(self._events)

    def get_by_type(self, event_type: str) -> list[dict]:
        """Get events filtered by type.

        Args:
            event_type: Event type to filter

        Returns:
            List of events matching type

        Example:
            >>> errors = event_bus.get_by_type('error')

        """
        with self._data_lock:
            return [e for e in self._events if e.get("type") == event_type]

    def get_recent(self, count: int) -> list[dict]:
        """Get most recent events.

        Args:
            count: Number of recent events to return

        Returns:
            List of most recent events

        Example:
            >>> recent = event_bus.get_recent(10)

        """
        with self._data_lock:
            return self._events[-count:] if count < len(self._events) else list(self._events)

    def clear(self) -> None:
        """Clear all events.

        Useful for testing or between Lambda invocations.
        """
        with self._data_lock:
            self._events.clear()

    def count(self) -> int:
        """Get total event count.

        Returns:
            Number of events stored

        """
        with self._data_lock:
            return len(self._events)


# Module-level singleton instance
_event_bus_instance = None
_event_bus_lock = threading.Lock()


def get_event_bus(max_events: int = 1000) -> EventBus:
    """Get singleton EventBus instance.

    Thread-safe singleton accessor with lazy initialization.

    Args:
        max_events: Maximum events (only used on first call)

    Returns:
        Singleton EventBus instance

    Thread Safety:
        Thread-safe initialization using double-checked locking

    Example:
        >>> from lee.metadata import get_event_bus
        >>> event_bus = get_event_bus()
        >>> event_bus.add({'type': 'test', 'data': {}})

    """
    global _event_bus_instance

    if _event_bus_instance is None:
        with _event_bus_lock:
            # Double-check lock pattern
            if _event_bus_instance is None:
                _event_bus_instance = EventBus(max_events=max_events)

    return _event_bus_instance


# ===== GATEWAY INTERFACE IMPLEMENTATIONS =====

def _add_event_implementation(event: dict, correlation_id: Optional[str] = None, **kwargs) -> str:
    """Add event to storage (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    bus.add(event)
    return f"evt_{id(event)}"

def _get_all_events_implementation(correlation_id: Optional[str] = None, **kwargs) -> list:
    """Get all events (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    return bus.get_all()

def _get_events_by_type_implementation(event_type: str, correlation_id: Optional[str] = None, **kwargs) -> list:
    """Get events by type (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    return bus.get_by_type(event_type)

def _get_recent_events_implementation(count: int = 100, correlation_id: Optional[str] = None, **kwargs) -> list:
    """Get recent events (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    return bus.get_recent(count)

def _clear_events_implementation(correlation_id: Optional[str] = None, **kwargs) -> None:
    """Clear all events (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    bus.clear()

def _get_event_count_implementation(correlation_id: Optional[str] = None, **kwargs) -> int:
    """Get event count (gateway interface implementation)."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    bus = get_event_bus()
    return bus.count()


__all__ = [
    "EventBus",
    "_add_event_implementation",
    "_clear_events_implementation",
    "_get_all_events_implementation",
    "_get_event_count_implementation",
    "_get_events_by_type_implementation",
    "_get_recent_events_implementation",
    "get_event_bus",
]
