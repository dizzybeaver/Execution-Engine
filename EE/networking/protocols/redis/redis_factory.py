"""
Redis Factory - Networking Domain

Redis protocol implementation (RESP - Redis Serialization Protocol).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Implements RESP protocol
"""

import socket
import logging
from typing import Any, Dict, Optional, Callable, Union, List


class RedisFactory:
    """Redis factory.

    Provides Redis protocol operations:
    - String operations: get, set, delete, exists, keys
    - Hash operations: hget, hset, hgetall
    - List operations: lpush, rpush, lrange
    - Pub/Sub: publish

    UG-ISP Compliance:
    - Uses only standard library
    - Implements RESP (Redis Serialization Protocol)
    - Cross-domain calls via call_operation callback
    """

    # Protocol markers
    SIMPLE_STRING = b'+'
    ERROR = b'-'
    INTEGER = b':'
    BULK_STRING = b'$'
    ARRAY = b'*'

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize Redis factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.protocols.redis")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

        # Connection cache for reuse
        self._connections: Dict[str, socket.socket] = {}

    def _get_connection(self, host: str, port: int, db: int = 0,
                        password: Optional[str] = None, timeout: int = 10) -> socket.socket:
        """Get or create Redis connection.

        Args:
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password
            timeout: Connection timeout

        Returns:
            Connected socket
        """
        key = f"{host}:{port}:{db}"

        # Check if connection exists and is valid
        if key in self._connections:
            return self._connections[key]

        # Create new connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # Authenticate if password provided
        if password:
            self._send_command(sock, ['AUTH', password])
            response = self._receive_response(sock)
            if response != b'+OK':
                raise ConnectionError('Redis authentication failed')

        # Select database
        if db != 0:
            self._send_command(sock, ['SELECT', str(db)])
            response = self._receive_response(sock)
            if response != b'+OK':
                raise ConnectionError('Redis database selection failed')

        self._connections[key] = sock
        return sock

    def _send_command(self, sock: socket.socket, command: List[Union[str, bytes]]) -> None:
        """Send Redis command using RESP protocol.

        Args:
            sock: Socket to send to
            command: List of command parts
        """
        # Encode command as RESP array
        data = b'*%d\r\n' % len(command)
        for arg in command:
            if isinstance(arg, str):
                arg = arg.encode('utf-8')
            data += b'$%d\r\n%s\r\n' % (len(arg), arg)
        sock.send(data)

    def _receive_response(self, sock: socket.socket) -> Union[bytes, int, List, None]:
        """Receive Redis response using RESP protocol.

        Args:
            sock: Socket to receive from

        Returns:
            Parsed response based on RESP type

        Raises:
            ConnectionError: On protocol error
        """
        # Read first byte to determine response type
        first_byte = sock.recv(1)
        if not first_byte:
            raise ConnectionError('Connection closed')

        if first_byte == self.SIMPLE_STRING:
            return self._read_simple_string(sock)
        elif first_byte == self.ERROR:
            error = self._read_simple_string(sock)
            raise ConnectionError(f'Redis error: {error.decode("utf-8")}')
        elif first_byte == self.INTEGER:
            return self._read_integer(sock)
        elif first_byte == self.BULK_STRING:
            return self._read_bulk_string(sock)
        elif first_byte == self.ARRAY:
            return self._read_array(sock)
        else:
            raise ConnectionError(f'Unknown Redis response type: {first_byte}')

    def _read_line(self, sock: socket.socket) -> bytes:
        """Read line ending with CRLF.

        Args:
            sock: Socket to read from

        Returns:
            Line without CRLF
        """
        line = b''
        while True:
            char = sock.recv(1)
            if not char:
                raise ConnectionError('Connection closed')
            line += char
            if line.endswith(b'\r\n'):
                return line[:-2]

    def _read_simple_string(self, sock: socket.socket) -> bytes:
        """Read simple string response.

        Args:
            sock: Socket to read from

        Returns:
            String bytes
        """
        return self._read_line(sock)

    def _read_integer(self, sock: socket.socket) -> int:
        """Read integer response.

        Args:
            sock: Socket to read from

        Returns:
            Integer value
        """
        line = self._read_line(sock)
        return int(line)

    def _read_bulk_string(self, sock: socket.socket) -> Optional[bytes]:
        """Read bulk string response.

        Args:
            sock: Socket to read from

        Returns:
            String bytes or None
        """
        length_line = self._read_line(sock)
        length = int(length_line)
        if length == -1:
            return None
        data = sock.recv(length + 2)
        return data[:-2]

    def _read_array(self, sock: socket.socket) -> Optional[List]:
        """Read array response.

        Args:
            sock: Socket to read from

        Returns:
            List of elements or None
        """
        length_line = self._read_line(sock)
        length = int(length_line)
        if length == -1:
            return None

        result = []
        for _ in range(length):
            result.append(self._receive_response(sock))
        return result

    def get(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Get value for key.

        Args:
            key: Redis key
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Value or None if not found

        Example:
            factory = RedisFactory()
            value = factory.get(key="mykey", host="localhost", port=6379)
        """
        self.logger.debug(f"Redis GET: {key}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['GET', key])
        return self._receive_response(conn)

    def set(
        self,
        key: str,
        value: Union[str, bytes],
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Set key to value.

        Args:
            key: Redis key
            value: Value to set
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password
            ex: Expiration in seconds
            px: Expiration in milliseconds

        Returns:
            True if successful

        Example:
            factory = RedisFactory()
            factory.set(key="mykey", value="myvalue", ex=60)
        """
        self.logger.debug(f"Redis SET: {key}")

        conn = self._get_connection(host, port, db, password)
        command = ['SET', key, value]
        if ex is not None:
            command.extend(['EX', str(ex)])
        if px is not None:
            command.extend(['PX', str(px)])
        self._send_command(conn, command)
        response = self._receive_response(conn)
        return response == b'+OK'

    def delete(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Delete key.

        Args:
            key: Redis key
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Number of keys deleted

        Example:
            factory = RedisFactory()
            count = factory.delete(key="mykey")
        """
        self.logger.debug(f"Redis DELETE: {key}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['DEL', key])
        return self._receive_response(conn)

    def exists(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Check if key exists.

        Args:
            key: Redis key
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            1 if exists, 0 if not

        Example:
            factory = RedisFactory()
            exists = factory.exists(key="mykey")
        """
        self.logger.debug(f"Redis EXISTS: {key}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['EXISTS', key])
        return self._receive_response(conn)

    def keys(
        self,
        pattern: str = '*',
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> List[bytes]:
        """Find keys matching pattern.

        Args:
            pattern: Key pattern (default: '*')
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            List of matching keys

        Example:
            factory = RedisFactory()
            keys = factory.keys(pattern="user:*")
        """
        self.logger.debug(f"Redis KEYS: {pattern}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['KEYS', pattern])
        return self._receive_response(conn)

    def hget(
        self,
        key: str,
        field: str,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> Optional[bytes]:
        """Get hash field value.

        Args:
            key: Hash key
            field: Field name
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Field value or None

        Example:
            factory = RedisFactory()
            value = factory.hget(key="user:1", field="name")
        """
        self.logger.debug(f"Redis HGET: {key}.{field}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['HGET', key, field])
        return self._receive_response(conn)

    def hset(
        self,
        key: str,
        field: str,
        value: Union[str, bytes],
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Set hash field value.

        Args:
            key: Hash key
            field: Field name
            value: Field value
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Number of fields added (1 if new, 0 if updated)

        Example:
            factory = RedisFactory()
            factory.hset(key="user:1", field="name", value="John")
        """
        self.logger.debug(f"Redis HSET: {key}.{field}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['HSET', key, field, value])
        return self._receive_response(conn)

    def hgetall(
        self,
        key: str,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> Dict[bytes, bytes]:
        """Get all hash fields and values.

        Args:
            key: Hash key
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Dictionary of fields and values

        Example:
            factory = RedisFactory()
            data = factory.hgetall(key="user:1")
        """
        self.logger.debug(f"Redis HGETALL: {key}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['HGETALL', key])
        result = self._receive_response(conn)
        if not result:
            return {}
        return dict(zip(result[::2], result[1::2]))

    def lpush(
        self,
        key: str,
        *values: Union[str, bytes],
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Prepend values to list.

        Args:
            key: List key
            values: Values to prepend
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            New list length

        Example:
            factory = RedisFactory()
            length = factory.lpush(key="mylist", "value1", "value2")
        """
        self.logger.debug(f"Redis LPUSH: {key}")

        conn = self._get_connection(host, port, db, password)
        command = ['LPUSH', key] + list(values)
        self._send_command(conn, command)
        return self._receive_response(conn)

    def rpush(
        self,
        key: str,
        *values: Union[str, bytes],
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Append values to list.

        Args:
            key: List key
            values: Values to append
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            New list length

        Example:
            factory = RedisFactory()
            length = factory.rpush(key="mylist", "value1", "value2")
        """
        self.logger.debug(f"Redis RPUSH: {key}")

        conn = self._get_connection(host, port, db, password)
        command = ['RPUSH', key] + list(values)
        self._send_command(conn, command)
        return self._receive_response(conn)

    def lrange(
        self,
        key: str,
        start: int = 0,
        stop: int = -1,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> List[bytes]:
        """Get range of list elements.

        Args:
            key: List key
            start: Start index (0-based)
            stop: Stop index (-1 for end)
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            List of elements

        Example:
            factory = RedisFactory()
            items = factory.lrange(key="mylist", start=0, stop=10)
        """
        self.logger.debug(f"Redis LRANGE: {key}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['LRANGE', key, str(start), str(stop)])
        return self._receive_response(conn)

    def publish(
        self,
        channel: str,
        message: Union[str, bytes],
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> int:
        """Publish message to channel.

        Args:
            channel: Channel name
            message: Message to publish
            host: Redis server host
            port: Redis server port
            db: Database number
            password: Optional password

        Returns:
            Number of subscribers who received message

        Example:
            factory = RedisFactory()
            subs = factory.publish(channel="events", message="hello")
        """
        self.logger.debug(f"Redis PUBLISH: {channel}")

        conn = self._get_connection(host, port, db, password)
        self._send_command(conn, ['PUBLISH', channel, message])
        return self._receive_response(conn)


__all__ = [
    "RedisFactory",
]
