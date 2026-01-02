"""
Singleton Factory - Foundation Domain

Instance management and memory tracking implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- Thread-safe singleton management
"""

import logging
import threading
from typing import Any, Dict, Optional, Callable


class SingletonFactory:
    """Singleton instance management factory.

    Provides thread-safe singleton instance management with:
    - Strong references (explicit cleanup required)
    - Memory tracking
    - Lifecycle management

    UG-ISP Compliance:
    - Cross-domain calls via call_operation callback
    - Thread-safe operations
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize singleton factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Use regular dict for strong references
        self._instances: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def get(self, name: str, **kwargs) -> Optional[Any]:
        """Get singleton instance by name.

        Args:
            name: Instance name
            **kwargs: Additional parameters

        Returns:
            Singleton instance or None if not found
        """
        with self._lock:
            instance = self._instances.get(name)
            if instance is None:
                self.logger.debug(f"Singleton not found: {name}")
            return instance

    def set(self, name: str, instance: Any, **kwargs) -> bool:
        """Set singleton instance.

        Args:
            name: Instance name
            instance: Instance to store
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._lock:
            self._instances[name] = instance
            self.logger.info(f"Singleton registered: {name} ({type(instance).__name__})")
            return True

    def delete(self, name: str, **kwargs) -> bool:
        """Delete singleton instance.

        Args:
            name: Instance name
            **kwargs: Additional parameters

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if name in self._instances:
                del self._instances[name]
                self.logger.info(f"Singleton deleted: {name}")
                return True
            return False

    def exists(self, name: str, **kwargs) -> bool:
        """Check if singleton instance exists.

        Args:
            name: Instance name
            **kwargs: Additional parameters

        Returns:
            True if exists
        """
        with self._lock:
            return name in self._instances

    def list_all(self, **kwargs) -> Dict[str, str]:
        """List all singleton instances.

        Args:
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping instance names to type names
        """
        with self._lock:
            return {
                name: type(instance).__name__
                for name, instance in self._instances.items()
            }

    def clear(self, **kwargs) -> bool:
        """Clear all singleton instances.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._lock:
            count = len(self._instances)
            self._instances.clear()
            self.logger.info(f"Cleared {count} singleton instances")
            return True


__all__ = [
    "SingletonFactory",
]
