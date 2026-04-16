"""cache_l2_disk_split/disk_io.py

Disk I/O operations for L2 disk cache.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os

from lee.lee_cache.cache_l2_disk_split.models import L2CacheEntry
from lee.lee_security import safe_dumps, safe_loads

try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    execute_operation = None
    GatewayInterface = None

# Hash algorithm for cache keys
HASH_ALGORITHM = "sha256"


class DiskIO:
    """Disk I/O operations for L2 cache."""

    def __init__(self, cache_dir: str):
        """Initialize disk I/O handler.

        Args:
            cache_dir: Directory path for cache storage

        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            # Log warning but don't crash - allow memory-only operation
            pass
            if execute_operation is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_warning",
                        message=f"L2 cache directory unavailable: {self.cache_dir}. Operating in memory-only mode. Error: {e}",
                        extra_context={"operation": "ensure_cache_dir", "cache_dir": self.cache_dir},
                    )
                except (AttributeError, RuntimeError, ValueError, TypeError, KeyError):
                    # Logging unavailable - silent fail (stderr fallback below)
                    pass
            # If gateway is not available, print to stderr
            print(f"WARNING: L2 cache directory unavailable: {self.cache_dir}. Operating in memory-only mode. Error: {e}")

    def get_key_path(self, key: str) -> str:
        """Get file path for a cache key (combined metadata + value file)."""
        key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")

    def get_metadata_path(self, key: str) -> str:
        """Get legacy metadata file path for backward compatibility."""
        key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.meta")

    def get_value_path(self, key: str) -> str:
        """Get legacy value file path for backward compatibility."""
        key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")

    def load_entry(self, key_hash: str, filename: str, correlation_id: str = None) -> L2CacheEntry:
        """Load a cache entry from disk.

        OPTIMIZATION (2026-04-03): Combined file format - single file read per entry
        instead of separate metadata and value files. Reduces file I/O by 50%.
        Supports backward compatibility with old two-file format.

        Args:
            key_hash: Hashed key for the entry
            filename: Cache filename to load
            correlation_id: Optional correlation ID for tracking

        Returns:
            L2CacheEntry if loaded successfully, None if expired or corrupted

        """
        cache_path = os.path.join(self.cache_dir, filename)

        try:
            with open(cache_path, "rb") as f:
                data = f.read()

            # Try to parse as combined JSON format
            try:
                combined_data = json.loads(data.decode('utf-8'))

                # New combined format
                if "metadata" in combined_data and "value_b64" in combined_data:
                    # Decode value from base64
                    value_bytes = base64.b64decode(combined_data["value_b64"])
                    value = safe_loads(value_bytes)

                    # Remove 'value' from metadata if it exists
                    metadata = combined_data["metadata"].copy()
                    metadata.pop('value', None)

                    # Create entry with value as separate parameter
                    entry = L2CacheEntry(
                        key=metadata['key'],
                        value=value,
                        created_at=metadata['created_at'],
                        expires_at=metadata['expires_at'],
                        size_bytes=metadata['size_bytes'],
                        access_count=metadata.get('access_count', 0),
                        last_accessed=metadata.get('last_accessed', 0.0)
                    )

                    # Only return if not expired
                    if not entry.is_expired():
                        return entry
                    else:
                        # Clean up expired entry
                        os.unlink(cache_path)
                        # Also clean up old .meta file if it exists
                        old_meta_path = os.path.join(self.cache_dir, f"{key_hash}.meta")
                        if os.path.exists(old_meta_path):
                            os.unlink(old_meta_path)
                        return None
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                # Not a combined format file - fall through to legacy format
                pass

            # Legacy two-file format
            metadata_path = os.path.join(self.cache_dir, f"{key_hash}.meta")
            if os.path.exists(metadata_path):
                # Load metadata
                with open(metadata_path, encoding='utf-8') as f:
                    json_string = f.read()
                    metadata = execute_operation(GatewayInterface.UTILITY, "json_loads", json_string=json_string)

                # Load value from the .cache file we already read
                value = safe_loads(data)

                # Remove 'value' from metadata if it exists (shouldn't be there in legacy format)
                metadata.pop('value', None)

                # Create entry with value as separate parameter
                entry = L2CacheEntry(
                    key=metadata['key'],
                    value=value,
                    created_at=metadata['created_at'],
                    expires_at=metadata['expires_at'],
                    size_bytes=metadata['size_bytes'],
                    access_count=metadata.get('access_count', 0),
                    last_accessed=metadata.get('last_accessed', 0.0)
                )

                # Only return if not expired
                if not entry.is_expired():
                    return entry
                else:
                    # Clean up expired entry
                    os.unlink(cache_path)
                    os.unlink(metadata_path)
                    return None

        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            # Skip corrupted entries
            return None

    def save_entry(self, entry: L2CacheEntry, correlation_id: str = None) -> bool:
        """Save a cache entry to disk.

        OPTIMIZATION (2026-04-03): Combined file format - single file write per entry
        instead of separate metadata and value files. Reduces file I/O by 50%.

        Args:
            entry: Cache entry to save
            correlation_id: Optional correlation ID for tracking

        Returns:
            True if saved successfully, False otherwise

        """
        key_hash = hashlib.new(HASH_ALGORITHM, entry.key.encode()).hexdigest()
        cache_path = self.get_key_path(key_hash)
        old_metadata_path = self.get_metadata_path(key_hash)

        # Atomic write with temporary file
        temp_cache_path = cache_path + ".tmp"

        try:
            # Serialize value using SecurePickle
            value_bytes = safe_dumps(entry.value)

            # Create metadata dict without the value field
            metadata_dict = entry.to_dict()
            metadata_dict.pop('value', None)  # Remove value from metadata

            # Create combined format: {"metadata": {...}, "value_b64": "<base64_value>"}
            combined_data = {
                "metadata": metadata_dict,
                "value_b64": base64.b64encode(value_bytes).decode('utf-8')
            }

            # Write combined data as JSON
            json_string = execute_operation(GatewayInterface.UTILITY, "json_dumps", obj=combined_data)
            with open(temp_cache_path, "w", encoding='utf-8') as f:
                f.write(json_string)

            # Atomic rename
            os.replace(temp_cache_path, cache_path)

            # Clean up old metadata file if it exists (migration cleanup)
            if os.path.exists(old_metadata_path):
                try:
                    os.unlink(old_metadata_path)
                except OSError:
                    # Old metadata file cleanup failed - not critical
                    pass

            return True
        except (OSError, ValueError):
            # Clean up temp file on failure
            pass
            try:
                if os.path.exists(temp_cache_path):
                    os.unlink(temp_cache_path)
            except OSError:
                # File doesn't exist or can't be deleted - continue
                pass
            raise

    def delete_entry_files(self, key_hash: str, correlation_id: str = None) -> None:
        """Delete entry files from disk.

        OPTIMIZATION (2026-04-03): Handle both combined format and legacy two-file format.

        Args:
            key_hash: Hashed key for the entry to delete
            correlation_id: Optional correlation ID for tracking

        """
        cache_path = self.get_key_path(key_hash)
        old_metadata_path = self.get_metadata_path(key_hash)

        # Delete combined format file (or old value file)
        if os.path.exists(cache_path):
            os.unlink(cache_path)

        # Delete old metadata file if it exists (legacy format)
        if os.path.exists(old_metadata_path):
            os.unlink(old_metadata_path)

    def clear_all_files(self, correlation_id: str = None) -> bool:
        """Clear all cache files from disk.

        Args:
            correlation_id: Optional correlation ID for tracking

        Returns:
            True if cleared successfully, False otherwise

        """
        try:
            # Delete all files in cache directory (both combined and legacy formats)
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".cache") or filename.endswith(".meta"):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.unlink(file_path)

            return True
        except OSError:
            return False

    def list_cache_files(self) -> list[str]:
        """List all cache files in the cache directory.

        Returns:
            List of cache filenames

        """
        try:
            return [
                filename for filename in os.listdir(self.cache_dir)
                if filename.endswith(".cache")
            ]
        except OSError:
            return []
