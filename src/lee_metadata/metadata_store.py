"""Metadata Store

Thread-safe key-value metadata storage.

Ported from UGA observability foundation (2026-03-08)
Ref: ee-obs-metadata-storage-core

Security Considerations:
- Thread-safe key-value storage using threading.Lock
- No sensitive data storage (avoid OAuth tokens, passwords, PII)
- All values are stored as-is (no automatic sanitization)
- Application lifecycle only (not persisted across Lambda invocations)

Lambda Impact:
    Memory: ~50-100KB for typical metadata (varies by usage)
    Cold start: +5ms
    Runtime: <1ms per operation
"""

import threading
from typing import Any


class MetadataStore:
    """Thread-safe key-value metadata storage.

    Provides simple dictionary-like storage for application metadata.
    Useful for storing request context, configuration values, or
    runtime state that needs to be shared across components.

    Attributes:
        _metadata: Internal storage dictionary
        _data_lock: Thread safety lock for metadata operations

    Thread Safety:
        All operations are thread-safe using threading.Lock
        Suitable for Lambda single-threaded execution but safe for multi-threaded

    Use Cases:
        - Request correlation metadata
        - Feature flags or configuration overrides
        - Runtime state tracking
        - Cross-component communication

    Lambda Impact:
        Memory: Variable (~50-100KB typical)
        Cold start: +5ms
        Runtime: <1ms per operation

    """

    def __init__(self):
        """Initialize MetadataStore with key-value storage.

        Note:
            Metadata is not persisted across Lambda invocations.
            All data is lost when container is recycled.

        """
        self._metadata = {}
        self._data_lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        """Set a metadata key-value pair.

        Args:
            key: Metadata key (must be string)
            value: Metadata value (any type)

        Example:
            >>> store = MetadataStore()
            >>> store.set('request_id', 'abc123')
            >>> store.set('retry_count', 3)

        """
        with self._data_lock:
            self._metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a metadata value by key.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default

        Example:
            >>> store = MetadataStore()
            >>> store.set('request_id', 'abc123')
            >>> store.get('request_id')
            'abc123'
            >>> store.get('missing_key', 'default')
            'default'

        """
        with self._data_lock:
            return self._metadata.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Get all metadata.

        Returns:
            Dictionary containing all metadata

        Thread Safety:
            Returns a copy of metadata dict to avoid external modification

        Example:
            >>> store = MetadataStore()
            >>> store.set('key1', 'value1')
            >>> store.set('key2', 'value2')
            >>> store.get_all()
            {'key1': 'value1', 'key2': 'value2'}

        """
        with self._data_lock:
            return dict(self._metadata)

    def delete(self, key: str) -> bool:
        """Delete a metadata key.

        Args:
            key: Metadata key to delete

        Returns:
            True if key was deleted, False if not found

        Example:
            >>> store = MetadataStore()
            >>> store.set('temp_key', 'temp_value')
            >>> store.delete('temp_key')
            True
            >>> store.delete('nonexistent')
            False

        """
        with self._data_lock:
            if key in self._metadata:
                del self._metadata[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all metadata.

        Useful for testing or between Lambda invocations.
        """
        with self._data_lock:
            self._metadata.clear()

    def update(self, metadata: dict[str, Any]) -> None:
        """Update multiple metadata key-value pairs.

        Args:
            metadata: Dictionary of key-value pairs to update

        Example:
            >>> store = MetadataStore()
            >>> store.update({
            ...     'request_id': 'abc123',
            ...     'user_id': 'user456',
            ...     'retry_count': 3
            ... })

        """
        with self._data_lock:
            self._metadata.update(metadata)


# Module-level singleton instance
_metadata_store_instance = None
_metadata_store_lock = threading.Lock()


def get_metadata_store() -> MetadataStore:
    """Get singleton MetadataStore instance.

    Thread-safe singleton accessor with lazy initialization.

    Returns:
        Singleton MetadataStore instance

    Thread Safety:
        Thread-safe initialization using double-checked locking

    Example:
        >>> from lee.metadata import get_metadata_store
        >>> store = get_metadata_store()
        >>> store.set('request_id', 'abc123')

    """
    global _metadata_store_instance

    if _metadata_store_instance is None:
        with _metadata_store_lock:
            # Double-check lock pattern
            if _metadata_store_instance is None:
                _metadata_store_instance = MetadataStore()

    return _metadata_store_instance


# ===== GATEWAY INTERFACE IMPLEMENTATIONS =====

def _set_metadata_implementation(key: str, value: Any, **kwargs) -> dict:
    """Set metadata key-value pair (gateway interface implementation)."""
    store = get_metadata_store()
    store.set(key, value)
    return {"status": "ok", "message": f"Metadata set: {key}"}

def _get_metadata_implementation(key: str, default: Any = None, **kwargs) -> dict:
    """Get metadata value (gateway interface implementation)."""
    store = get_metadata_store()
    value = store.get(key, default)
    return {"status": "ok", "key": key, "value": value}

def _get_all_metadata_implementation(**kwargs) -> dict:
    """Get all metadata (gateway interface implementation)."""
    store = get_metadata_store()
    metadata = store.get_all()
    return {"status": "ok", "metadata": metadata, "count": len(metadata)}

def _delete_metadata_implementation(key: str, **kwargs) -> dict:
    """Delete metadata key (gateway interface implementation)."""
    store = get_metadata_store()
    deleted = store.delete(key)
    return {"status": "ok", "deleted": deleted, "key": key}

def _clear_metadata_implementation(**kwargs) -> dict:
    """Clear all metadata (gateway interface implementation)."""
    store = get_metadata_store()
    store.clear()
    return {"status": "ok", "message": "Metadata cleared"}

def _update_metadata_implementation(metadata: dict[str, Any], **kwargs) -> dict:
    """Update multiple metadata key-value pairs (gateway interface implementation)."""
    store = get_metadata_store()
    store.update(metadata)
    return {"status": "ok", "message": f"Updated {len(metadata)} metadata entries"}


__all__ = [
    "MetadataStore",
    "_clear_metadata_implementation",
    "_delete_metadata_implementation",
    "_get_all_metadata_implementation",
    "_get_metadata_implementation",
    "_set_metadata_implementation",
    "_update_metadata_implementation",
    "get_metadata_store",
]
