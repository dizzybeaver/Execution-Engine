"""network/ws_core_frame.py

WebSocket frame send/recv and handshake functionality.

This module contains the frame-level operations and handshake logic
for WebSocketClient. Kept separate to maintain 350-line file limit.
"""

from typing import Optional
import base64
import hashlib
import os
import socket
import struct
import time

# Import WebSocketClient for method binding
from lee.network.ws_core import WebSocketClient, WebSocketClosed, WebSocketError

# Debug support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


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


# Handshake
# pylint: disable=too-many-locals,too-many-statements
def _perform_handshake(self, parsed, host: str, port: int) -> None:
    assert self._sock is not None  # pylint: disable=protected-access
    sock = self._sock  # pylint: disable=protected-access

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='WebSocket handshake starting',
                             scope='WS_FRAME', host=host, port=port)
        except (ImportError, AttributeError):
            pass

    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    key = _generate_key()

    headers: dict[str, str] = {
        "Host": f"{host}:{port}",
        "Upgrade": "websocket",
        "Connection": "Upgrade",
        "Sec-WebSocket-Key": key,
        "Sec-WebSocket-Version": "13",
    }

    if self.subprotocols:
        headers["Sec-WebSocket-Protocol"] = ", ".join(self.subprotocols)

    # Application-level auth
    if self.auth_header_factory:
        for hk, hv in (self.auth_header_factory() or {}).items():
            headers[hk] = hv

    # User-supplied headers override defaults/auth
    for k, v in self.headers.items():
        headers[k] = v

    # If ws:// via proxy with auth on proxy, we may need Proxy-Authorization
    proxy_auth = getattr(self, "_proxy_auth_header", None)
    if proxy_auth:
        headers.setdefault("Proxy-Authorization", proxy_auth)

    # Build request
    request_lines = [f"GET {path} HTTP/1.1"]
    for k, v in headers.items():
        request_lines.append(f"{k}: {v}")
    request_lines.append("\r\n")

    sock.sendall("\r\n".join(request_lines).encode("utf-8"))

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='WebSocket handshake request sent',
                             scope='WS_FRAME', path=path, subprotocols=self.subprotocols)
        except (ImportError, AttributeError):
            pass

    status_line, resp_headers = self._read_http_response_headers(sock)  # pylint: disable=protected-access

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='WebSocket handshake response received',
                             scope='WS_FRAME', status_line=status_line)
        except (ImportError, AttributeError):
            pass

    if not status_line.startswith("HTTP/1.1 101"):
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='WebSocket handshake failed',
                                 scope='WS_FRAME', status_line=status_line)
            except (ImportError, AttributeError):
                pass
        raise WebSocketError(f"Handshake failed: {status_line}")

    accept = resp_headers.get("sec-websocket-accept")
    if accept != _compute_accept(key):
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Invalid Sec-WebSocket-Accept',
                                 scope='WS_FRAME')
            except (ImportError, AttributeError):
                pass
        raise WebSocketError("Invalid Sec-WebSocket-Accept in handshake")

    self._selected_subprotocol = resp_headers.get("sec-websocket-protocol")  # pylint: disable=protected-access

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='WebSocket handshake completed',
                             scope='WS_FRAME', subprotocol=self._selected_subprotocol)
        except (ImportError, AttributeError):
            pass


# Frame send
def _send_frame(self, opcode: int, payload: bytes) -> None:  # pylint: disable=protected-access
    if not self._connected or self._sock is None:  # pylint: disable=protected-access
        raise WebSocketClosed("WebSocket is not connected")

    sock = self._sock  # pylint: disable=protected-access

    # Opcode names for debug logging
    _OPCODE_NAMES = {
        0x0: "CONT",
        0x1: "TEXT",
        0x2: "BINARY",
        0x8: "CLOSE",
        0x9: "PING",
        0xA: "PONG",
    }

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Sending frame',
                             scope='WS_FRAME',
                             opcode=_OPCODE_NAMES.get(opcode, f"0x{opcode:X}"),
                             payload_length=len(payload))
        except (ImportError, AttributeError):
            pass

    with self._send_lock:  # pylint: disable=protected-access
        fin = 0x80
        b1 = fin | (opcode & 0x0F)

        mask_bit = 0x80
        length = len(payload)

        header = bytearray()
        header.append(b1)

        if length < 126:
            header.append(mask_bit | length)
        elif length < (1 << 16):
            header.append(mask_bit | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(mask_bit | 127)
            header.extend(struct.pack("!Q", length))

        masking_key = os.urandom(4)
        header.extend(masking_key)
        masked_data = _mask_payload(masking_key, payload)

        sock.sendall(header + masked_data)

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Frame sent successfully',
                                 scope='WS_FRAME',
                                 opcode=_OPCODE_NAMES.get(opcode, f"0x{opcode:X}"),
                                 payload_length=len(payload))
            except (ImportError, AttributeError):
                pass


