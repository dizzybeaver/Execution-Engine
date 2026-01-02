"""
Plugins Factory - Infrastructure Domain

Contains implementation of plugin loading and management operations.

UG-ISP Architecture:
- Factory contains implementation
- Interface routes to factory methods
- Cross-domain via call_operation() only
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List, Protocol
from pathlib import Path
from enum import Enum
import importlib.util
import sys
from datetime import datetime


class PluginState(Enum):
    """Plugin lifecycle states."""
    LOADING = "loading"
    LOADED = "loaded"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNLOADING = "unloading"
    UNLOADED = "unloaded"
    ERROR = "error"


# Type protocols for dependency injection
class Logger(Protocol):
    def debug(self, msg: str, **kwargs): ...
    def info(self, msg: str, **kwargs): ...
    def warning(self, msg: str, **kwargs): ...
    def error(self, msg: str, **kwargs): ...


class Metrics(Protocol):
    def increment(self, metric: str, value: int = 1): ...
    def timing(self, metric: str, value: float): ...


class OperationCaller(Protocol):
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...


class PluginsFactory:
    """Plugins Factory - Implementation Layer.

    Contains actual plugin loading and management implementation.
    """

    def __init__(
        self,
        logger: Optional[Logger] = None,
        metrics: Optional[Metrics] = None,
        call_operation: Optional[OperationCaller] = None,
    ):
        """Initialize plugins factory with injected dependencies."""
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

        # Plugin registry
        self._plugins: Dict[str, Dict[str, Any]] = {}

    def load(
        self,
        name: str,
        path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Load a plugin by name or path.

        Args:
            name: Plugin name
            path: Optional path to plugin file/directory
            **kwargs: Additional arguments

        Returns:
            Dictionary with load result
        """
        if self._logger:
            self._logger.debug(f"Loading plugin", name=name, path=path)

        # Check if already loaded
        if name in self._plugins:
            return {
                "status": "already_loaded",
                "plugin": name,
                "state": self._plugins[name]["state"],
            }

        # Load plugin
        try:
            plugin_info = {
                "name": name,
                "path": path,
                "state": PluginState.LOADED.value,
                "loaded_at": datetime.now().isoformat(),
                "enabled": True,
            }

            # If path provided, try to import module
            if path:
                plugin_path = Path(path)
                if plugin_path.exists():
                    spec = importlib.util.spec_from_file_location(name, path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[name] = module
                        spec.loader.exec_module(module)
                        plugin_info["module"] = module
                        plugin_info["state"] = PluginState.RUNNING.value

            # Register plugin
            self._plugins[name] = plugin_info

            if self._metrics:
                self._metrics.increment("infrastructure.plugins.loaded")

            return {
                "status": "success",
                "plugin": name,
                "state": plugin_info["state"],
            }

        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to load plugin {name}: {e}")

            if self._metrics:
                self._metrics.increment("infrastructure.plugins.load_failed")

            return {
                "status": "error",
                "plugin": name,
                "error": str(e),
                "state": PluginState.ERROR.value,
            }

    def unload(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Unload a loaded plugin.

        Args:
            name: Plugin name
            **kwargs: Additional arguments

        Returns:
            Dictionary with unload result
        """
        if self._logger:
            self._logger.debug(f"Unloading plugin", name=name)

        if name not in self._plugins:
            return {
                "status": "not_found",
                "plugin": name,
                "error": f"Plugin not loaded: {name}",
            }

        try:
            # Remove from registry
            plugin_info = self._plugins.pop(name)

            # Remove from sys.modules if present
            if name in sys.modules:
                del sys.modules[name]

            if self._metrics:
                self._metrics.increment("infrastructure.plugins.unloaded")

            return {
                "status": "success",
                "plugin": name,
                "state": PluginState.UNLOADED.value,
            }

        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to unload plugin {name}: {e}")

            return {
                "status": "error",
                "plugin": name,
                "error": str(e),
            }

    def reload(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Reload a plugin (hot reload).

        Args:
            name: Plugin name
            **kwargs: Additional arguments

        Returns:
            Dictionary with reload result
        """
        if self._logger:
            self._logger.debug(f"Reloading plugin", name=name)

        if name not in self._plugins:
            return {
                "status": "not_found",
                "plugin": name,
                "error": f"Plugin not loaded: {name}",
            }

        # Get plugin info
        plugin_info = self._plugins[name]
        path = plugin_info.get("path")

        # Unload first
        unload_result = self.unload(name, **kwargs)

        if unload_result["status"] != "success":
            return unload_result

        # Reload
        return self.load(name, path=path, **kwargs)

    def list(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List all loaded plugins.

        Args:
            **kwargs: Additional arguments

        Returns:
            List of plugin information dictionaries
        """
        if self._logger:
            self._logger.debug(f"Listing plugins")

        plugins_list = []
        for name, info in self._plugins.items():
            plugins_list.append({
                "name": name,
                "state": info["state"],
                "enabled": info.get("enabled", True),
                "loaded_at": info.get("loaded_at"),
            })

        return plugins_list

    def get_info(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get plugin information.

        Args:
            name: Plugin name
            **kwargs: Additional arguments

        Returns:
            Dictionary with plugin information
        """
        if self._logger:
            self._logger.debug(f"Getting plugin info", name=name)

        if name not in self._plugins:
            return {
                "status": "not_found",
                "plugin": name,
                "error": f"Plugin not loaded: {name}",
            }

        plugin_info = self._plugins[name].copy()

        # Remove module reference from return (not serializable)
        plugin_info.pop("module", None)

        return plugin_info

    def enable(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Enable a plugin.

        Args:
            name: Plugin name
            **kwargs: Additional arguments

        Returns:
            Dictionary with enable result
        """
        if self._logger:
            self._logger.debug(f"Enabling plugin", name=name)

        if name not in self._plugins:
            return {
                "status": "not_found",
                "plugin": name,
                "error": f"Plugin not loaded: {name}",
            }

        self._plugins[name]["enabled"] = True

        if self._metrics:
            self._metrics.increment("infrastructure.plugins.enabled")

        return {
            "status": "success",
            "plugin": name,
            "enabled": True,
        }

    def disable(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Disable a plugin.

        Args:
            name: Plugin name
            **kwargs: Additional arguments

        Returns:
            Dictionary with disable result
        """
        if self._logger:
            self._logger.debug(f"Disabling plugin", name=name)

        if name not in self._plugins:
            return {
                "status": "not_found",
                "plugin": name,
                "error": f"Plugin not loaded: {name}",
            }

        self._plugins[name]["enabled"] = False

        if self._metrics:
            self._metrics.increment("infrastructure.plugins.disabled")

        return {
            "status": "success",
            "plugin": name,
            "enabled": False,
        }


__all__ = [
    'PluginsFactory',
]
