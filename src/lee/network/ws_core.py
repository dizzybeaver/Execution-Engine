"""network/ws_core.py

Core stdlib WebSocket client with ws:// and wss:// support,
HTTP proxy, auth header injection, and fragmentation handling.

This is intentionally unaware of any specific auth scheme or application
(Home Assistant, etc.) — that's layered above.
"""

from typing import Optional
import base64
import hashlib
import os
import socket
import ssl
import struct
import threading
import urllib.parse
from collections.abc import Callable

from lee.lee_config.constants import WEBSOCKET_CONNECT_TIMEOUT

# Debug support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"

__all__ = [
    "WebSocketClient",
    "WebSocketClosed",
    "WebSocketError",
]

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


# Exceptions
class WebSocketError(Exception):
    """Base error for WebSocket operations."""


class WebSocketClosed(WebSocketError):
    """Raised when operations are attempted on a closed WebSocket."""


# Internal helpers
def _generate_key() -> str:
    return base64.b64encode(os.urandom(16)).decode("ascii")


def _compute_accept(key: str) -> str:
    # SHA-1 required by WebSocket RFC 6455 for Sec-WebSocket-Accept header
    # This is protocol compliance, not a security operation
    # See: https://datatracker.ietf.org/doc/html/rfc6455#section-1.3
    sha1 = hashlib.sha1()
    sha1.update(key.encode("ascii"))
    sha1.update(_WS_GUID.encode("ascii"))
    return base64.b64encode(sha1.digest()).decode("ascii")


def _mask_payload(masking_key: bytes, payload: bytes) -> bytes:
    return bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))


OP_CONT = 0x0
OP_TEXT = 0x1
OP_BINARY = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xA


