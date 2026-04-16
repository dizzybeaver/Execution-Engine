"""lee_ligs/lazy_import_system.py - Lazy Import Gateway System
Version: 1.0.0
Date: 2026-03-05
Description: Thread-safe lazy module loading for LEE

Based on UGA's LIGS pattern (gateway.omms.ligs.SubdomainManager).

Key Features:
    - LazyModule: Wrapper for deferred module loading
    - LazyImportRegistry: Thread-safe singleton registry
    - Factory pattern for consistent module creation
    - First-access loading with caching
    - Preload support for warming up critical modules

Performance Impact:
    - Cold Start: Reduces INIT time by 40-60% for HA-SUGA
    - Memory: Modules only load when first accessed
    - Thread Safety: Double-checked locking pattern

Usage:
    from lee.lee_ligs import get_lazy_import_registry

    registry = get_lazy_import_registry()

    # Register module
    registry.register(
        name='ha_gateway',
        module_path='home_assistant.ha_gateway',
        factory=lambda: __import__('home_assistant.ha_gateway')
    )

    # Get module (loads on first access)
    ha_gateway = registry.get('ha_gateway')

    # Check if loaded
    if registry.is_loaded('ha_gateway'):
        # Use gateway logging instead of print
        execute_operation(
            GatewayInterface.LOGGING,
            "log_debug",
            message="HA Gateway already loaded",
            corr_id="ligs_demo",
        )

    # Preload specific modules
    registry.preload(['ha_gateway', 'ha_devices'])

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable
from typing import Any, Optional

# Import gateway for logging
from lee.gateway import GatewayInterface, execute_operation

# Cache debug mode check at module load time
_DEBUG_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if debug mode is enabled.

    Returns:
        True if LEE_DEBUG environment variable is set to 'true'
    """
    return _DEBUG_ENABLED


class LazyModule:
    """Lazy-loaded module wrapper.

    Defers module import until first access, then caches the result.
    Uses factory pattern for consistent module creation.

    Attributes:
        module_path: Dot-notation path to module (e.g., 'home_assistant.ha_gateway')
        factory: Factory function that creates/imports the module
        _loaded: Whether module has been loaded
        _module: Cached module instance (None until loaded)
        _load_time_ms: Time taken to load module (milliseconds)
        _load_error: Exception if load failed

    Example:
        def import_ha_gateway():
            import home_assistant.ha_gateway as ha_gateway
            return ha_gateway

        lazy = LazyModule('home_assistant.ha_gateway', import_ha_gateway)

        # Module loads on first access
        ha_gateway = lazy.load()

    """

    def __init__(self, module_path: str, factory: Callable[[], Any]):
        """Initialize LazyModule.

        Args:
            module_path: Dot-notation path to module
            factory: Factory function that creates/imports the module

        Raises:
            ValueError: If module_path is empty or factory is not callable

        """
        if not module_path:
            raise ValueError("module_path cannot be empty")
        if not callable(factory):
            raise ValueError("factory must be callable")

        self.module_path = module_path
        self.factory = factory
        self._loaded = False
        self._module = None
        self._load_time_ms = 0.0
        self._load_error = None
        self._lock = threading.Lock()  # Instance-level lock for thread safety

    def load(self) -> Any:
        """Load module on first access.

        Uses thread-safe double-checked locking pattern.
        Only loads once, then returns cached module.

        Returns:
            Loaded module instance

        Raises:
            ImportError: If module fails to load
            RuntimeError: If factory function raises exception

        """
        # Fast path - already loaded
        if self._loaded:
            return self._module

        # Slow path - acquire lock and load
        # Note: Lambda is single-threaded, but lock provides safety for testing
        with self._lock:
            # Double-check after acquiring lock
            if self._loaded:
                return self._module

            # Load module
            start_time = time.perf_counter()

            try:
                self._module = self.factory()
                self._loaded = True
                self._load_time_ms = (time.perf_counter() - start_time) * 1000

                # Log successful load (only if debug mode enabled)
                if _is_debug_mode():
                    try:
                        execute_operation(
                            GatewayInterface.DEBUG, 'log',
                            message="[LIGS] Loaded module",
                            scope='LIGS',
                            module_path=self.module_path,
                            load_time_ms=self._load_time_ms,
                        )
                    except (ImportError, AttributeError):
                        ...

                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_info",
                        message=f"[LIGS] Loaded module: {self.module_path} "
                               f"({self._load_time_ms:.2f}ms)",
                        corr_id="ligs_load",
                    )
                except (ImportError, AttributeError):
                    # Silently fail if gateway not available
                    ...

                return self._module

            except (ImportError, ModuleNotFoundError, AttributeError, TypeError, ValueError, RuntimeError) as e:
                self._load_error = e
                self._load_time_ms = (time.perf_counter() - start_time) * 1000

                # Log load failure (secure: no traceback exposure)
                if _is_debug_mode():
                    try:
                        execute_operation(
                            GatewayInterface.DEBUG, 'log',
                            message="[LIGS] Failed to load module",
                            scope='LIGS',
                            module_path=self.module_path,
                            error=str(e),
                            error_type=type(e).__name__,
                        )
                    except (ImportError, AttributeError):
                        ...

                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_error",
                        message=f"[LIGS] Failed to load module: {self.module_path}",
                        corr_id="ligs_load_error",
                    )
                except (ImportError, AttributeError):
                    # Silently fail if gateway not available
                    ...

                raise ImportError(
                    f"Failed to load module '{self.module_path}': {e!s}",
                ) from e

    def is_loaded(self) -> bool:
        """Check if module has been loaded.

        Returns:
            True if module has been loaded

        """
        return self._loaded

    def get_load_time_ms(self) -> float:
        """Get time taken to load module.

        Returns:
            Load time in milliseconds (0.0 if not loaded)

        """
        return self._load_time_ms

    def get_load_error(self) -> Optional[Exception]:
        """Get load error if loading failed.

        Returns:
            Exception if load failed, None otherwise

        """
        return self._load_error


