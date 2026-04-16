"""Cache Invalidation System for LEE.

Provides tag-based, wildcard, and dependency tracking cache invalidation.
Implements efficient invalidation strategies with O(1) tag lookup and O(n) pattern matching.

Classes:
    TagRegistry: Manages key-to-tag mappings
    DependencyGraph: Tracks module dependencies
    InvalidationResult: Reports invalidation outcomes
    CacheInvalidator: Main invalidation orchestrator
"""

from __future__ import annotations

import fnmatch
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import RLock
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


class InvalidationStatus(Enum):
    """Status of invalidation operations."""

    SUCCESS = "success"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class InvalidationResult:
    """Result of a cache invalidation operation.

    Attributes:
        status: Operation status
        keys_invalidated: Set of keys that were invalidated
        keys_failed: Set of keys that failed invalidation
        pattern: Pattern or criteria used (for logging)
        duration_ms: Operation duration in milliseconds
        message: Human-readable result message

    """

    status: InvalidationStatus
    keys_invalidated: set[str] = field(default_factory=set)
    keys_failed: set[str] = field(default_factory=set)
    pattern: str = ""
    duration_ms: float = 0.0
    message: str = ""

    def __post_init__(self):
        """Validate result state."""
        if self.status == InvalidationStatus.SUCCESS and not self.keys_invalidated:
            self.message = "Invalidation succeeded but no keys matched"

    @property
    def total_keys(self) -> int:
        """Total number of keys affected."""
        return len(self.keys_invalidated) + len(self.keys_failed)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)."""
        if self.total_keys == 0:
            return 0.0
        return (len(self.keys_invalidated) / self.total_keys) * 100


class TagRegistry:
    """Registry for managing cache key tags with O(1) lookup.

    Maintains bidirectional mappings between keys and tags for efficient
    tag-based invalidation operations.

    Thread-safe for concurrent access.
    Implements rolling window to limit unbounded growth.
    """

    def __init__(self, max_tags: int = 1000):
        """Initialize tag registry with rolling window.

        Args:
            max_tags: Maximum number of unique tags to track
        """
        self._key_to_tags: dict[str, set[str]] = {}
        self._tag_to_keys: dict[str, set[str]] = {}
        self._tag_order: deque[str] = deque(maxlen=max_tags)
        self._max_tags = max_tags
        self._lock = RLock()

    def register_tags(self, key: str, tags: set[str]) -> None:
        """Register tags for a cache key.

        Replaces existing tags for the key.

            key: Cache key
            tags: Set of tags to associate with key

        """
        with self._lock:
            # Remove old tag associations
            if key in self._key_to_tags:
                for old_tag in self._key_to_tags[key]:
                    if old_tag in self._tag_to_keys:
                        self._tag_to_keys[old_tag].discard(key)
                        if not self._tag_to_keys[old_tag]:
                            del self._tag_to_keys[old_tag]

            # Add new tag associations
            self._key_to_tags[key] = tags.copy()
            for tag in tags:
                if tag not in self._tag_to_keys:
                    # Check if we need to evict oldest tag
                    if len(self._tag_order) >= self._max_tags and tag not in self._tag_order:
                        oldest = self._tag_order[0]
                        if oldest in self._tag_to_keys:
                            for key_to_remove in list(self._tag_to_keys[oldest]):
                                if key_to_remove in self._key_to_tags:
                                    self._key_to_tags[key_to_remove].discard(oldest)
                            del self._tag_to_keys[oldest]
                    self._tag_order.append(tag)
                    self._tag_to_keys[tag] = set()
                self._tag_to_keys[tag].add(key)

    def unregister_key(self, key: str) -> None:
        """Remove all tags for a cache key.

            key: Cache key to remove

        """
        with self._lock:
            if key in self._key_to_tags:
                for tag in self._key_to_tags[key]:
                    if tag in self._tag_to_keys:
                        self._tag_to_keys[tag].discard(key)
                        if not self._tag_to_keys[tag]:
                            del self._tag_to_keys[tag]
                del self._key_to_tags[key]

    def get_keys_by_tag(self, tag: str) -> set[str]:
        """Get all keys associated with a tag.

            tag: Tag to query

            Set of cache keys with this tag

        """
        with self._lock:
            return self._tag_to_keys.get(tag, set()).copy()

    def get_tags_for_key(self, key: str) -> set[str]:
        """Get all tags for a cache key.

            key: Cache key to query

            Set of tags for this key

        """
        with self._lock:
            return self._key_to_tags.get(key, set()).copy()

    def clear(self) -> None:
        """Clear all tag mappings."""
        with self._lock:
            self._key_to_tags.clear()
            self._tag_to_keys.clear()

    @property
    def total_keys(self) -> int:
        """Total number of registered keys."""
        with self._lock:
            return len(self._key_to_tags)

    @property
    def total_tags(self) -> int:
        """Total number of unique tags."""
        with self._lock:
            return len(self._tag_to_keys)


class DependencyGraph:
    """Graph for tracking cache key dependencies by module.

    Maintains module-to-keys mappings to enable module-level invalidation.

    Thread-safe for concurrent access.
    Implements rolling window to limit unbounded growth.
    """

    def __init__(self, max_modules: int = 500):
        """Initialize dependency graph with rolling window.

        Args:
            max_modules: Maximum number of unique modules to track
        """
        self._module_to_keys: dict[str, set[str]] = {}
        self._key_to_modules: dict[str, set[str]] = {}
        self._module_order: deque[str] = deque(maxlen=max_modules)
        self._max_modules = max_modules
        self._lock = RLock()

    def register_key(self, key: str, module: str) -> None:
        """Register a cache key with its source module.

            key: Cache key
            module: Module name that created this key

        """
        with self._lock:
            # Remove old module associations
            if key in self._key_to_modules:
                for old_module in self._key_to_modules[key]:
                    if old_module in self._module_to_keys:
                        self._module_to_keys[old_module].discard(key)
                        if not self._module_to_keys[old_module]:
                            del self._module_to_keys[old_module]

            # Add new module association
            self._key_to_modules[key] = {module}
            if module not in self._module_to_keys:
                # Check if we need to evict oldest module
                if len(self._module_order) >= self._max_modules and module not in self._module_order:
                    oldest = self._module_order[0]
                    if oldest in self._module_to_keys:
                        for key_to_remove in list(self._module_to_keys[oldest]):
                            if key_to_remove in self._key_to_modules:
                                self._key_to_modules[key_to_remove].discard(oldest)
                        del self._module_to_keys[oldest]
                self._module_order.append(module)
                self._module_to_keys[module] = set()
            self._module_to_keys[module].add(key)

    def unregister_key(self, key: str) -> None:
        """Remove a cache key from all modules.

            key: Cache key to remove

        """
        with self._lock:
            if key in self._key_to_modules:
                for module in self._key_to_modules[key]:
                    if module in self._module_to_keys:
                        self._module_to_keys[module].discard(key)
                        if not self._module_to_keys[module]:
                            del self._module_to_keys[module]
                del self._key_to_modules[key]

    def get_keys_by_module(self, module: str) -> set[str]:
        """Get all keys from a specific module.

            module: Module name to query

            Set of cache keys from this module

        """
        with self._lock:
            return self._module_to_keys.get(module, set()).copy()

    def get_modules_for_key(self, key: str) -> set[str]:
        """Get modules associated with a cache key.

            key: Cache key to query

            Set of module names for this key

        """
        with self._lock:
            return self._key_to_modules.get(key, set()).copy()

    def clear(self) -> None:
        """Clear all dependency mappings."""
        with self._lock:
            self._module_to_keys.clear()
            self._key_to_modules.clear()

    @property
    def total_keys(self) -> int:
        """Total number of registered keys."""
        with self._lock:
            return len(self._key_to_modules)

    @property
    def total_modules(self) -> int:
        """Total number of unique modules."""
        with self._lock:
            return len(self._module_to_keys)


class CacheInvalidator:
    """Cache invalidation orchestrator with multiple strategies.

    Supports three invalidation strategies:
    - Tag-based: Invalidate all keys with specific tags
    - Wildcard: Invalidate keys matching glob patterns
    - Module: Invalidate all keys from a specific module

    Thread-safe singleton implementation.
    """

    _instance: Optional[CacheInvalidator] = None
    _initialized: bool = False
    _lock = RLock()

    def __new__(cls) -> CacheInvalidator:
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize cache invalidator (only once)."""
        if self._initialized:
            return

        self._tag_registry = TagRegistry()
        self._dependency_graph = DependencyGraph()
        self._invalidate_callback: Optional[callable] = None
        self._initialized = True

    def set_invalidate_callback(self, callback: callable) -> None:
        """Set callback function for actual cache invalidation.

        The callback should accept a single key argument and return
        True if successful, False otherwise.

            callback: Function to call for each key invalidation

        """
        self._invalidate_callback = callback

    def register_tags(self, key: str, tags: set[str], module: Optional[str] = None) -> None:
        """Register a cache key with tags and optional module.

            key: Cache key
            tags: Set of tags to associate with key
            module: Optional module name for dependency tracking

        """
        self._tag_registry.register_tags(key, tags)
        if module:
            self._dependency_graph.register_key(key, module)

    def unregister_key(self, key: str) -> None:
        """Unregister a cache key from all tracking systems.

            key: Cache key to remove

        """
        self._tag_registry.unregister_key(key)
        self._dependency_graph.unregister_key(key)

    def invalidate_by_tag(self, tag: str, _correlation_id: Optional[str] = None) -> InvalidationResult:
        """Invalidate all cache keys with a specific tag.


            tag: Tag to invalidate
            correlation_id: Optional correlation ID for tracking

            InvalidationResult with details

        """
        start_time = datetime.now()

        try:
            keys = self._tag_registry.get_keys_by_tag(tag)

            if not keys:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                return InvalidationResult(
                    status=InvalidationStatus.NOT_FOUND,
                    pattern=tag,
                    duration_ms=duration_ms,
                    message=f"No keys found with tag '{tag}'",
                )

            keys_invalidated = set()
            keys_failed = set()

            for key in keys:
                try:
                    if self._invalidate_callback:
                        success = self._invalidate_callback(key)
                        if success:
                            keys_invalidated.add(key)
                        else:
                            keys_failed.add(key)
                    else:
                        # No callback set, assume success
                        keys_invalidated.add(key)
                except Exception as exc:
                    keys_failed.add(key)
                    try:
                        from lee.gateway import GatewayInterface as GII, execute_operation as eo  # pylint: disable=import-outside-toplevel,reimported
                        eo(
                            GII.LOGGING, "log_warning",
                            message=f"Cache invalidation failed for key: {exc}",
                            extra_context={"operation": "invalidate_by_tag", "tag": tag, "key": key},
                        )
                    except ImportError as inner_e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_warning',
                                message=f'Module import failed: {inner_e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            status = InvalidationStatus.SUCCESS
            if keys_failed:
                status = InvalidationStatus.PARTIAL

            return InvalidationResult(
                status=status,
                keys_invalidated=keys_invalidated,
                keys_failed=keys_failed,
                pattern=tag,
                duration_ms=duration_ms,
                message=f"Invalidated {len(keys_invalidated)} keys with tag '{tag}'",
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return InvalidationResult(
                status=InvalidationStatus.ERROR,
                pattern=tag,
                duration_ms=duration_ms,
                message=f"Error invalidating by tag: {e!s}",
            )

    def invalidate_by_pattern(self, pattern: str, _correlation_id: Optional[str] = None) -> InvalidationResult:
        """Invalidate cache keys matching a glob pattern.

        Uses fnmatch for Unix-style glob patterns (supports *, ?, [], [!]).

            pattern: Glob pattern (e.g., 'user:*:session', 'config:*')
            correlation_id: Optional correlation ID for tracking

            InvalidationResult with details

        """
        start_time = datetime.now()

        try:
            # Get all registered keys from tag registry and invalidate within lock
            # CRITICAL: Hold lock throughout to prevent race conditions
            # pylint: disable=protected-access
            with self._tag_registry._lock:
                all_keys = set(self._tag_registry._key_to_tags.keys())

                # Match keys against pattern
                matching_keys = {key for key in all_keys if fnmatch.fnmatch(key, pattern)}

                if not matching_keys:
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                    return InvalidationResult(
                        status=InvalidationStatus.NOT_FOUND,
                        pattern=pattern,
                        duration_ms=duration_ms,
                        message=f"No keys found matching pattern '{pattern}'",
                    )

                keys_invalidated = set()
                keys_failed = set()

                # Invalidate matching keys while holding lock
                for key in matching_keys:
                    try:
                        if self._invalidate_callback:
                            success = self._invalidate_callback(key)
                            if success:
                                keys_invalidated.add(key)
                            else:
                                keys_failed.add(key)
                        else:
                            # No callback set, assume success
                            keys_invalidated.add(key)
                    except Exception as exc:
                        keys_failed.add(key)
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING, "log_warning",
                                message=f"Cache invalidation failed for key: {exc}",
                                extra_context={"operation": "invalidate_by_pattern", "pattern": pattern, "key": key},
                            )
                        except ImportError as inner_e:
                            try:
                                execute_operation(
                                    GatewayInterface.LOGGING,
                                    'log_warning',
                                    message=f'Module import failed: {inner_e}',
                                    corr_id=None
                                )
                            except (ImportError, AttributeError, RuntimeError):
                                pass  # Gateway not available

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            status = InvalidationStatus.SUCCESS
            if keys_failed:
                status = InvalidationStatus.PARTIAL

            return InvalidationResult(
                status=status,
                keys_invalidated=keys_invalidated,
                keys_failed=keys_failed,
                pattern=pattern,
                duration_ms=duration_ms,
                message=f"Invalidated {len(keys_invalidated)} keys matching pattern '{pattern}'",
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return InvalidationResult(
                status=InvalidationStatus.ERROR,
                pattern=pattern,
                duration_ms=duration_ms,
                message=f"Error invalidating by pattern: {e!s}",
            )

    def invalidate_by_module(self, module: str, _correlation_id: Optional[str] = None) -> InvalidationResult:
        """Invalidate all cache keys from a specific module.


            module: Module name to invalidate
            correlation_id: Optional correlation ID for tracking

            InvalidationResult with details

        """
        start_time = datetime.now()

        try:
            keys = self._dependency_graph.get_keys_by_module(module)

            if not keys:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                return InvalidationResult(
                    status=InvalidationStatus.NOT_FOUND,
                    pattern=module,
                    duration_ms=duration_ms,
                    message=f"No keys found from module '{module}'",
                )

            keys_invalidated = set()
            keys_failed = set()

            for key in keys:
                try:
                    if self._invalidate_callback:
                        success = self._invalidate_callback(key)
                        if success:
                            keys_invalidated.add(key)
                        else:
                            keys_failed.add(key)
                    else:
                        # No callback set, assume success
                        keys_invalidated.add(key)
                except Exception as exc:
                    keys_failed.add(key)
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"Cache invalidation failed for key: {exc}",
                            extra_context={"operation": "invalidate_by_module", "module": module, "key": key},
                        )
                    except ImportError as inner_e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_warning',
                                message=f'Module import failed: {inner_e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            status = InvalidationStatus.SUCCESS
            if keys_failed:
                status = InvalidationStatus.PARTIAL

            return InvalidationResult(
                status=status,
                keys_invalidated=keys_invalidated,
                keys_failed=keys_failed,
                pattern=module,
                duration_ms=duration_ms,
                message=f"Invalidated {len(keys_invalidated)} keys from module '{module}'",
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return InvalidationResult(
                status=InvalidationStatus.ERROR,
                pattern=module,
                duration_ms=duration_ms,
                message=f"Error invalidating by module: {e!s}",
            )

    def invalidate_all(self, _correlation_id: Optional[str] = None) -> InvalidationResult:
        """Invalidate all tracked cache keys.

            correlation_id: Optional correlation ID for tracking

            InvalidationResult with details

        """
        start_time = datetime.now()

        try:
            # pylint: disable=protected-access
            with self._tag_registry._lock:
                all_keys = set(self._tag_registry._key_to_tags.keys())

            keys_invalidated = set()
            keys_failed = set()

            for key in all_keys:
                try:
                    if self._invalidate_callback:
                        success = self._invalidate_callback(key)
                        if success:
                            keys_invalidated.add(key)
                        else:
                            keys_failed.add(key)
                    else:
                        # No callback set, assume success
                        keys_invalidated.add(key)
                except Exception as exc:
                    keys_failed.add(key)
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"Cache invalidation failed for key: {exc}",
                            extra_context={"operation": "invalidate_all", "key": key},
                        )
                    except ImportError as inner_e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_warning',
                                message=f'Module import failed: {inner_e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            status = InvalidationStatus.SUCCESS
            if keys_failed:
                status = InvalidationStatus.PARTIAL

            return InvalidationResult(
                status=status,
                keys_invalidated=keys_invalidated,
                keys_failed=keys_failed,
                pattern="*",
                duration_ms=duration_ms,
                message=f"Invalidated all {len(keys_invalidated)} cache keys",
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return InvalidationResult(
                status=InvalidationStatus.ERROR,
                pattern="*",
                duration_ms=duration_ms,
                message=f"Error invalidating all: {e!s}",
            )

    def clear_tracking(self) -> None:
        """Clear all tag and dependency tracking."""
        self._tag_registry.clear()
        self._dependency_graph.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get tracking system statistics.

            Dict with registry and graph statistics

        """
        return {
            "tag_registry": {
                "total_keys": self._tag_registry.total_keys,
                "total_tags": self._tag_registry.total_tags,
            },
            "dependency_graph": {
                "total_keys": self._dependency_graph.total_keys,
                "total_modules": self._dependency_graph.total_modules,
            },
        }


def get_cache_invalidator() -> CacheInvalidator:
    """Get singleton CacheInvalidator instance.

        CacheInvalidator singleton instance

    """
    return CacheInvalidator()
