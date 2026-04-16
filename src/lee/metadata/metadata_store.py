"""metadata_store.py - Key-Value Metadata Store Implementation
Version: 2026-03-18
Purpose: Thread-safe in-memory key-value storage
License: Apache 2.0
"""

import threading
from typing import Any, Optional

_metadata_store: dict[str, Any] = {}
_store_lock = threading.Lock()


def _set_metadata_implementation(key: str, value: Any, correlation_id: Optional[str] = None) -> None:
    """Store metadata key-value pair in thread-safe metadata store.

    Args:
        key: Metadata key (string identifier)
        value: Metadata value to store (any serializable type)
        correlation_id: Optional correlation ID for tracking

    Note:
        This is an internal implementation function called by the gateway.
        Thread-safe through lock-based synchronization.
    """
    with _store_lock:
        _metadata_store[key] = value


def _get_metadata_implementation(key: str, correlation_id: Optional[str] = None) -> Any:
    """Retrieve metadata value by key from thread-safe metadata store.

    Args:
        key: Metadata key to retrieve
        correlation_id: Optional correlation ID for tracking

    Returns:
        Metadata value associated with key, or None if key not found

    Note:
        This is an internal implementation function called by the gateway.
        Thread-safe through lock-based synchronization.
    """
    with _store_lock:
        return _metadata_store.get(key)


def _get_all_metadata_implementation(correlation_id: Optional[str] = None, **_kwargs) -> dict[str, Any]:
    with _store_lock:
        return dict(_metadata_store)


def _delete_metadata_implementation(key: str, correlation_id: Optional[str] = None, **_kwargs) -> bool:
    with _store_lock:
        if key in _metadata_store:
            del _metadata_store[key]
            return True
        return False


def _clear_metadata_implementation(correlation_id: Optional[str] = None, **_kwargs) -> None:
    with _store_lock:
        _metadata_store.clear()


def _update_metadata_implementation(updates: dict[str, Any], correlation_id: Optional[str] = None, **_kwargs) -> None:
    with _store_lock:
        _metadata_store.update(updates)


__all__ = [
    "_set_metadata_implementation",
    "_get_metadata_implementation",
    "_get_all_metadata_implementation",
    "_delete_metadata_implementation",
    "_clear_metadata_implementation",
    "_update_metadata_implementation",
]
