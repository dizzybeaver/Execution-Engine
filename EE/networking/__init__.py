"""
Networking Domain - UG-ISP Compliant

Provides networking capabilities through the following interfaces:
- http: HTTP client operations (get, post, put, delete, request)
- websocket: WebSocket operations (connect, send, receive, close)
- redis: Redis protocol operations (get, set, delete, publish, etc.)
- mqtt: MQTT protocol operations (connect, publish, subscribe, etc.)
- ldap: LDAP protocol operations (bind, search, unbind, etc.)
- snmp: SNMP protocol operations (get, set, walk, disconnect)
- ntp: NTP protocol operations (get_time, sync)
- memcached: Memcached protocol operations (get, set, increment, etc.)
- rpc: RPC protocol operations (xmlrpc_call, jsonrpc_call)

UG-ISP Compliance:
- Extends DomainGateway base class
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
- NO imports outside networking domain
"""

from EE.networking.networking_gateway import NetworkingGateway

__all__ = [
    "NetworkingGateway",
]
