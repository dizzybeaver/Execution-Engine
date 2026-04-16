"""network/http_connection_pool.py

HTTP connection pooling with LRU eviction and lifetime management.
"""

import http.client
import time

from lee.gateway import execute_operation, GatewayInterface
from lee.lee_config.constants import HTTP_CONNECTION_POOL_LIFETIME
from lee.network.http_constants import _DEBUG_MODE


# Exceptions
class ConnectionError(Exception):
    """HTTP connection error."""


# Connection Pool
class _ConnectionPool:
    """HTTP connection pool with LRU eviction and lifetime management."""

    def __init__(self, ssl_context):
        from lee.lee_config.variables import HTTP_CLIENT_MAX_CONNECTIONS

        self._conns = {}
        self._ssl_context = ssl_context
        self._max_conns = HTTP_CLIENT_MAX_CONNECTIONS
        self._conn_last_used = {}
        self._conn_created = {}
        self._max_conn_lifetime = HTTP_CONNECTION_POOL_LIFETIME
        self._pool_hits = 0
        self._pool_misses = 0

    def _is_connection_stale(self, key):
        """Check if connection has exceeded its lifetime."""
        debug_enabled = _DEBUG_MODE
        if key not in self._conn_created:
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message=(
                        "ConnectionPool._is_connection_stale - "
                        "key not in conn_created, returning True"
                    ),
                    scope='CONNECTION_POOL'
                )
            return True
        age = time.time() - self._conn_created[key]
        is_stale = age > self._max_conn_lifetime
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"ConnectionPool._is_connection_stale - key={key}, "
                    f"age={age:.2f}s, max_lifetime={self._max_conn_lifetime}s, "
                    f"is_stale={is_stale}"
                ),
                scope='CONNECTION_POOL'
            )
        return is_stale

    def _remove_connection(self, key):
        """Safely remove and close a connection from the pool."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"ConnectionPool._remove_connection ENTRY - key={key}",
                scope='CONNECTION_POOL'
            )
        if key in self._conns:
            try:
                self._conns[key].close()
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=(
                            f"ConnectionPool._remove_connection - "
                            f"closed connection for key={key}"
                        ),
                        scope='CONNECTION_POOL'
                    )
            except (OSError, ConnectionError) as e:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_error',
                        message=f'(IOError, OSError, ConnectionError) occurred: {e}',
                        corr_id=None
                    )
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Gateway not available
            del self._conns[key]
        if key in self._conn_last_used:
            del self._conn_last_used[key]
        if key in self._conn_created:
            del self._conn_created[key]
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"ConnectionPool._remove_connection EXIT - key={key} removed",
                scope='CONNECTION_POOL'
            )

    def get(self, scheme, host, port, proxy, timeout=None):
        """Get or create a connection from the pool."""
        key = (scheme, host, port, bool(proxy))

        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"ConnectionPool.get ENTRY - scheme={scheme}, host={host}, port={port}, timeout={timeout}",
                             scope='CONNECTION_POOL')

        # Check for existing connection
        if key in self._conns:
            # Check if connection is stale
            if self._is_connection_stale(key):
                if debug_enabled:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message=f"Connection stale - removing from pool: {key}",
                                     scope='CONNECTION_POOL')
                self._remove_connection(key)
            else:
                # Connection is valid - reuse it
                self._conn_last_used[key] = time.time()
                self._pool_hits += 1
                # Update timeout on reused connection
                conn = self._conns[key]
                if timeout is not None:
                    old_timeout = conn.timeout
                    conn.timeout = timeout
                    if debug_enabled:
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message=f"Updated timeout on reused connection: old={old_timeout}s, new={timeout}s",
                                         scope='CONNECTION_POOL')
                if debug_enabled:
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message="Reusing existing connection - pool_hit",
                                     scope='CONNECTION_POOL')
                    execute_operation(GatewayInterface.DEBUG, 'timing',
                                     operation_name='pool_get_reuse',
                                     scope='CONNECTION_POOL')
                return conn

        # Need to create new connection
        self._pool_misses += 1

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message="Creating new connection - pool_miss",
                             scope='CONNECTION_POOL')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='before_conn_create',
                             scope='CONNECTION_POOL')

        # Evict oldest connection if at limit
        if len(self._conns) >= self._max_conns:
            oldest_key = min(self._conn_last_used, key=self._conn_last_used.get)
            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Evicting oldest connection: {oldest_key}",
                                 scope='CONNECTION_POOL')
            self._remove_connection(oldest_key)

        if proxy:
            phost = proxy.hostname
            pport = proxy.port or (443 if proxy.scheme == "https" else 80)
            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Creating {proxy.scheme.upper()} connection to proxy {phost}:{pport}",
                                 scope='CONNECTION_POOL')
            if proxy.scheme == "https":
                conn = http.client.HTTPSConnection(phost, pport, context=self._ssl_context, timeout=timeout)
            else:
                conn = http.client.HTTPConnection(phost, pport, timeout=timeout)
        else:
            # Dictionary dispatch for O(1) connection type lookup
            CONNECTION_TYPES = {
                "https": lambda h, p: http.client.HTTPSConnection(h, p, context=self._ssl_context, timeout=timeout),
                "http": lambda h, p: http.client.HTTPConnection(h, p, timeout=timeout),
            }
            connection_factory = CONNECTION_TYPES.get(scheme, http.client.HTTPConnection)

            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Creating {scheme.upper()} connection to {host}:{port}",
                                 scope='CONNECTION_POOL')

            conn = connection_factory(host, port)

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"Connection created - conn={type(conn).__name__}, conn.timeout={conn.timeout}",
                             scope='CONNECTION_POOL')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='after_conn_create',
                             scope='CONNECTION_POOL')

        self._conns[key] = conn
        self._conn_last_used[key] = time.time()
        self._conn_created[key] = time.time()

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='pool_get_complete',
                             scope='CONNECTION_POOL')

        return conn

    def mark_broken(self, scheme, host, port, proxy):  # pylint: disable=too-many-arguments
        """Remove a broken connection from the pool."""
        debug_enabled = _DEBUG_MODE
        key = (scheme, host, port, bool(proxy))
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"ConnectionPool.mark_broken ENTRY - "
                    f"marking connection as broken: key={key}"
                ),
                scope='CONNECTION_POOL'
            )
        self._remove_connection(key)
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="ConnectionPool.mark_broken EXIT - broken connection removed",
                scope='CONNECTION_POOL'
            )

    def get_pool_stats(self):
        """Get connection pool statistics."""
        debug_enabled = _DEBUG_MODE
        active_conns = len(self._conns)
        total_requests = self._pool_hits + self._pool_misses
        hit_rate = (
            self._pool_hits / total_requests if total_requests > 0 else 0.0
        )
        stats = {
            "active_connections": active_conns,
            "max_connections": self._max_conns,
            "pool_hits": self._pool_hits,
            "pool_misses": self._pool_misses,
            "hit_rate": hit_rate,
        }
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"ConnectionPool.get_pool_stats - {stats}",
                scope='CONNECTION_POOL'
            )
        return stats

    def close_all(self):
        """Close all connections in the pool."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"ConnectionPool.close_all ENTRY - "
                    f"closing {len(self._conns)} connections"
                ),
                scope='CONNECTION_POOL'
            )
        for c in self._conns.values():
            try:
                c.close()
            except (OSError, ConnectionError) as e:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_error',
                        message=f'(IOError, OSError, ConnectionError) occurred: {e}',
                        corr_id=None
                    )
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Gateway not available
        self._conns.clear()
        self._conn_last_used.clear()
        self._conn_created.clear()
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="ConnectionPool.close_all EXIT - all connections closed",
                scope='CONNECTION_POOL'
            )


__all__ = [
    "_ConnectionPool",
    "ConnectionError",
]