# Core WebSocketClient
class WebSocketClient:  # pylint: disable=too-many-instance-attributes
    """Core WebSocket client.

    Key knobs:
      - url: ws:// or wss://
      - timeout: socket timeout
      - headers: extra HTTP headers
      - subprotocols: list of requested subprotocols
      - verify_ssl: toggle TLS verification
      - proxy: "http://host:port" (basic HTTP proxy)
      - auth_header_factory: callable returning {header_name: value} for auth

    The client is intentionally synchronous and stdlib-only.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        *,
        timeout: Optional[float] = WEBSOCKET_CONNECT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
        subprotocols: Optional[list] = None,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        auth_header_factory: Optional[Callable[[], dict[str, str]]] = None,
    ) -> None:
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='WebSocketClient.__init__ ENTRY',
                                 scope='WS_CORE', url=url, timeout=timeout,
                                 verify_ssl=verify_ssl)
            except (ImportError, AttributeError):
                pass
        self.url = url
        self.timeout = timeout
        self.headers = headers or {}
        self.subprotocols = subprotocols or []
        # SECURITY: Only allow SSL verification bypass in non-production environments
        if not verify_ssl:
            is_production = os.environ.get('PRODUCTION', 'false').lower() == 'true'
            if is_production:
                if _DEBUG_ENABLED:
                    try:
                        from lee.gateway import execute_operation, GatewayInterface
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message='SSL verification bypass rejected - production environment',
                                         scope='WS_CORE')
                    except (ImportError, AttributeError):
                        pass
                raise ValueError(
                    "SSL verification cannot be disabled in production. "
                    "Set PRODUCTION=false environment variable for development."
                )
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='SSL verification disabled - development mode',
                                     scope='WS_CORE')
                except (ImportError, AttributeError):
                    pass
        self.verify_ssl = verify_ssl
        self.proxy = proxy or \
            os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or \
            os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        self.auth_header_factory = auth_header_factory

        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._recv_lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._selected_subprotocol: Optional[str] = None
        self._close_code: Optional[int] = None
        self._close_reason: Optional[str] = None

    # Public API
    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected

    @property
    def selected_subprotocol(self) -> Optional[str]:
        """Get the negotiated subprotocol."""
        return self._selected_subprotocol

    @property
    def close_code(self) -> Optional[int]:
        """Get the close code."""
        return self._close_code

    @property
    def close_reason(self) -> Optional[str]:
        """Get the close reason."""
        return self._close_reason

    def connect(self) -> None:
        """Establish TCP/TLS connection and WebSocket handshake."""
        if self._connected:
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='WebSocket already connected, skipping',
                                     scope='WS_CORE', url=self.url)
                except (ImportError, AttributeError):
                    pass
            return

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='WebSocket connect starting',
                                 scope='WS_CORE', url=self.url)
            except (ImportError, AttributeError):
                pass

        parsed = urllib.parse.urlparse(self.url)
        scheme = parsed.scheme
        if scheme not in ("ws", "wss"):
            raise ValueError(f"Unsupported WebSocket scheme: {scheme}")

        host = parsed.hostname
        if host is None:
            raise ValueError(f"Invalid WebSocket URL (no host): {self.url}")

        port = parsed.port or (443 if scheme == "wss" else 80)
        proxy = urllib.parse.urlparse(self.proxy) if self.proxy else None

        if proxy:
            sock = self._connect_via_proxy(parsed, proxy, host, port)
        else:
            sock = self._direct_connect(parsed, host, port)

        self._sock = sock
        self._perform_handshake(parsed, host, port)  # pylint: disable=no-member
        self._connected = True

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='WebSocket connected successfully',
                                 scope='WS_CORE', url=self.url,
                                 scheme=scheme, host=host, port=port,
                                 subprotocol=self._selected_subprotocol)
            except (ImportError, AttributeError):
                pass

    def send_text(self, data: str) -> None:
        """Send a text message."""
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Sending text message',
                                 scope='WS_CORE', length=len(data))
            except (ImportError, AttributeError):
                pass
        self._send_frame(OP_TEXT, data.encode("utf-8"))  # pylint: disable=no-member

    def send_binary(self, data: bytes) -> None:
        """Send a binary message."""
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Sending binary message',
                                 scope='WS_CORE', length=len(data))
            except (ImportError, AttributeError):
                pass
        self._send_frame(OP_BINARY, data)  # pylint: disable=no-member

    def send_ping(self, data: bytes = b"") -> None:
        """Send a ping frame."""
        if len(data) > 125:
            raise ValueError("Ping payload must be <= 125 bytes")
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Sending ping frame',
                                 scope='WS_CORE', payload_length=len(data))
            except (ImportError, AttributeError):
                pass
        self._send_frame(OP_PING, data)  # pylint: disable=no-member

    def send_pong(self, data: bytes = b"") -> None:
        """Send a pong frame."""
        if len(data) > 125:
            raise ValueError("Pong payload must be <= 125 bytes")
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Sending pong frame',
                                 scope='WS_CORE', payload_length=len(data))
            except (ImportError, AttributeError):
                pass
        self._send_frame(OP_PONG, data)  # pylint: disable=no-member

    def close(self, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket connection."""
        if not self._connected:
            return

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Closing WebSocket connection',
                                 scope='WS_CORE', code=code, reason=reason)
            except (ImportError, AttributeError):
                pass

        payload = b""
        if code is not None:
            payload = struct.pack("!H", code)
            if reason:
                payload += reason.encode("utf-8")
        try:
            self._send_frame(OP_CLOSE, payload)  # pylint: disable=no-member
        except (ConnectionError, OSError):
            # Optional dependency - continue if unavailable
            ...
        self._teardown()  # pylint: disable=no-member

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='WebSocket connection closed',
                                 scope='WS_CORE', code=code, reason=reason)
            except (ImportError, AttributeError):
                pass

    def recv(
        self,
        *,
        as_text: bool = True,
        timeout: Optional[float] = None,
    ) -> str | Optional[bytes]:
        """Receive a complete message (possibly fragmented).

        Returns:
          - str for text messages if as_text=True
          - bytes otherwise (or for binary)
          - None if a CLOSE frame is received

        """
        if not self._connected or self._sock is None:
            raise WebSocketClosed("WebSocket is not connected")

        sock = self._sock
        old_timeout = sock.gettimeout()
        if timeout is not None:
            sock.settimeout(timeout)

        try:
            with self._recv_lock:
                payload, is_text = self._recv_message()  # pylint: disable=no-member
        finally:
            sock.settimeout(old_timeout)

        if payload is None:
            return None
        if as_text and is_text:
            return payload.decode("utf-8", "replace")
        return payload


# Low-level connection
def _direct_connect(self, parsed, host: str, port: int) -> socket.socket:
    """Establish direct connection (no proxy)."""
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.settimeout(self.timeout)
    sock = None  # Initialize to avoid fragile locals() check in exception handler

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Starting direct connection',
                             scope='WS_CORE', host=host, port=port,
                             scheme=parsed.scheme)
        except (ImportError, AttributeError):
            pass

    try:
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f'Setting raw socket timeout to {self.timeout}s',
                                 scope='WS_CORE')
            except (ImportError, AttributeError):
                pass
        raw.settimeout(self.timeout)

        if parsed.scheme == "wss":
            ctx = ssl.create_default_context()
            if not self.verify_ssl:
                # Security: Only allow SSL verification bypass in non-production environments
                is_production = os.environ.get('PRODUCTION', 'false').lower() == 'true'
                if is_production:
                    if _DEBUG_ENABLED:
                        try:
                            from lee.gateway import execute_operation, GatewayInterface
                            execute_operation(GatewayInterface.DEBUG, 'log',
                                             message='SSL verification bypass rejected - production environment',
                                             scope='WS_CORE')
                        except (ImportError, AttributeError):
                            pass
                    raise ValueError("SSL verification cannot be disabled in production environment")
                # Log warning when SSL verification is disabled
                import sys
                print("WARNING: SSL verification is disabled - Man-in-the-middle attacks possible", file=sys.stderr)
                if _DEBUG_ENABLED:
                    try:
                        from lee.gateway import execute_operation, GatewayInterface
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message='SSL verification disabled - development mode',
                                         scope='WS_CORE')
                    except (ImportError, AttributeError):
                        pass
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(raw, server_hostname=host)
            # SSL wrapped sockets don't inherit timeout, set it explicitly
            sock.settimeout(self.timeout)
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message=f'SSL wrapped socket timeout set to {self.timeout}s',
                                     scope='WS_CORE')
                except (ImportError, AttributeError):
                    pass

            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='SSL/TLS connection established',
                                     scope='WS_CORE', host=host, port=port)
                except (ImportError, AttributeError):
                    pass
        else:
            sock = raw

        sock.connect((host, port))

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Direct connection established',
                                 scope='WS_CORE', host=host, port=port)
            except (ImportError, AttributeError):
                pass

        return sock
    except (ConnectionError, TimeoutError, OSError) as e:
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Direct connection failed',
                                 scope='WS_CORE', host=host, port=port,
                                 error_type=type(e).__name__, error=str(e))
            except (ImportError, AttributeError):
                pass
        raw.close()
        # Close wrapped socket if it was created (more reliable than 'sock' in locals())
        if sock is not None and sock is not raw:
            sock.close()
        raise


