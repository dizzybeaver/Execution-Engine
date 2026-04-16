"""network/ws_pool.py

WebSocket connection pool with LRU eviction, size limits, and auto-cleanup.

Prevents memory leaks from unbounded connection growth.
Implements connection pooling with proper resource management.

Version: 1.0.0 (2026-03-31)
License: Apache 2.0
"""

import os
import threading
import time
from collections import OrderedDict
from typing import Any, Optional

# Gateway operations
from lee.gateway import GatewayInterface, execute_operation

# Use new network factory for WebSocket client
from lee.network.ws_core import WebSocketClient

# Debug support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"


class WebSocketConnectionPool:  # pylint: disable=too-many-instance-attributes
    """WebSocket connection pool with LRU eviction and automatic cleanup.

    Features:
      - Maximum connection limit (default: 50)
      - Idle timeout cleanup (default: 300 seconds)
      - LRU eviction when limit reached
      - Thread-safe operations
      - Connection metadata tracking

    Pool Configuration (via environment variables):
      - WS_POOL_MAX_SIZE: Maximum connections (default: 50)
      - WS_POOL_IDLE_TIMEOUT: Idle seconds before cleanup (default: 300)
      - WS_POOL_CLEANUP_INTERVAL: Cleanup check interval (default: 60)

    Example:
        pool = WebSocketConnectionPool()
        conn_id = pool.add_connection(ws_client, url="ws://...")
        connection = pool.get_connection(conn_id)
        pool.remove_connection(conn_id)
        pool.cleanup_idle()  # Remove idle connections
    """

    def __init__(
        self,
        max_size: Optional[int] = None,
        idle_timeout: Optional[int] = None,
        cleanup_interval: Optional[int] = None,
    ):
        """Initialize WebSocket connection pool.

        Args:
            max_size: Maximum number of connections (default: env WS_POOL_MAX_SIZE or 50)
            idle_timeout: Seconds before connection considered idle (default: env WS_POOL_IDLE_TIMEOUT or 300)
            cleanup_interval: Seconds between cleanup checks (default: env WS_POOL_CLEANUP_INTERVAL or 60)

        """
        self._max_size = max_size or int(os.environ.get("WS_POOL_MAX_SIZE", "50"))
        self._idle_timeout = idle_timeout or int(os.environ.get("WS_POOL_IDLE_TIMEOUT", "300"))
        self._cleanup_interval = cleanup_interval or int(os.environ.get("WS_POOL_CLEANUP_INTERVAL", "60"))

        # OrderedDict for LRU tracking (maintains insertion order)
        self._connections: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()

        # Metadata
        self._total_created = 0
        self._total_evicted = 0
        self._total_idle_removed = 0
        self._last_cleanup = time.time()

        if _DEBUG_ENABLED:
            try:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message='WebSocketConnectionPool.__init__',
                    scope='WS_POOL',
                    max_size=self._max_size,
                    idle_timeout=self._idle_timeout,
                    cleanup_interval=self._cleanup_interval
                )
            except (ImportError, AttributeError):
                pass

        # Validate configuration
        if self._max_size < 1:
            raise ValueError("WS_POOL_MAX_SIZE must be at least 1")
        if self._idle_timeout < 1:
            raise ValueError("WS_POOL_IDLE_TIMEOUT must be at least 1 second")
        if self._cleanup_interval < 1:
            raise ValueError("WS_POOL_CLEANUP_INTERVAL must be at least 1 second")

    def add_connection(self, connection: WebSocketClient, url: str, conn_id: Optional[str] = None) -> str:
        """Add connection to pool with LRU eviction.

        Args:
            connection: WebSocketClient instance
            url: WebSocket URL for metadata
            conn_id: Optional connection ID (auto-generated if None)

        Returns:
            Connection ID for pool operations

        Raises:
            ValueError: If connection is None or invalid
            RuntimeError: If pool is full (should not happen with eviction)

        """
        if connection is None:
            raise ValueError("Connection cannot be None")

        with self._lock:
            # Auto-generate connection ID if not provided
            if conn_id is None:
                conn_id = f"conn_{int(time.time() * 1000)}_{os.urandom(2).hex()}"

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Adding connection to pool',
                                     scope='WS_POOL', conn_id=conn_id,
                                     url=url, pool_size=len(self._connections),
                                     max_size=self._max_size)
                except (ImportError, AttributeError):
                    pass

            # Evict oldest connection if at limit
            if len(self._connections) >= self._max_size:
                if _DEBUG_ENABLED:
                    try:
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message='Pool at capacity, evicting LRU',
                                         scope='WS_POOL', pool_size=len(self._connections))
                    except (ImportError, AttributeError):
                        pass
                self._evict_lru()

            # Add to pool (insertion order = LRU order)
            now = time.time()
            self._connections[conn_id] = {
                "connection": connection,
                "url": url,
                "created_at": now,
                "last_used": now,
                "use_count": 0,
            }

            self._total_created += 1

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Connection added to pool',
                                     scope='WS_POOL', conn_id=conn_id,
                                     pool_size=len(self._connections))
                except (ImportError, AttributeError):
                    pass

            return conn_id

    def get_connection(self, conn_id: str) -> Optional[WebSocketClient]:
        """Get connection by ID and update LRU timestamp.

        Args:
            conn_id: Connection ID from add_connection()

        Returns:
            WebSocketClient instance or None if not found

        """
        with self._lock:
            if conn_id not in self._connections:
                if _DEBUG_ENABLED:
                    try:
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message='Connection not found in pool',
                                         scope='WS_POOL', conn_id=conn_id)
                    except (ImportError, AttributeError):
                        pass
                return None

            # Move to end (most recently used)
            conn_data = self._connections.pop(conn_id)
            conn_data["last_used"] = time.time()
            conn_data["use_count"] += 1
            self._connections[conn_id] = conn_data

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Connection retrieved from pool',
                                     scope='WS_POOL', conn_id=conn_id,
                                     use_count=conn_data["use_count"])
                except (ImportError, AttributeError):
                    pass

            return conn_data["connection"]

    def remove_connection(self, conn_id: str) -> bool:
        """Remove connection from pool.

        Args:
            conn_id: Connection ID to remove

        Returns:
            True if connection was removed, False if not found

        """
        with self._lock:
            if conn_id not in self._connections:
                if _DEBUG_ENABLED:
                    try:
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message='Connection not found for removal',
                                         scope='WS_POOL', conn_id=conn_id)
                    except (ImportError, AttributeError):
                        pass
                return False

            conn_data = self._connections.pop(conn_id)
            connection = conn_data["connection"]

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Removing connection from pool',
                                     scope='WS_POOL', conn_id=conn_id)
                except (ImportError, AttributeError):
                    pass

            # Close connection if still active
            try:
                if connection.connected:
                    connection.close()
            except (ConnectionError, OSError):
                # Connection close failed - continue
                pass

            return True

    def cleanup_idle(self) -> int:
        """Remove idle connections based on timeout.

        Automatically called periodically by get_connection() and add_connection().
        Can also be called manually for immediate cleanup.

        Returns:
            Number of connections removed

        """
        now = time.time()
        removed = 0

        with self._lock:
            # Check if cleanup is needed
            time_since_last_cleanup = now - self._last_cleanup
            if _DEBUG_ENABLED:
                try:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message='cleanup_idle - checking if cleanup needed',
                        scope='WS_POOL',
                        time_since_last_cleanup=f"{time_since_last_cleanup:.1f}s",
                        cleanup_interval=self._cleanup_interval
                    )
                except (ImportError, AttributeError):
                    pass

            if time_since_last_cleanup < self._cleanup_interval:
                return 0

            # Find idle connections
            idle_ids = []
            for conn_id, conn_data in self._connections.items():
                idle_time = now - conn_data["last_used"]
                if idle_time > self._idle_timeout:
                    idle_ids.append(conn_id)

            if _DEBUG_ENABLED and idle_ids:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Cleaning up idle connections',
                                     scope='WS_POOL', idle_count=len(idle_ids),
                                     pool_size=len(self._connections))
                except (ImportError, AttributeError):
                    pass

            # Remove idle connections
            for conn_id in idle_ids:
                if self.remove_connection(conn_id):
                    removed += 1
                    self._total_idle_removed += 1

            self._last_cleanup = now

            if _DEBUG_ENABLED and removed > 0:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Idle connections cleaned up',
                                     scope='WS_POOL', removed=removed,
                                     total_idle_removed=self._total_idle_removed)
                except (ImportError, AttributeError):
                    pass

        return removed

    def _evict_lru(self) -> None:
        """Evict least-recently-used connection.

        Called automatically when pool reaches max_size.

        """
        if not self._connections:
            return

        # Get oldest connection (first in OrderedDict)
        conn_id, conn_data = next(iter(self._connections.items()))
        self.remove_connection(conn_id)
        self._total_evicted += 1

        # Log eviction via gateway
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                "log_warning",
                message=f"WebSocket pool evicted LRU connection: {conn_id}",
                url=conn_data.get("url", "unknown")[:100],
                pool_size=len(self._connections),
            )
        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            pass

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool metrics

        """
        with self._lock:
            now = time.time()
            active_count = 0
            idle_count = 0

            for conn_data in self._connections.values():
                try:
                    if conn_data["connection"].connected:
                        idle_time = now - conn_data["last_used"]
                        if idle_time > self._idle_timeout:
                            idle_count += 1
                        else:
                            active_count += 1
                except (KeyError, AttributeError, TypeError):
                    # Connection check failed, count as idle
                    idle_count += 1

            return {
                "pool_size": len(self._connections),
                "max_size": self._max_size,
                "active_connections": active_count,
                "idle_connections": idle_count,
                "total_created": self._total_created,
                "total_evicted": self._total_evicted,
                "total_idle_removed": self._total_idle_removed,
                "idle_timeout": self._idle_timeout,
                "cleanup_interval": self._cleanup_interval,
                "last_cleanup": self._last_cleanup,
                "connection_ids": list(self._connections.keys()),
            }

    def reset(self) -> None:
        """Reset pool, closing all connections.

        Called by websocket_reset_implementation().

        """
        with self._lock:
            pool_size = len(self._connections)

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Resetting connection pool',
                                     scope='WS_POOL', pool_size=pool_size)
                except (ImportError, AttributeError):
                    pass

            # Close all connections
            for conn_data in list(self._connections.values()):
                connection = conn_data["connection"]
                try:
                    if connection.connected:
                        connection.close()
                except (ConnectionError, OSError):
                    # Connection close failed - continue
                    pass

            # Clear pool
            self._connections.clear()

            if _DEBUG_ENABLED:
                try:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Connection pool reset completed',
                                     scope='WS_POOL', previous_size=pool_size)
                except (ImportError, AttributeError):
                    pass

    @property
    def max_size(self) -> int:
        """Maximum pool size."""
        return self._max_size

    @property
    def idle_timeout(self) -> int:
        """Idle timeout in seconds."""
        return self._idle_timeout

    @property
    def size(self) -> int:
        """Current pool size."""
        return len(self._connections)


# Global connection pool instance
_global_pool: Optional[WebSocketConnectionPool] = None
_pool_lock = threading.Lock()


def get_global_pool() -> WebSocketConnectionPool:
    """Get or create global WebSocket connection pool.

    Returns:
        Singleton WebSocketConnectionPool instance

    """
    global _global_pool  # pylint: disable=global-statement

    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:
                # Double-checked locking pattern
                _global_pool = WebSocketConnectionPool()

    return _global_pool


__all__ = [
    "WebSocketConnectionPool",
    "get_global_pool",
]
