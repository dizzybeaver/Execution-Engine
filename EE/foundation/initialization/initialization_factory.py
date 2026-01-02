"""
Initialization Factory - Foundation Domain

System bootstrap and initialization implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- Manages system lifecycle
"""

import logging
import threading
from typing import Any, Dict, Optional, Callable
from enum import Enum, auto


class InitializationStatus(Enum):
    """System initialization status."""
    UNINITIALIZED = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    SHUTTING_DOWN = auto()
    SHUTDOWN = auto()


class InitializationFactory:
    """System initialization factory.

    Manages system lifecycle:
    - Initialize all components
    - Shutdown gracefully
    - Health checks
    - Status tracking

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
        """Initialize initialization factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        self._status = InitializationStatus.UNINITIALIZED
        self._lock = threading.RLock()
        self._components: Dict[str, Any] = {}

    def initialize(self, **kwargs) -> bool:
        """Initialize system.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._lock:
            if self._status != InitializationStatus.UNINITIALIZED:
                self.logger.warning(f"System already initialized: {self._status.name}")
                return True

            self.logger.info("Initializing system...")
            self._status = InitializationStatus.INITIALIZING

        try:
            # Initialize components
            self._initialize_components()

            with self._lock:
                self._status = InitializationStatus.INITIALIZED
                self.logger.info("System initialized successfully")

            return True

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            with self._lock:
                self._status = InitializationStatus.UNINITIALIZED
            return False

    def shutdown(self, **kwargs) -> bool:
        """Shutdown system.

        Args:
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        with self._lock:
            if self._status == InitializationStatus.SHUTDOWN:
                self.logger.warning("System already shutdown")
                return True

            self.logger.info("Shutting down system...")
            self._status = InitializationStatus.SHUTTING_DOWN

        try:
            # Shutdown components
            self._shutdown_components()

            with self._lock:
                self._status = InitializationStatus.SHUTDOWN
                self.logger.info("System shutdown successfully")

            return True

        except Exception as e:
            self.logger.error(f"System shutdown failed: {e}")
            return False

    def get_status(self, **kwargs) -> Dict[str, Any]:
        """Get system status.

        Args:
            **kwargs: Additional parameters

        Returns:
            Status information
        """
        with self._lock:
            return {
                "status": self._status.name,
                "components": list(self._components.keys()),
            }

    def get_health(self, **kwargs) -> Dict[str, Any]:
        """Get system health.

        Args:
            **kwargs: Additional parameters

        Returns:
            Health information
        """
        with self._lock:
            healthy = self._status in (
                InitializationStatus.INITIALIZED,
                InitializationStatus.SHUTDOWN
            )

            return {
                "healthy": healthy,
                "status": self._status.name,
                "component_count": len(self._components),
            }

    def _initialize_components(self) -> None:
        """Initialize system components."""
        # Initialize config
        self.logger.debug("Initializing config component")
        self._components["config"] = {"initialized": True}

        # Initialize logging
        self.logger.debug("Initializing logging component")
        self._components["logging"] = {"initialized": True}

        # Initialize other components as needed
        if self.call_operation:
            try:
                # Can call other domains via callback
                pass
            except Exception as e:
                self.logger.warning(f"Cross-domain initialization failed: {e}")

    def _shutdown_components(self) -> None:
        """Shutdown system components."""
        # Shutdown in reverse order
        for component_name in reversed(list(self._components.keys())):
            try:
                self.logger.debug(f"Shutting down {component_name}")
                del self._components[component_name]
            except Exception as e:
                self.logger.warning(f"Failed to shutdown {component_name}: {e}")


__all__ = [
    "InitializationFactory",
    "InitializationStatus",
]
