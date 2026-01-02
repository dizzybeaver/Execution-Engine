"""
WebSocket Factory - Networking Domain

WebSocket client implementation using standard library only.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Basic WebSocket handshake and frame handling
"""

import hashlib
import base64
import struct
import logging
import socket
from typing import Any, Dict, Optional, Callable, Union


class WebSocketFactory:
    """WebSocket factory.

    Provides WebSocket client operations:
    - Connect to WebSocket server
    - Send messages
    - Receive messages
    - Close connection

    UG-ISP Compliance:
    - Uses only standard library
    - Implements WebSocket protocol (RFC 6455)
    - Cross-domain calls via call_operation callback

    Note: This is a basic implementation. For production use,
    consider using the 'websocket-client' library.
    """

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize WebSocket factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.websocket")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._url: Optional[str] = None

    def _generate_websocket_key(self) -> str:
        """Generate WebSocket handshake key.

        Returns:
            Base64-encoded WebSocket key
        """
        # Generate 16-byte random key
        import os
        key_bytes = os.urandom(16)
        return base64.b64encode(key_bytes).decode('utf-8')

    def _parse_url(self, url: str) -> Dict[str, Any]:
        """Parse WebSocket URL.

        Args:
            url: WebSocket URL (ws:// or wss://)

        Returns:
            Dictionary with host, port, path, is_ssl
        """
        if url.startswith('wss://'):
            is_ssl = True
            host_path = url[6:]
        elif url.startswith('ws://'):
            is_ssl = False
            host_path = url[5:]
        else:
            raise ValueError(f"Invalid WebSocket URL: {url}")

        # Split host and path
        parts = host_path.split('/', 1)
        host = parts[0]
        path = '/' + parts[1] if len(parts) > 1 else '/'

        # Extract port
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        else:
            port = 443 if is_ssl else 80

        return {
            'host': host,
            'port': port,
            'path': path,
            'is_ssl': is_ssl
        }

    def _do_handshake(self, url: str, headers: Optional[Dict[str, str]] = None) -> bool:
        """Perform WebSocket handshake.

        Args:
            url: WebSocket URL
            headers: Additional headers

        Returns:
            True if handshake successful
        """
        parsed = self._parse_url(url)

        # Generate WebSocket key
        key = self._generate_websocket_key()

        # Build handshake request
        request_headers = {
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': key,
            'Sec-WebSocket-Version': '13',
        }

        if headers:
            request_headers.update(headers)

        # Build HTTP request
        request_lines = [
            f"GET {parsed['path']} HTTP/1.1",
            f"Host: {parsed['host']}:{parsed['port']}",
        ]

        for header_name, header_value in request_headers.items():
            request_lines.append(f"{header_name}: {header_value}")

        request = '\r\n'.join(request_lines) + '\r\n\r\n'

        # Send handshake
        if parsed['is_ssl']:
            import ssl
            context = ssl.create_default_context()
            self._socket = context.wrap_socket(
                self._socket,
                server_hostname=parsed['host']
            )

        self._socket.send(request.encode('utf-8'))

        # Receive handshake response
        response = self._socket.recv(4096).decode('utf-8')

        # Validate response
        if '101 Switching Protocols' not in response:
            raise ConnectionError(f"WebSocket handshake failed: {response}")

        # Validate Sec-WebSocket-Accept
        lines = response.split('\r\n')
        for line in lines:
            if line.startswith('Sec-WebSocket-Accept:'):
                accept_key = line.split(':', 1)[1].strip()

                # Compute expected accept
                magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                expected = base64.b64encode(
                    hashlib.sha1((key + magic_string).encode()).digest()
                ).decode('utf-8')

                if accept_key != expected:
                    raise ConnectionError("Invalid Sec-WebSocket-Accept")

                break
        else:
            raise ConnectionError("Missing Sec-WebSocket-Accept header")

        self._connected = True
        self._url = url
        return True

    def _encode_frame(self, data: Union[str, bytes], opcode: int = 0x01) -> bytes:
        """Encode WebSocket frame.

        Args:
            data: Data to send
            opcode: Frame opcode (0x01=text, 0x02=binary)

        Returns:
            Encoded frame bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        length = len(data)

        # Build frame
        if length < 126:
            frame = bytes([0x80 | opcode, length])
        elif length < 65536:
            frame = bytes([0x80 | opcode, 126, length >> 8, length & 0xFF])
        else:
            frame = bytes([
                0x80 | opcode, 127,
                (length >> 56) & 0xFF, (length >> 48) & 0xFF,
                (length >> 40) & 0xFF, (length >> 32) & 0xFF,
                (length >> 24) & 0xFF, (length >> 16) & 0xFF,
                (length >> 8) & 0xFF, length & 0xFF
            ])

        return frame + data

    def _decode_frame(self, data: bytes) -> Dict[str, Any]:
        """Decode WebSocket frame.

        Args:
            data: Frame bytes

        Returns:
            Dictionary with opcode, payload, fin
        """
        if len(data) < 2:
            raise ValueError("Invalid frame: too short")

        byte1 = data[0]
        byte2 = data[1]

        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0F
        masked = bool(byte2 & 0x80)
        payload_length = byte2 & 0x7F

        offset = 2

        # Extended payload length
        if payload_length == 126:
            if len(data) < 4:
                raise ValueError("Invalid frame: extended length incomplete")
            payload_length = (data[2] << 8) | data[3]
            offset = 4
        elif payload_length == 127:
            if len(data) < 10:
                raise ValueError("Invalid frame: extended length incomplete")
            payload_length = (
                (data[2] << 56) | (data[3] << 48) |
                (data[4] << 40) | (data[5] << 32) |
                (data[6] << 24) | (data[7] << 16) |
                (data[8] << 8) | data[9]
            )
            offset = 10

        # Check data length
        if len(data) < offset + payload_length:
            raise ValueError("Invalid frame: payload incomplete")

        payload = data[offset:offset + payload_length]

        return {
            'fin': fin,
            'opcode': opcode,
            'payload': payload,
        }

    def connect(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Connect to WebSocket server.

        Args:
            url: WebSocket URL (ws:// or wss://)
            headers: Additional headers
            timeout: Connection timeout in seconds

        Returns:
            Connection result dict

        Example:
            factory = WebSocketFactory()
            result = factory.connect(
                url="ws://echo.websocket.org"
            )
        """
        self.logger.debug(f"WebSocket connect: {url}")

        try:
            parsed = self._parse_url(url)

            # Create socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((parsed['host'], parsed['port']))

            # Perform handshake
            self._do_handshake(url, headers)

            return {
                "connected": True,
                "url": url,
                "host": parsed['host'],
                "port": parsed['port']
            }

        except Exception as e:
            self._connected = False
            if self._socket:
                self._socket.close()
                self._socket = None
            raise ConnectionError(f"WebSocket connection failed: {e}")

    def send(
        self,
        message: Union[str, bytes],
        url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send message via WebSocket.

        Args:
            message: Message to send (string or bytes)
            url: WebSocket URL (if not already connected)

        Returns:
            Send result dict

        Example:
            factory = WebSocketFactory()
            factory.connect(url="ws://echo.websocket.org")
            factory.send("Hello, WebSocket!")
        """
        self.logger.debug(f"WebSocket send: {len(str(message))} bytes")

        if not self._connected or not self._socket:
            if url:
                self.connect(url)
            else:
                raise ConnectionError("WebSocket not connected")

        try:
            # Encode and send frame
            frame = self._encode_frame(message, opcode=0x01)
            self._socket.send(frame)

            return {
                "sent": True,
                "length": len(str(message))
            }

        except Exception as e:
            raise RuntimeError(f"WebSocket send failed: {e}")

    def receive(
        self,
        url: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Receive message from WebSocket.

        Args:
            url: WebSocket URL (if not already connected)
            timeout: Receive timeout in seconds

        Returns:
            Receive result dict with message data

        Example:
            factory = WebSocketFactory()
            factory.connect(url="ws://echo.websocket.org")
            factory.send("Hello")
            result = factory.receive()
            print(result['message'])
        """
        self.logger.debug("WebSocket receive")

        if not self._connected or not self._socket:
            if url:
                self.connect(url)
            else:
                raise ConnectionError("WebSocket not connected")

        try:
            if timeout:
                self._socket.settimeout(timeout)

            # Receive frame
            data = self._socket.recv(4096)
            frame = self._decode_frame(data)

            # Decode payload
            message = frame['payload']
            if frame['opcode'] == 0x01:  # Text frame
                message = message.decode('utf-8')

            return {
                "received": True,
                "message": message,
                "opcode": frame['opcode'],
                "fin": frame['fin']
            }

        except socket.timeout:
            return {
                "received": False,
                "timeout": True
            }
        except Exception as e:
            raise RuntimeError(f"WebSocket receive failed: {e}")

    def close(
        self,
        code: int = 1000,
        reason: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Close WebSocket connection.

        Args:
            code: Close code (default: 1000 - normal closure)
            reason: Close reason

        Returns:
            Close result dict

        Example:
            factory = WebSocketFactory()
            factory.connect(url="ws://echo.websocket.org")
            factory.close()
        """
        self.logger.debug("WebSocket close")

        if self._socket:
            try:
                # Send close frame
                close_frame = self._encode_frame(reason, opcode=0x08)
                self._socket.send(close_frame)
                self._socket.close()
            except Exception:
                pass

        self._connected = False
        self._socket = None
        self._url = None

        return {
            "closed": True,
            "code": code
        }


__all__ = [
    "WebSocketFactory",
]