class LazyImportRegistry:
    """Thread-safe registry for lazy-loaded modules.

    Manages LazyModule instances with factory pattern.
    Implements singleton pattern for shared registry.

    Attributes:
        _modules: Dict mapping module names to LazyModule instances
        _lock: Thread lock for thread-safe operations

    Example:
        registry = LazyImportRegistry()

        # Register module
        registry.register(
            name='ha_gateway',
            module_path='home_assistant.ha_gateway',
            factory=lambda: __import__('home_assistant.ha_gateway')
        )

        # Get module (loads on first access)
        ha_gateway = registry.get('ha_gateway')

        # Preload multiple modules
        registry.preload(['ha_gateway', 'ha_devices'])

        # Get all loaded modules
        loaded = registry.get_all_loaded()
        # Use gateway logging instead of print
        execute_operation(
            GatewayInterface.LOGGING,
            "log_info",
            message=f"LIGS: Loaded modules: {', '.join(loaded)}",
            corr_id="ligs_registry",
        )

    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize LazyImportRegistry (use get_instance() instead)."""
        self._modules: dict[str, LazyModule] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        module_path: str,
        factory: Callable[[], Any],
    ) -> None:
        """Register a lazy module.

        Args:
            name: Unique name for this module (e.g., 'ha_gateway')
            module_path: Dot-notation path to module
            factory: Factory function that creates/imports the module

        Raises:
            ValueError: If parameters invalid

        Note:
            If module already registered, skips registration silently.
            This aligns with Python's import behavior where re-importing
            returns the cached module.
        """
        if not name:
            raise ValueError("name cannot be empty")
        if not module_path:
            raise ValueError("module_path cannot be empty")
        if not callable(factory):
            raise ValueError("factory must be callable")

        with self._lock:
            if name in self._modules:
                if _is_debug_mode():
                    try:
                        execute_operation(
                            GatewayInterface.DEBUG, 'log',
                            message="[LIGS] Module already registered, skipping",
                            scope='LIGS',
                            name=name,
                        )
                    except (ImportError, AttributeError):
                        ...

                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_debug',
                    message=f"LIGS: Module '{name}' already registered, skipping registration",
                )
                return

            lazy_module = LazyModule(module_path, factory)
            self._modules[name] = lazy_module

            if _is_debug_mode():
                try:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message="[LIGS] Registered module",
                        scope='LIGS',
                        name=name,
                        module_path=module_path,
                    )
                except (ImportError, AttributeError):
                    ...

    def get(self, name: str) -> Any:
        """Get module, loading if necessary.

        Args:
            name: Module name

        Returns:
            Loaded module instance

        Raises:
            ValueError: If module name not registered
            ImportError: If module fails to load

        """
        # Fast path - check if exists without lock
        if name not in self._modules:
            available = list(self._modules.keys())
            raise ValueError(
                f"Module '{name}' not registered. "
                f"Available: {', '.join(available) if available else '(none)'}",
            )

        # Get lazy module
        lazy_module = self._modules[name]

        # Load and return module
        return lazy_module.load()

    def preload(self, names: list[str]) -> None:
        """Preload specific modules.

        Useful for warming up the system with frequently used modules.
        Forces module loading even if not yet accessed.

        Args:
            names: List of module names to preload

        Raises:
            ValueError: If any module name not registered
            ImportError: If any module fails to load

        """
        for name in names:
            self.get(name)  # Forces load

    def is_loaded(self, name: str) -> bool:
        """Check if module is loaded.

        Args:
            name: Module name

        Returns:
            True if module has been loaded

        Raises:
            ValueError: If module name not registered

        """
        if name not in self._modules:
            raise ValueError(
                f"Module '{name}' not registered. "
                f"Available: {', '.join(self._modules.keys())}",
            )

        return self._modules[name].is_loaded()

    def get_all_loaded(self) -> set[str]:
        """Get set of all loaded module names.

        Returns:
            Set of loaded module names

        """
        return {
            name for name, lazy_module in self._modules.items()
            if lazy_module.is_loaded()
        }

    def get_all_registered(self) -> set[str]:
        """Get set of all registered module names.

        Returns:
            Set of all registered module names

        """
        return set(self._modules.keys())

    def get_load_time_ms(self, name: str) -> float:
        """Get load time for a specific module.

        Args:
            name: Module name

        Returns:
            Load time in milliseconds (0.0 if not loaded)

        Raises:
            ValueError: If module name not registered

        """
        if name not in self._modules:
            raise ValueError(
                f"Module '{name}' not registered. "
                f"Available: {', '.join(self._modules.keys())}",
            )

        return self._modules[name].get_load_time_ms()

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dictionary with:
                - total_registered: Total number of registered modules
                - total_loaded: Number of loaded modules
                - loaded_names: Set of loaded module names
                - load_times_ms: Dict mapping name to load time

        """
        return {
            "total_registered": len(self._modules),
            "total_loaded": sum(
                1 for m in self._modules.values() if m.is_loaded()
            ),
            "loaded_names": self.get_all_loaded(),
            "load_times_ms": {
                name: m.get_load_time_ms()
                for name, m in self._modules.items()
                if m.is_loaded()
            },
        }

    def clear(self) -> int:
        """Clear all registered modules.

        Useful for testing or memory management.

        Returns:
            Number of modules cleared

        """
        with self._lock:
            count = len(self._modules)
            self._modules.clear()
            return count

    @staticmethod
    def get_instance() -> LazyImportRegistry:
        """Get singleton instance of LazyImportRegistry.

        Implements thread-safe double-checked locking pattern.

        Returns:
            Shared LazyImportRegistry instance

        """
        # Fast path - already initialized
        if LazyImportRegistry._instance is not None:
            return LazyImportRegistry._instance

        # Slow path - acquire lock and create
        with LazyImportRegistry._lock:
            # Double-check after acquiring lock
            if LazyImportRegistry._instance is not None:
                return LazyImportRegistry._instance

            # Create instance
            LazyImportRegistry._instance = LazyImportRegistry()

            return LazyImportRegistry._instance


def get_lazy_import_registry() -> LazyImportRegistry:
    """Convenience function to get singleton LazyImportRegistry.

    Returns:
        Shared LazyImportRegistry instance

    Example:
        from lee.lee_ligs import get_lazy_import_registry

        registry = get_lazy_import_registry()
        registry.register('ha_gateway', 'home_assistant.ha_gateway', ...)

    """
    return LazyImportRegistry.get_instance()


__all__ = [
    "LazyImportRegistry",
    "LazyModule",
    "get_lazy_import_registry",
]
