"""
Networking Domain Gateway - EE 2.1 Compliant

Routes operations to appropriate interfaces within the Networking domain:
- http: HTTP client operations (GET, POST, PUT, DELETE, custom requests)
- websocket: WebSocket operations (connect, send, receive, close)
- redis: Redis protocol operations (string, hash, list, pub/sub)
- mqtt: MQTT protocol operations (connect, publish, subscribe, unsubscribe, ping)
- ldap: LDAP protocol operations (bind, search, unbind)
- snmp: SNMP protocol operations (get, set, walk)
- ntp: NTP protocol operations (get_time, sync)
- memcached: Memcached protocol operations (get, set, add, replace, delete, increment, decrement, flush, stats)
- rpc: RPC protocol operations (xmlrpc_call, jsonrpc_call, xmlrpc_list_methods)

EE 2.1 Compliance:
- Extends DomainGateway base class with proper __init__
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
- Uniform constructor signature with get_config parameter
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable

# EE 2.1: NO sys.path manipulation
from EE.universal_gateway.domain_gateway import DomainGateway

# Import interface routers
from EE.networking.http_client.http_interface import execute_http_operation
from EE.networking.websocket_client.websocket_interface import execute_websocket_operation
from EE.networking.connectivity.connectivity_interface import execute_connectivity_operation
from EE.networking.protocols.redis.redis_interface import execute_redis_operation
from EE.networking.protocols.mqtt.mqtt_interface import execute_mqtt_operation
from EE.networking.protocols.ldap.ldap_interface import execute_ldap_operation
from EE.networking.protocols.snmp.snmp_interface import execute_snmp_operation
from EE.networking.protocols.ntp.ntp_interface import execute_ntp_operation
from EE.networking.protocols.memcached.memcached_interface import execute_memcached_operation
from EE.networking.protocols.rpc.rpc_interface import execute_rpc_operation


class NetworkingGateway(DomainGateway):
    """Networking Domain Gateway.

    Provides networking capabilities through the following interfaces:
    - connectivity: Network connectivity operations (scan, discover, test_connection, get_config, set_config)
    - http: HTTP client operations (get, post, put, delete, request)
    - websocket: WebSocket operations (connect, send, receive, close)
    - redis: Redis operations (get, set, delete, exists, keys, hget, hset, hgetall, lpush, rpush, lrange, publish)
    - mqtt: MQTT operations (connect, disconnect, publish, subscribe, unsubscribe, ping, get_subscriptions)
    - ldap: LDAP operations (connect, bind, unbind, search, disconnect)
    - snmp: SNMP operations (connect, get, set, walk, disconnect)
    - ntp: NTP operations (get_time, sync)
    - memcached: Memcached operations (get, set, add, replace, delete, increment, decrement, flush, stats)
    - rpc: RPC operations (xmlrpc_call, jsonrpc_call, xmlrpc_list_methods)

    All operations follow EE 2.1 patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside networking domain

    Example:
        gateway = NetworkingGateway(
            domain_name="networking",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=callback
        )

        # HTTP GET request
        response = gateway.execute_domain_operation(
            "http", "get",
            url="https://api.example.com/data"
        )

        # Redis set operation
        result = gateway.execute_domain_operation(
            "redis", "set",
            key="mykey", value="myvalue",
            host="localhost", port=6379
        )

        # MQTT publish
        gateway.execute_domain_operation(
            "mqtt", "publish",
            topic="sensors/temperature",
            payload="22.5",
            host="mqtt.example.com", port=1883
        )
    """

    # FIXED: EE 2.1 Uniform Gateway Constructor Signature - REQUIRED parameters only
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize networking domain gateway (EE 2.1).

        Args:
            domain_name: Domain name (must be "networking")
            get_logger: Factory function to create loggers (REQUIRED)
            get_metrics: Factory function to create metrics collectors (REQUIRED)
            get_config: Factory function to get config values (REQUIRED)
            call_operation: Function to call operations in other domains (REQUIRED)
        """
        # FIXED: Removed all default factories and fallback logic - EE 2.1 requires DI
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    def _default_logger(self, name: str) -> Any:
        """Create default logger."""
        import logging
        return logging.getLogger(name)

    def _default_metrics(self, name: str) -> Any:
        """Create default metrics collector."""
        return None

    def _default_call_operation(
        self, domain: str, interface: str, operation: str, **kwargs
    ) -> Any:
        """Default operation caller (raises error)."""
        raise RuntimeError(
            f"Cross-domain call not configured. "
            f"Attempted to call {domain}.{interface}.{operation}"
        )

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using EE 2.1 pattern.

        Args:
            interface: Interface name (http, websocket, redis, mqtt, ldap, snmp, ntp, memcached, rpc)
            operation: Operation name
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            InterfaceNotFoundError: If interface is invalid
            OperationNotFoundError: If operation is invalid
            DomainGatewayError: If execution fails
        """
        # EE 2.1: Inject factory functions instead of instances
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("get_config", self._get_config)
        kwargs.setdefault("call_operation", self._call_operation)

        # Route to appropriate interface
        try:
            if interface == "connectivity":
                return execute_connectivity_operation(operation, **kwargs)
            elif interface == "http":
                return execute_http_operation(operation, **kwargs)
            elif interface == "websocket":
                return execute_websocket_operation(operation, **kwargs)
            elif interface == "redis":
                return execute_redis_operation(operation, **kwargs)
            elif interface == "mqtt":
                return execute_mqtt_operation(operation, **kwargs)
            elif interface == "ldap":
                return execute_ldap_operation(operation, **kwargs)
            elif interface == "snmp":
                return execute_snmp_operation(operation, **kwargs)
            elif interface == "ntp":
                return execute_ntp_operation(operation, **kwargs)
            elif interface == "memcached":
                return execute_memcached_operation(operation, **kwargs)
            elif interface == "rpc":
                return execute_rpc_operation(operation, **kwargs)
            else:
                from EE.universal_gateway.domain_gateway import InterfaceNotFoundError
                raise InterfaceNotFoundError(
                    f"Unknown networking interface: {interface}. "
                    f"Valid interfaces: connectivity, http, websocket, redis, mqtt, ldap, snmp, ntp, memcached, rpc"
                )
        except ValueError as e:
            from EE.universal_gateway.domain_gateway import DomainGatewayError
            raise DomainGatewayError(
                f"Operation failed: {e}"
            ) from e

    def list_all(self) -> Dict[str, Any]:
        """List all networking domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": self._domain_name,
            "interfaces": {
                "connectivity": {
                    "description": "Network connectivity operations",
                    "operations": [
                        {"operation": "scan", "description": "Scan network targets"},
                        {"operation": "discover", "description": "Discover network resources"},
                        {"operation": "test_connection", "description": "Test network connection"},
                        {"operation": "get_config", "description": "Get connectivity config"},
                        {"operation": "set_config", "description": "Set connectivity config"},
                    ]
                },
                "http": {
                    "description": "HTTP client operations",
                    "operations": [
                        {"operation": "get", "description": "HTTP GET request"},
                        {"operation": "post", "description": "HTTP POST request"},
                        {"operation": "put", "description": "HTTP PUT request"},
                        {"operation": "delete", "description": "HTTP DELETE request"},
                        {"operation": "request", "description": "Custom HTTP request"},
                    ]
                },
                "websocket": {
                    "description": "WebSocket operations",
                    "operations": [
                        {"operation": "connect", "description": "Connect to WebSocket server"},
                        {"operation": "send", "description": "Send message via WebSocket"},
                        {"operation": "receive", "description": "Receive message from WebSocket"},
                        {"operation": "close", "description": "Close WebSocket connection"},
                    ]
                },
                "redis": {
                    "description": "Redis protocol operations",
                    "operations": [
                        {"operation": "get", "description": "Get value from Redis"},
                        {"operation": "set", "description": "Set value in Redis"},
                        {"operation": "delete", "description": "Delete key from Redis"},
                        {"operation": "exists", "description": "Check if key exists"},
                        {"operation": "keys", "description": "Find keys matching pattern"},
                        {"operation": "hget", "description": "Get hash field value"},
                        {"operation": "hset", "description": "Set hash field value"},
                        {"operation": "hgetall", "description": "Get all hash fields"},
                        {"operation": "lpush", "description": "Prepend to list"},
                        {"operation": "rpush", "description": "Append to list"},
                        {"operation": "lrange", "description": "Get range from list"},
                        {"operation": "publish", "description": "Publish to channel"},
                    ]
                },
                "mqtt": {
                    "description": "MQTT protocol operations",
                    "operations": [
                        {"operation": "connect", "description": "Connect to MQTT broker"},
                        {"operation": "disconnect", "description": "Disconnect from broker"},
                        {"operation": "publish", "description": "Publish message to topic"},
                        {"operation": "subscribe", "description": "Subscribe to topic"},
                        {"operation": "unsubscribe", "description": "Unsubscribe from topic"},
                        {"operation": "ping", "description": "Send ping request"},
                        {"operation": "get_subscriptions", "description": "Get active subscriptions"},
                    ]
                },
                "ldap": {
                    "description": "LDAP protocol operations",
                    "operations": [
                        {"operation": "connect", "description": "Connect to LDAP server"},
                        {"operation": "bind", "description": "Bind to LDAP with credentials"},
                        {"operation": "unbind", "description": "Unbind from LDAP server"},
                        {"operation": "search", "description": "Search LDAP directory"},
                        {"operation": "disconnect", "description": "Disconnect from LDAP server"},
                    ]
                },
                "snmp": {
                    "description": "SNMP protocol operations",
                    "operations": [
                        {"operation": "connect", "description": "Create SNMP socket"},
                        {"operation": "get", "description": "SNMP GET request"},
                        {"operation": "set", "description": "SNMP SET request"},
                        {"operation": "walk", "description": "SNMP WALK operation"},
                        {"operation": "disconnect", "description": "Close SNMP socket"},
                    ]
                },
                "ntp": {
                    "description": "NTP protocol operations",
                    "operations": [
                        {"operation": "get_time", "description": "Get time from NTP server"},
                        {"operation": "sync", "description": "Get time offset for sync"},
                    ]
                },
                "memcached": {
                    "description": "Memcached protocol operations",
                    "operations": [
                        {"operation": "get", "description": "Get value from Memcached"},
                        {"operation": "set", "description": "Set value in Memcached"},
                        {"operation": "add", "description": "Add key if not exists"},
                        {"operation": "replace", "description": "Replace key if exists"},
                        {"operation": "delete", "description": "Delete key"},
                        {"operation": "increment", "description": "Increment numeric value"},
                        {"operation": "decrement", "description": "Decrement numeric value"},
                        {"operation": "flush", "description": "Flush all keys"},
                        {"operation": "stats", "description": "Get server statistics"},
                    ]
                },
                "rpc": {
                    "description": "RPC protocol operations",
                    "operations": [
                        {"operation": "xmlrpc_call", "description": "Call XML-RPC method"},
                        {"operation": "jsonrpc_call", "description": "Call JSON-RPC method"},
                        {"operation": "xmlrpc_list_methods", "description": "List XML-RPC methods"},
                    ]
                },
            }
        }


__all__ = [
    "NetworkingGateway",
]