def _connect_via_proxy(  # pylint: disable=too-many-locals
    self,
    parsed,
    proxy,
    host: str,
    port: int,
) -> socket.socket:
    """Establish connection via HTTP proxy."""
    proxy_host = proxy.hostname
    proxy_port = proxy.port or 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(self.timeout)
    wrapped_sock = None

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Starting proxy connection',
                             scope='WS_CORE', proxy_host=proxy_host,
                             proxy_port=proxy_port, target_host=host,
                             target_port=port, scheme=parsed.scheme)
        except (ImportError, AttributeError):
            pass

    try:
        sock.connect((proxy_host, proxy_port))

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Connected to proxy',
                                 scope='WS_CORE', proxy_host=proxy_host,
                                 proxy_port=proxy_port)
            except (ImportError, AttributeError):
                pass

        # Optional: basic proxy auth from proxy URL
        proxy_auth_header = None
        if proxy.username or proxy.password:
            creds = f"{proxy.username or ''}:{proxy.password or ''}"
            token = base64.b64encode(creds.encode("utf-8")).decode("ascii")
            proxy_auth_header = f"Basic {token}"

        # ws:// via proxy: no CONNECT, handshake goes directly through proxy
        if parsed.scheme == "ws":
            self._proxy_auth_header = proxy_auth_header  # pylint: disable=protected-access
            return sock

        # wss:// via proxy: CONNECT then TLS
        connect_lines = [
            f"CONNECT {host}:{port} HTTP/1.1",
            f"Host: {host}:{port}",
            "Proxy-Connection: Keep-Alive",
        ]
        if proxy_auth_header:
            connect_lines.append(f"Proxy-Authorization: {proxy_auth_header}")
        connect_lines.append("\r\n")

        sock.sendall("\r\n".join(connect_lines).encode("ascii"))

        status_line, _headers = self._read_http_response_headers(sock)  # pylint: disable=protected-access
        if not status_line.startswith("HTTP/1.1 200"):
            sock.close()
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Proxy CONNECT failed',
                                     scope='WS_CORE', status_line=status_line)
                except (ImportError, AttributeError):
                    pass
            raise WebSocketError(f"Proxy CONNECT failed: {status_line}")

        ctx = ssl.create_default_context()
        if not self.verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        wrapped_sock = ctx.wrap_socket(sock, server_hostname=host)

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Proxy connection established',
                                 scope='WS_CORE', proxy_host=proxy_host,
                                 proxy_port=proxy_port, target_host=host,
                                 target_port=port)
            except (ImportError, AttributeError):
                pass

        return wrapped_sock
    except (ssl.SSLError, OSError) as e:
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Proxy connection failed',
                                 scope='WS_CORE', proxy_host=proxy_host,
                                 proxy_port=proxy_port, error_type=type(e).__name__,
                                 error=str(e))
            except (ImportError, AttributeError):
                pass
        if wrapped_sock is not None:
            wrapped_sock.close()
        else:
            sock.close()
        raise WebSocketError(f"Proxy connection failed: {e}") from e


# Bind methods to WebSocketClient
WebSocketClient._direct_connect = _direct_connect  # pylint: disable=protected-access
WebSocketClient._connect_via_proxy = _connect_via_proxy  # pylint: disable=protected-access

# Import ws_core_frame to bind handshake and framing methods
# This binds: _perform_handshake, _send_frame, _recv_frame, etc.
from lee.network import ws_core_frame  # noqa: F401 (import triggers side-effect bindings)  pylint: disable=wrong-import-position,unused-import