def _recv_exact(self, n: int) -> bytes:  # pylint: disable=protected-access
    if not self._connected or self._sock is None:  # pylint: disable=protected-access
        raise WebSocketClosed("WebSocket is not connected")

    sock = self._sock  # pylint: disable=protected-access

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Receiving exact bytes',
                             scope='WS_FRAME', bytes_requested=n)
        except (ImportError, AttributeError):
            pass

    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Socket closed while receiving',
                                     scope='WS_FRAME', bytes_received=len(buf),
                                     bytes_expected=n)
                except (ImportError, AttributeError):
                    pass
            self._teardown()  # pylint: disable=protected-access
            raise WebSocketClosed("Socket closed while receiving")
        buf.extend(chunk)
    return bytes(buf)


def _recv_frame(self) -> tuple[int, bool, bytes]:  # pylint: disable=protected-access
    header = self._recv_exact(2)  # pylint: disable=protected-access
    b1, b2 = header[0], header[1]

    fin = (b1 & 0x80) != 0
    opcode = b1 & 0x0F
    masked = (b2 & 0x80) != 0
    length = b2 & 0x7F

    # Opcode names for debug logging
    _OPCODE_NAMES = {
        0x0: "CONT",
        0x1: "TEXT",
        0x2: "BINARY",
        0x8: "CLOSE",
        0x9: "PING",
        0xA: "PONG",
    }

    if length == 126:
        (length,) = struct.unpack("!H", self._recv_exact(2))  # pylint: disable=protected-access
    elif length == 127:
        (length,) = struct.unpack("!Q", self._recv_exact(8))  # pylint: disable=protected-access

    masking_key = self._recv_exact(4) if masked else b""  # pylint: disable=protected-access
    payload = self._recv_exact(length)  # pylint: disable=protected-access

    if masked:
        payload = _mask_payload(masking_key, payload)

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Received frame',
                             scope='WS_FRAME',
                             opcode=_OPCODE_NAMES.get(opcode, f"0x{opcode:X}"),
                             fin=fin, masked=masked, payload_length=len(payload))
        except (ImportError, AttributeError):
            pass

    return opcode, fin, payload


def _recv_message(self) -> tuple[Optional[bytes], bool]:  # pylint: disable=too-many-locals

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Starting message receive',
                             scope='WS_FRAME')
        except (ImportError, AttributeError):
            pass

    parts: list[bytes] = []
    started = False
    is_text = False
    frame_count = 0

    # SECURITY: Add 30-second timeout to prevent infinite loops
    # Rationale: Allows sufficient time for large fragmented messages while
    # preventing malicious servers from hanging the connection indefinitely
    timeout = time.time() + 30

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Starting message receive with 30-second timeout',
                             scope='WS_FRAME',
                             rationale='Prevents infinite loops from malformed frames')
        except (ImportError, AttributeError):
            pass

    # Opcode dispatch dictionary for frame handling
    def _handle_cont_frame(payload: bytes) -> None:
        """Handle continuation frame."""
        nonlocal started
        if not started:
            raise WebSocketError("Unexpected continuation frame")
        parts.append(payload)

    def _handle_data_frame(payload: bytes, opcode: int) -> None:  # pylint: disable=unused-argument
        """Handle data frame (text or binary)."""
        nonlocal started, is_text
        if started:
            raise WebSocketError("New data frame before previous finished")
        started = True
        is_text = (opcode == OP_TEXT)
        parts.append(payload)

    def _handle_ping_frame(payload: bytes) -> None:
        """Handle ping frame."""
        self.send_pong(payload)

    def _handle_pong_frame(_payload: bytes) -> None:
        """Handle pong frame."""

    def _handle_close_frame(payload: bytes) -> tuple[Optional[bytes], bool]:
        """Handle close frame and return termination signal."""
        code = None
        reason = ""
        if len(payload) >= 2:
            (code,) = struct.unpack("!H", payload[:2])
            if len(payload) > 2:
                reason = payload[2:].decode("utf-8", "replace")

        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Received close frame',
                                 scope='WS_FRAME', code=code, reason=reason)
            except (ImportError, AttributeError):
                pass

        self._close_code = code  # pylint: disable=protected-access
        self._close_reason = reason  # pylint: disable=protected-access

        if self._connected:  # pylint: disable=protected-access
            try:
                self._send_frame(OP_CLOSE, payload)  # pylint: disable=protected-access
            except (ConnectionError, OSError, WebSocketError):
                # Optional dependency - continue if unavailable
                ...

        self._teardown()  # pylint: disable=protected-access
        return None, False

    # Opcode dispatch table for O(1) handler lookup
    _OPCODE_DISPATCH = {
        OP_CONT: {
            "handler": _handle_cont_frame,
            "type": "continuation",
            "description": "Continuation frame",
        },
        OP_TEXT: {
            "handler": lambda p: _handle_data_frame(p, OP_TEXT),
            "type": "data",
            "description": "Text data frame",
        },
        OP_BINARY: {
            "handler": lambda p: _handle_data_frame(p, OP_BINARY),
            "type": "data",
            "description": "Binary data frame",
        },
        OP_PING: {
            "handler": _handle_ping_frame,
            "type": "control",
            "description": "Ping control frame",
        },
        OP_PONG: {
            "handler": _handle_pong_frame,
            "type": "control",
            "description": "Pong control frame",
        },
        OP_CLOSE: {
            "handler": _handle_close_frame,
            "type": "control",
            "description": "Close control frame",
        },
    }

    while time.time() < timeout:
        opcode, fin, payload = self._recv_frame()  # pylint: disable=protected-access
        frame_count += 1

        opcode_entry = _OPCODE_DISPATCH.get(opcode)
        if not opcode_entry:
            if _DEBUG_ENABLED:
                try:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message='Unsupported opcode received',
                                     scope='WS_FRAME', opcode=opcode)
                except (ImportError, AttributeError):
                    pass
            raise WebSocketError(f"Unsupported opcode: {opcode}")

        handler = opcode_entry["handler"]
        opcode_type = opcode_entry["type"]

        # Special handling for close frame (returns termination signal)
        if opcode == OP_CLOSE:
            return handler(payload)

        # Handle data frames with FIN flag
        if opcode_type == "data":
            handler(payload)
            if fin:
                break
        # Handle continuation frames
        elif opcode == OP_CONT:
            handler(payload)
            if fin:
                break
        # Handle control frames (no FIN check needed)
        else:
            handler(payload)
            continue

    # Check if we timed out
    if time.time() >= timeout:
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Message receive timed out',
                                 scope='WS_FRAME', frame_count=frame_count)
            except (ImportError, AttributeError):
                pass
        raise TimeoutError("WebSocket message reception timed out after 30 seconds")

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Message receive completed',
                             scope='WS_FRAME', frame_count=frame_count,
                             is_text=is_text, total_bytes=sum(len(p) for p in parts))
        except (ImportError, AttributeError):
            pass

    if not started:
        return b"", False

    return b"".join(parts), is_text


