"""
Memcached Factory - Networking Domain

Memcached protocol implementation (Binary Protocol).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Implements Memcached binary protocol
"""

import socket
import struct
import logging
from typing import Any, Dict, Optional, Callable, Union


class MemcachedFactory:
    """Memcached factory.

    Provides Memcached protocol operations:
    - Basic operations: get, set, add, replace, delete
    - Arithmetic: increment, decrement
    - Management: flush, stats

    UG-ISP Compliance:
    - Uses only standard library
    - Implements Memcached binary protocol
    - Cross-domain calls via call_operation callback
    """

    # Binary protocol opcodes
    GET = 0x00
    SET = 0x01
    ADD = 0x02
    REPLACE = 0x03
    DELETE = 0x04
    INCREMENT = 0x05
    DECREMENT = 0x06
    QUIT = 0x07
    FLUSH = 0x08
    STAT = 0x10

    # Status codes
    SUCCESS = 0x00
    KEY_ENOENT = 0x01
    KEY_EEXISTS = 0x02

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize Memcached factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.protocols.memcached")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

        self._connections: Dict[str, socket.socket] = {}

    def _get_connection(self, host: str, port: int, timeout: int = 10) -> socket.socket:
        """Get or create Memcached connection.

        Args:
            host: Memcached server host
            port: Memcached server port
            timeout: Connection timeout

        Returns:
            Connected socket
        """
        key = f"{host}:{port}"

        if key in self._connections:
            return self._connections[key]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        self._connections[key] = sock
        return sock

    def _send_request(self, sock: socket.socket, opcode: int, key: bytes = b'',
                      value: bytes = b'', extras: bytes = b'', cas: int = 0) -> None:
        """Send Memcached binary protocol request.

        Args:
            sock: Socket to send to
            opcode: Operation code
            key: Request key
            value: Request value
            extras: Extra data
            cas: Compare-and-swap value
        """
        # Build header (24 bytes)
        header = struct.pack(
            '>BBHBBHLLQ',
            0x80,  # Magic (request)
            opcode,
            len(key),
            len(extras),
            0,  # Data type
            len(value),
            0,  # Opaque
            cas
        )

        # Build packet
        packet = header + extras + key + value
        sock.send(packet)

    def _receive_response(self, sock: socket.socket) -> Dict[str, Any]:
        """Receive Memcached binary protocol response.

        Args:
            sock: Socket to receive from

        Returns:
            Response dictionary
        """
        # Read header (24 bytes)
        header = sock.recv(24)
        if not header or len(header) != 24:
            raise ConnectionError('Connection closed or invalid response')

        magic, opcode, key_len, extras_len, data_type, status, body_len, opaque, cas = \
            struct.unpack('>BBHBBHLLQ', header)

        if magic != 0x81:
            raise ConnectionError('Invalid Memcached response magic')

        # Read body if present
        body = b''
        if body_len > 0:
            body = sock.recv(body_len)

        return {
            'opcode': opcode,
            'key_length': key_len,
            'extras_length': extras_len,
            'data_type': data_type,
            'status': status,
            'body_length': body_len,
            'opaque': opaque,
            'cas': cas,
            'body': body
        }

    def get(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 11211,
        timeout: int = 10,
        **kwargs
    ) -> Optional[bytes]:
        """Get value for key.

        Args:
            key: Memcached key
            host: Memcached server host
            port: Memcached server port
            timeout: Connection timeout

        Returns:
            Value or None if not found

        Example:
            factory = MemcachedFactory()
            value = factory.get(key="mykey", host="localhost", port=11211)
        """
        self.logger.debug(f"Memcached GET: {key}")

        conn = self._get_connection(host, port, timeout)
        self._send_request(conn, self.GET, key=key.encode('utf-8'))
        response = self._receive_response(conn)

        if response['status'] == self.KEY_ENOENT:
            return None
        elif response['status'] != self.SUCCESS:
            raise ConnectionError(f'Memcached get failed: status {response["status"]}')

        # Skip extras (flags) and return value
        if response['extras_length'] > 0:
            return response['body'][response['extras_length']:]
        return response['body']

    def set(
        self,
        key: str,
        value: Union[str, bytes],
        host: str = 'localhost',
        port: int = 11211,
        expire: int = 0,
        flags: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> bool:
        """Set key to value.

        Args:
            key: Memcached key
            value: Value to set
            host: Memcached server host
            port: Memcached server port
            expire: Expiration time in seconds
            flags: User-defined flags
            timeout: Connection timeout

        Returns:
            True if successful

        Example:
            factory = MemcachedFactory()
            factory.set(key="mykey", value="myvalue", expire=60)
        """
        self.logger.debug(f"Memcached SET: {key}")

        conn = self._get_connection(host, port, timeout)

        if isinstance(value, str):
            value = value.encode('utf-8')

        extras = struct.pack('>II', flags, expire)
        self._send_request(conn, self.SET, key=key.encode('utf-8'),
                          value=value, extras=extras)
        response = self._receive_response(conn)

        return response['status'] == self.SUCCESS

    def add(
        self,
        key: str,
        value: Union[str, bytes],
        host: str = 'localhost',
        port: int = 11211,
        expire: int = 0,
        flags: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> bool:
        """Add key only if it doesn't exist.

        Args:
            key: Memcached key
            value: Value to add
            host: Memcached server host
            port: Memcached server port
            expire: Expiration time in seconds
            flags: User-defined flags
            timeout: Connection timeout

        Returns:
            True if added, False if key exists

        Example:
            factory = MemcachedFactory()
            success = factory.add(key="newkey", value="value")
        """
        self.logger.debug(f"Memcached ADD: {key}")

        conn = self._get_connection(host, port, timeout)

        if isinstance(value, str):
            value = value.encode('utf-8')

        extras = struct.pack('>II', flags, expire)
        self._send_request(conn, self.ADD, key=key.encode('utf-8'),
                          value=value, extras=extras)
        response = self._receive_response(conn)

        return response['status'] == self.SUCCESS

    def replace(
        self,
        key: str,
        value: Union[str, bytes],
        host: str = 'localhost',
        port: int = 11211,
        expire: int = 0,
        flags: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> bool:
        """Replace key only if it exists.

        Args:
            key: Memcached key
            value: New value
            host: Memcached server host
            port: Memcached server port
            expire: Expiration time in seconds
            flags: User-defined flags
            timeout: Connection timeout

        Returns:
            True if replaced, False if key doesn't exist

        Example:
            factory = MemcachedFactory()
            success = factory.replace(key="mykey", value="newvalue")
        """
        self.logger.debug(f"Memcached REPLACE: {key}")

        conn = self._get_connection(host, port, timeout)

        if isinstance(value, str):
            value = value.encode('utf-8')

        extras = struct.pack('>II', flags, expire)
        self._send_request(conn, self.REPLACE, key=key.encode('utf-8'),
                          value=value, extras=extras)
        response = self._receive_response(conn)

        return response['status'] == self.SUCCESS

    def delete(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 11211,
        timeout: int = 10,
        **kwargs
    ) -> bool:
        """Delete key.

        Args:
            key: Memcached key
            host: Memcached server host
            port: Memcached server port
            timeout: Connection timeout

        Returns:
            True if deleted

        Example:
            factory = MemcachedFactory()
            factory.delete(key="mykey")
        """
        self.logger.debug(f"Memcached DELETE: {key}")

        conn = self._get_connection(host, port, timeout)
        self._send_request(conn, self.DELETE, key=key.encode('utf-8'))
        response = self._receive_response(conn)

        return response['status'] == self.SUCCESS

    def increment(
        self,
        key: str,
        delta: int = 1,
        host: str = 'localhost',
        port: int = 11211,
        initial: int = 0,
        expire: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> int:
        """Increment numeric value.

        Args:
            key: Memcached key
            delta: Amount to increment
            host: Memcached server host
            port: Memcached server port
            initial: Initial value if key doesn't exist
            expire: Expiration time in seconds
            timeout: Connection timeout

        Returns:
            New value

        Example:
            factory = MemcachedFactory()
            new_value = factory.increment(key="counter", delta=5)
        """
        self.logger.debug(f"Memcached INCREMENT: {key}")

        conn = self._get_connection(host, port, timeout)
        extras = struct.pack('>QII', delta, initial, expire)
        self._send_request(conn, self.INCREMENT, key=key.encode('utf-8'), extras=extras)
        response = self._receive_response(conn)

        if response['status'] != self.SUCCESS:
            raise ConnectionError(f'Memcached increment failed: status {response["status"]}')

        return int.from_bytes(response['body'], 'big')

    def decrement(
        self,
        key: str,
        delta: int = 1,
        host: str = 'localhost',
        port: int = 11211,
        initial: int = 0,
        expire: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> int:
        """Decrement numeric value.

        Args:
            key: Memcached key
            delta: Amount to decrement
            host: Memcached server host
            port: Memcached server port
            initial: Initial value if key doesn't exist
            expire: Expiration time in seconds
            timeout: Connection timeout

        Returns:
            New value

        Example:
            factory = MemcachedFactory()
            new_value = factory.decrement(key="counter", delta=1)
        """
        self.logger.debug(f"Memcached DECREMENT: {key}")

        conn = self._get_connection(host, port, timeout)
        extras = struct.pack('>QII', delta, initial, expire)
        self._send_request(conn, self.DECREMENT, key=key.encode('utf-8'), extras=extras)
        response = self._receive_response(conn)

        if response['status'] != self.SUCCESS:
            raise ConnectionError(f'Memcached decrement failed: status {response["status"]}')

        return int.from_bytes(response['body'], 'big')

    def flush(
        self,
        host: str = 'localhost',
        port: int = 11211,
        delay: int = 0,
        timeout: int = 10,
        **kwargs
    ) -> bool:
        """Flush all keys.

        Args:
            host: Memcached server host
            port: Memcached server port
            delay: Delay before flushing (seconds)
            timeout: Connection timeout

        Returns:
            True if successful

        Example:
            factory = MemcachedFactory()
            factory.flush(delay=0)
        """
        self.logger.debug("Memcached FLUSH")

        conn = self._get_connection(host, port, timeout)
        extras = struct.pack('>I', delay)
        self._send_request(conn, self.FLUSH, extras=extras)
        response = self._receive_response(conn)

        return response['status'] == self.SUCCESS

    def stats(
        self,
        host: str = 'localhost',
        port: int = 11211,
        timeout: int = 10,
        **kwargs
    ) -> Dict[str, str]:
        """Get server statistics.

        Args:
            host: Memcached server host
            port: Memcached server port
            timeout: Connection timeout

        Returns:
            Dictionary of statistic name-value pairs

        Example:
            factory = MemcachedFactory()
            stats = factory.stats()
            print(f"Total items: {stats.get('total_items')}")
        """
        self.logger.debug("Memcached STATS")

        conn = self._get_connection(host, port, timeout)
        self._send_request(conn, self.STAT)
        stats = {}

        while True:
            response = self._receive_response(conn)

            if response['status'] != self.SUCCESS:
                break

            if response['body_length'] == 0:
                break

            # Parse stat: key\0value\0
            parts = response['body'].split(b'\x00')
            if len(parts) >= 2:
                key = parts[0].decode('utf-8')
                value = parts[1].decode('utf-8')
                stats[key] = value

        return stats


__all__ = [
    "MemcachedFactory",
]
