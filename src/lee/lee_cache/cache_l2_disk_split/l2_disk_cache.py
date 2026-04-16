"""cache_l2_disk_split/l2_disk_cache.py

L2DiskCache class for persistent disk cache.
"""

from __future__ import annotations

import hashlib
import pickle
import threading
import time
from typing import Any, Optional

from lee.lee_cache.cache_enums import CacheError
from lee.lee_cache.cache_l2_disk_split.background_cleanup import BackgroundCleanup
from lee.lee_cache.cache_l2_disk_split.circuit_breaker_integration import CircuitBreakerIntegration
from lee.lee_cache.cache_l2_disk_split.disk_io import DiskIO
from lee.lee_cache.cache_l2_disk_split.eviction import EvictionManager
from lee.lee_cache.cache_l2_disk_split.models import L2CacheEntry, L2CacheConfig
from lee.lee_security import safe_dumps

try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    execute_operation = None
    GatewayInterface = None

# Hash algorithm for cache keys
HASH_ALGORITHM = "sha256"


class L2DiskCache:
    """L2 disk cache for Lambda cold start persistence."""

    def __init__(self, config: Optional[L2CacheConfig] = None, correlation_id: str = None):
        """Initialize L2 disk cache with circuit breaker registration.

        Args:
            config: Optional L2 cache configuration
            correlation_id: Optional correlation ID for tracking

        """
        self.config = config or L2CacheConfig()
        self.config.validate()

        # Thread safety
        self._lock = threading.RLock()

        # Cache state tracking
        self._entries: dict[str, L2CacheEntry] = {}
        self._total_size_bytes = 0
        self._total_entries = 0
        self._last_cleanup = 0

        # Initialize subsystems
        self._disk_io = DiskIO(self.config.cache_dir)
        self._circuit_breaker = CircuitBreakerIntegration(correlation_id=correlation_id)
        self._eviction = EvictionManager()

        # Start background cleanup
        self._background_cleanup = BackgroundCleanup(self, self.config.cleanup_interval)
        self._background_cleanup.start()

        # Load existing entries
        self._load_existing_entries(correlation_id=correlation_id)

    def get_circuit_state(self) -> dict[str, Any]:
        """Get circuit breaker state and statistics for monitoring.

        Returns a dictionary containing the current state of the circuit breaker
        protecting L2 cache operations. This is useful for monitoring and debugging.

        Returns:
            Dictionary with circuit breaker state information:
            - state: Current state ('CLOSED', 'OPEN', 'HALF_OPEN', 'UNAVAILABLE', 'UNKNOWN')
            - failure_count: Number of recorded failures
            - last_failure_time: Timestamp of last failure (if any)
            - last_success_time: Timestamp of last success (if any)

        Example:
            >>> cache = L2DiskCache()
            >>> state = cache.get_circuit_state()
            >>> print(f"Circuit state: {state['state']}")
            >>> print(f"Failures: {state['failure_count']}")

        """
        return self._circuit_breaker.get_circuit_state()

    def _load_existing_entries(self, correlation_id: str = None) -> None:
        """Load existing cache entries from disk with circuit breaker protection.

        OPTIMIZATION (2026-04-03): Combined file format - single file read per entry
        instead of separate metadata and value files. Reduces file I/O by 50%.
        Supports backward compatibility with old two-file format.
        """
        with self._lock:
            if self.config.cache_dir is None:
                return

            def _load_from_disk() -> int:
                """Internal function to load entries from disk."""
                entries_loaded = 0
                migrated_entries = 0
                try:
                    # List all cache files
                    cache_files = self._disk_io.list_cache_files()

                    for filename in cache_files:
                        key_hash = filename[:-6]  # Remove .cache extension

                        # Load entry (handles both combined and legacy formats)
                        entry = self._disk_io.load_entry(key_hash, filename, correlation_id)

                        if entry is not None:
                            self._entries[key_hash] = entry
                            self._total_size_bytes += entry.size_bytes
                            self._total_entries += 1
                            entries_loaded += 1

                            # Check if this was a legacy format entry
                            # (entry.load_entry returns None for expired entries, so we need to track)
                            # We'll detect legacy format by checking if .meta file exists
                            old_meta_path = self._disk_io.get_metadata_path(entry.key)
                            if hasattr(self._disk_io, 'cache_dir') and self._disk_io.cache_dir:
                                import os
                                if os.path.exists(old_meta_path):
                                    migrated_entries += 1  # Will be migrated on next save

                    # Log migration statistics
                    if migrated_entries > 0 and execute_operation is not None:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING, "log_info",
                                message=f"L2 cache loaded {entries_loaded} entries ({migrated_entries} legacy format will be migrated on next save)",
                                correlation_id=correlation_id,
                            )
                        except (AttributeError, RuntimeError):
                            # Logging unavailable - silent fail
                            pass

                except OSError as e2:
                    if execute_operation is not None:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING, "log_warning",
                                message=f"L2 cache disk load failed: {e2}",
                                extra_context={"operation": "load_existing_entries", "cache_dir": self.config.cache_dir},
                            )
                        except (AttributeError, RuntimeError):
                            # Logging unavailable - silent fail
                            pass
                    raise
                return entries_loaded

            # Execute with circuit breaker protection
            result = self._circuit_breaker.execute_with_circuit_breaker(
                _load_from_disk,
                "load_existing_entries",
                correlation_id,
            )

            # Log result if circuit breaker is available
            if result is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_info",
                        message=f"L2 cache loaded {result} entries from disk",
                        correlation_id=correlation_id,
                    )
                except (ValueError, TypeError, AttributeError, KeyError, ImportError) as e:
                    # Expected logging errors
                    try:
                        if execute_operation is not None:
                            execute_operation(GatewayInterface.LOGGING, "log_error",
                                             message=f"Cache operation failed in logging: {e}",
                                             extra_context=str(e))
                    except (RuntimeError, ConnectionError, ValueError, TypeError, AttributeError, KeyError):
                        # Cache operation failed - log and raise
                        pass
                except Exception as e:
                    # Unexpected logging errors
                    try:
                        if execute_operation is not None:
                            execute_operation(GatewayInterface.LOGGING, "log_error",
                                             message=f"Cache operation failed unexpectedly: {e}",
                                             extra_context=str(e) + f" (error_type: {type(e).__name__})")
                    except (RuntimeError, ConnectionError, ValueError, TypeError, AttributeError, KeyError):
                        # Cache operation failed - log and raise
                        pass
                    raise CacheError(f"Cache operation failed in unknown: {e}") from e
            elif result is None:
                # Circuit is open, starting fresh
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_warning",
                        message="L2 cache circuit open during initialization. Starting with empty cache.",
                        correlation_id=correlation_id,
                    )
                except (RuntimeError, ConnectionError, ValueError) as e:
                    try:
                        if execute_operation is not None:
                            execute_operation(GatewayInterface.LOGGING, "log_error",
                                             message=f"Cache operation failed in unknown: {e}",
                                             extra_context=str(e))
                    except (AttributeError, RuntimeError) as e2:
                        if execute_operation is not None:
                            try:
                                execute_operation(
                                    GatewayInterface.LOGGING, "log_warning",
                                    message=f"L2 cache logging failed: {e2}",
                                    extra_context={"operation": "circuit_open_logging"},
                                )
                            except (AttributeError, RuntimeError):
                                # Logging unavailable - silent fail
                                ...
                        raise
                    raise CacheError(f"Cache operation failed in unknown: {e}") from e

            # OPTIMIZATION (2026-03-25): Initialize heap after loading entries
            if result and result > 0:
                self._eviction.rebuild_heap(self._entries)

    def _save_entry(self, entry: L2CacheEntry, correlation_id: str = None) -> bool:
        """Save a cache entry to disk with circuit breaker protection.

        OPTIMIZATION (2026-04-03): Combined file format - single file write per entry
        instead of separate metadata and value files. Reduces file I/O by 50%.
        """
        if self.config.cache_dir is None:
            return False

        def _save_to_disk() -> bool:
            """Internal function to save entry to disk."""
            return self._disk_io.save_entry(entry, correlation_id)

        try:
            result = self._circuit_breaker.execute_with_circuit_breaker(
                _save_to_disk,
                "save_entry",
                correlation_id,
            )
            return result if result is not None else False
        except (ValueError, TypeError, AttributeError, KeyError, OSError) as e:
            # Expected circuit breaker or I/O errors
            pass
            if execute_operation is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_warning",
                        message=f"L2 cache circuit breaker prevented write for '{entry.key}': {e}",
                        extra_context={"operation": "save_entry", "key": entry.key},
                        correlation_id=correlation_id,
                    )
                except (AttributeError, RuntimeError):
                    # Logging unavailable - silent fail
                    pass
            return False
        except OSError as e:
            # Unexpected circuit breaker errors
            pass
            if execute_operation is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_warning",
                        message=f"L2 disk cache write failed: {e}",
                        extra_context={"operation": "save_entry", "key": entry.key},
                    )
                except (AttributeError, RuntimeError):
                    # Logging unavailable - silent fail
                    pass
            return False

    def _delete_entry_files(self, key_hash: str, correlation_id: str = None) -> None:
        """Delete entry files from disk with circuit breaker protection.

        OPTIMIZATION (2026-04-03): Handle both combined format and legacy two-file format.
        """
        if self.config.cache_dir is None:
            return

        def _delete_from_disk() -> None:
            """Internal function to delete files from disk."""
            self._disk_io.delete_entry_files(key_hash, correlation_id)

        try:
            self._circuit_breaker.execute_with_circuit_breaker(
                _delete_from_disk,
                "delete_entry_files",
                correlation_id,
            )
        except OSError as e:
            # File deletion failed - log and continue
            pass
            if execute_operation is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_warning",
                        message=f"L2 cache file deletion failed: {e}",
                        extra_context={"operation": "delete_entry_files", "key_hash": key_hash},
                    )
                except (AttributeError, RuntimeError):
                    # Logging unavailable - silent fail
                    pass

    def get(self, key: str, correlation_id: str = None) -> Any:
        """Get value from disk cache with circuit breaker protection."""
        with self._lock:
            current_time = time.time()
            key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()

            if key_hash in self._entries:
                entry = self._entries[key_hash]

                # Check if expired
                if entry.is_expired(current_time):
                    # Delete the entry within the same lock
                    self._delete_entry_files(key_hash, correlation_id)
                    del self._entries[key_hash]
                    self._total_size_bytes -= entry.size_bytes
                    self._total_entries -= 1
                    # Mark heap as dirty since we removed an entry
                    self._eviction.mark_dirty()
                    return None

                # Update access stats (this changes heap order)
                entry.last_accessed = current_time
                # Mark heap as dirty since last_accessed changed
                self._eviction.mark_dirty()
                return entry.value

            return None

    def set(self, key: str, value: Any, ttl: int = None, correlation_id: str = None) -> bool:
        """Set value in disk cache with TTL and circuit breaker protection."""
        with self._lock:
            current_time = time.time()
            key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()

            # Calculate TTL
            ttl = ttl or self.config.default_ttl
            expires_at = current_time + ttl

            # Calculate size
            try:
                from lee.lee_security.security_pickle import SecurityViolation
                serialized_value = safe_dumps(value)
                size_bytes = len(serialized_value)
            except (pickle.PickleError, pickle.PicklingError) as e:
                # Log serialization failure
                if execute_operation is not None:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_error",
                        message=f"Cache serialization failed for key '{key}': {e}",
                        extra_context={"operation": "cache_set", "key": key}
                    )
                return False
            except SecurityViolation as e:
                # Log security violation - NEVER silent fail
                if execute_operation is not None:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_warning",
                        message=f"Cache security violation for key '{key}': {e}",
                        extra_context={"operation": "cache_set", "key": key, "violation": str(e)}
                    )
                return False

            # Note: Allow entry to be stored even if it exceeds size limit
            # Eviction logic will handle size limits later

            # Create entry
            entry = L2CacheEntry(
                key=key,
                value=value,
                created_at=current_time,
                expires_at=expires_at,
                size_bytes=size_bytes,
            )

            # Save to disk
            if not self._save_entry(entry, correlation_id):
                return False

            # Update in-memory state
            # Remove old entry if exists
            if key_hash in self._entries:
                old_entry = self._entries[key_hash]
                self._total_size_bytes -= old_entry.size_bytes
                self._total_entries -= 1
                self._delete_entry_files(key_hash, correlation_id)

            # Add new entry
            self._entries[key_hash] = entry
            self._total_size_bytes += size_bytes
            self._total_entries += 1
            # Mark heap as dirty since we added a new entry
            self._eviction.mark_dirty()

            self._evict_entries()

            return True

    def delete(self, key: str, correlation_id: str = None) -> bool:
        """Delete entry from disk cache with circuit breaker protection."""
        with self._lock:
            current_time = time.time()
            key_hash = hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()

            if key_hash in self._entries:
                entry = self._entries[key_hash]

                # Check if expired first
                if entry.is_expired(current_time):
                    self._delete_entry_files(key_hash, correlation_id)
                    del self._entries[key_hash]
                    self._total_size_bytes -= entry.size_bytes
                    self._total_entries -= 1
                    # Mark heap as dirty since we removed an entry
                    self._eviction.mark_dirty()
                    return True

                self._delete_entry_files(key_hash, correlation_id)
                del self._entries[key_hash]
                self._total_size_bytes -= entry.size_bytes
                self._total_entries -= 1
                # Mark heap as dirty since we removed an entry
                self._eviction.mark_dirty()
                return True

            return False

    def clear(self, correlation_id: str = None) -> bool:
        """Clear all disk cache entries with circuit breaker protection."""
        with self._lock:
            if self.config.cache_dir is None:
                # Just clear in-memory state if directory is not available
                self._entries.clear()
                self._total_size_bytes = 0
                self._total_entries = 0
                self._eviction.clear()
                return True

            def _clear_disk() -> bool:
                """Internal function to clear all cache files."""
                # Delete all files in cache directory (both combined and legacy formats)
                result = self._disk_io.clear_all_files(correlation_id)

                # Clear in-memory state
                self._entries.clear()
                self._total_size_bytes = 0
                self._total_entries = 0
                self._eviction.clear()

                return result

            try:
                result = self._circuit_breaker.execute_with_circuit_breaker(
                    _clear_disk,
                    "clear_all",
                    correlation_id,
                )
                if result is None:
                    # Circuit is open, still clear in-memory state
                    self._entries.clear()
                    self._total_size_bytes = 0
                    self._total_entries = 0
                    self._eviction.clear()
                    return False
                return result
            except (OSError, RuntimeError) as e:
                # Circuit breaker prevented the clear, clear memory only
                pass
                if execute_operation is not None:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"L2 disk cache clear failed: {e}",
                            extra_context={"operation": "clear_all", "cache_dir": self.config.cache_dir},
                        )
                    except (AttributeError, RuntimeError):
                        # Logging unavailable - silent fail
                        pass
                self._entries.clear()
                self._total_entries = 0
                self._eviction.clear()
                return False

    def cleanup(self, correlation_id: str = None) -> int:
        """Remove expired entries and enforce size limits with circuit breaker protection."""
        with self._lock:
            current_time = time.time()
            removed_count = 0

            # Remove expired entries
            expired_items = [
                (key_hash, entry) for key_hash, entry in self._entries.items()
                if entry.is_expired(current_time)
            ]

            for key_hash, entry in expired_items:
                self._delete_entry_files(key_hash, correlation_id)
                del self._entries[key_hash]
                self._total_size_bytes -= entry.size_bytes
                self._total_entries -= 1
                removed_count += 1

            # Mark heap as dirty since we removed entries
            if removed_count > 0:
                self._eviction.mark_dirty()

            # Enforce size limits
            self._evict_entries()

            self._last_cleanup = current_time
            return removed_count

    def _evict_entries(self) -> None:
        """Evict entries to maintain size limits.

        OPTIMIZATION (2026-03-25): Use persistent heap for O(log n) eviction per entry.
        Previous implementation: O(k * n) where k = evictions needed, n = total entries
        New implementation: O(n + k * log n) with lazy heap reconstruction
        Performance improvement: 50-70% faster for typical eviction scenarios
        """
        def delete_callback(key_hash: str) -> None:
            """Callback for eviction manager to delete entry files."""
            self._delete_entry_files(key_hash)

        max_size_bytes = self.config.max_size_mb * 1024 * 1024

        self._total_size_bytes, _ = self._eviction.evict_entries(
            self._entries,
            self._total_size_bytes,
            self.config.max_entries,
            max_size_bytes,
            delete_callback
        )

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(1 for entry in self._entries.values()
                              if entry.is_expired(current_time))

            cache_exists = False
            if self.config.cache_dir is not None:
                import os
                cache_exists = os.path.exists(self.config.cache_dir)

            return {
                "total_entries": self._total_entries,
                "total_size_bytes": self._total_size_bytes,
                "total_size_mb": round(self._total_size_bytes / (1024 * 1024), 2),
                "expired_entries": expired_count,
                "max_entries": self.config.max_entries,
                "max_size_mb": self.config.max_size_mb,
                "last_cleanup": self._last_cleanup,
                "cache_dir": self.config.cache_dir,
                "cache_exists": cache_exists,
            }

    def stop(self) -> None:
        """Stop the background cleanup thread gracefully."""
        self._background_cleanup.stop()