# HTTP response parser
def _read_http_response_headers(
    self, sock: socket.socket,
) -> tuple[str, dict]:
    def read_line() -> str:
        buf = bytearray()
        # 30-second timeout per line prevents hanging on malformed responses
        timeout = time.time() + 30
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Reading HTTP header line with 30-second timeout',
                                 scope='WS_FRAME')
            except (ImportError, AttributeError):
                pass
        while time.time() < timeout:
            ch = sock.recv(1)
            if not ch:
                break
            buf.extend(ch)
            if buf.endswith(b"\r\n"):
                break
        else:
            raise TimeoutError("HTTP header line read timed out after 30 seconds")
        return buf.decode("iso-8859-1").rstrip("\r\n")

    status_line = read_line()
    headers = {}
    # 30-second timeout for entire header block prevents slowloris attacks
    timeout = time.time() + 30
    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='Reading HTTP headers with 30-second timeout',
                             scope='WS_FRAME',
                             rationale='Prevents slowloris attacks')
        except (ImportError, AttributeError):
            pass
    while time.time() < timeout:
        line = read_line()
        if not line:
            break
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()
    else:
        raise TimeoutError("HTTP headers read timed out after 30 seconds")
    return status_line, headers


# Teardown & context manager
def _teardown(self) -> None:  # pylint: disable=protected-access
    if self._sock:  # pylint: disable=protected-access
        if _DEBUG_ENABLED:
            try:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message='Tearing down WebSocket connection',
                                 scope='WS_FRAME')
            except (ImportError, AttributeError):
                pass
        try:
            self._sock.shutdown(socket.SHUT_RDWR)  # pylint: disable=protected-access
        except (OSError, ConnectionError):
            # Socket already closed or shutdown - continue with cleanup
            ...
        try:
            self._sock.close()  # pylint: disable=protected-access
        except (OSError, ConnectionError):
            # Socket already closed - continue with cleanup
            ...
    self._sock = None  # pylint: disable=protected-access
    self._connected = False  # pylint: disable=protected-access

    if _DEBUG_ENABLED:
        try:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message='WebSocket teardown completed',
                             scope='WS_FRAME')
        except (ImportError, AttributeError):
            pass


def __enter__(self) -> "WebSocketClient":
    self.connect()
    return self


def __exit__(self, _exc_type, _exc, _tb) -> None:  # pylint: disable=unused-argument
    self.close()


# Bind methods to WebSocketClient
WebSocketClient._perform_handshake = _perform_handshake
WebSocketClient._send_frame = _send_frame
WebSocketClient._recv_exact = _recv_exact
WebSocketClient._recv_frame = _recv_frame
WebSocketClient._recv_message = _recv_message
WebSocketClient._read_http_response_headers = _read_http_response_headers
WebSocketClient._teardown = _teardown
WebSocketClient.__enter__ = __enter__
WebSocketClient.__exit__ = __exit__
