"""cache_l2_disk_split/background_cleanup.py

Background cleanup thread management for L2 disk cache.
"""

from __future__ import annotations

import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lee.lee_cache.cache_l2_disk_split.l2_disk_cache import L2DiskCache

try:
    from lee.gateway import GatewayInterface, execute_operation
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    execute_operation = None
    GatewayInterface = None


class BackgroundCleanup:
    """Background cleanup thread manager."""

    def __init__(self, cache_instance: "L2DiskCache", cleanup_interval: int):
        """Initialize background cleanup manager.

        Args:
            cache_instance: L2DiskCache instance to clean
            cleanup_interval: Seconds between cleanup cycles

        """
        self.cache_instance = cache_instance
        self.cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()
        self._running = True
        self._cleanup_thread = None

    def start(self) -> None:
        """Start background cleanup thread."""
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup,
            daemon=True,
        )
        self._cleanup_thread.start()

    def stop(self) -> None:
        """Stop the background cleanup thread gracefully."""
        self._running = False
        self._stop_event.set()  # Signal thread to stop immediately
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)  # Wait longer for graceful shutdown

    def _background_cleanup(self) -> None:
        """Background cleanup thread.

        NOTE: time.sleep() is used here as an acceptable exception to gateway pattern
        because this is a background thread that runs independently of Lambda request
        processing. Using gateway for sleep in a background thread would add unnecessary
        overhead and complexity.
        """
        while not self._stop_event.is_set():
            try:
                # Use event.wait() instead of sleep() for responsive shutdown
                if self._stop_event.wait(timeout=self.cleanup_interval):
                    break  # Stop event was set
                self.cache_instance.cleanup()
            except (OSError, RuntimeError) as e:
                # Background cleanup failed - log and continue
                pass
                if execute_operation is not None:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING, "log_warning",
                            message=f"L2 cache background cleanup failed: {e}",
                            extra_context={"operation": "background_cleanup"},
                        )
                    except (AttributeError, RuntimeError):
                        # Logging unavailable - silent fail
                        pass
                # Continue loop - don't re-raise (thread should be resilient)
