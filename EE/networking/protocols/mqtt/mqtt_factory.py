"""
MQTT Factory - Networking Domain

MQTT protocol implementation (v3.1.1).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Implements MQTT v3.1.1 protocol
"""

import socket
import struct
import random
import logging
from typing import Any, Dict, Optional, Callable, Union


class MQTTFactory:
    """MQTT factory.

    Provides MQTT protocol operations:
    - Connection management: connect, disconnect
    - Messaging: publish, subscribe, unsubscribe
    - Keep-alive: ping
    - Status: get_subscriptions

    UG-ISP Compliance:
    - Uses only standard library
    - Implements MQTT v3.1.1 protocol
    - Cross-domain calls via call_operation callback
    """

    # MQTT message types
    CONNECT = 0x10
    CONNACK = 0x20
    PUBLISH = 0x30
    PUBACK = 0x40
    SUBSCRIBE = 0x80
    SUBACK = 0x90
    UNSUBSCRIBE = 0xA0
    UNSUBACK = 0xB0
    PINGREQ = 0xC0
    PINGRESP = 0xD0
    DISCONNECT = 0xE0

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize MQTT factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.protocols.mqtt")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._message_id = 1
        self._subscriptions: Dict[str, int] = {}

    def _encode_string(self, s: str) -> bytes:
        """Encode string for MQTT (2-byte length + UTF-8).

        Args:
            s: String to encode

        Returns:
            Encoded bytes
        """
        encoded = s.encode('utf-8')
        return len(encoded).to_bytes(2, 'big') + encoded

    def _encode_length(self, length: int) -> bytes:
        """Encode remaining length for MQTT.

        Args:
            length: Length to encode

        Returns:
            Encoded bytes
        """
        encoded = bytearray()
        while True:
            digit = length % 128
            length = length // 128
            if length > 0:
                digit |= 0x80
            encoded.append(digit)
            if length == 0:
                break
        return bytes(encoded)

    def _receive_packet(self, sock: socket.socket) -> Optional[bytes]:
        """Receive complete MQTT packet.

        Args:
            sock: Socket to receive from

        Returns:
            Packet bytes or None
        """
        # Read fixed header
        header = sock.recv(1)
        if not header:
            return None

        # Read remaining length
        remaining_length = 0
        multiplier = 1
        while True:
            byte = sock.recv(1)
            if not byte:
                return None
            remaining_length += (byte[0] & 0x7F) * multiplier
            multiplier *= 128
            if not (byte[0] & 0x80):
                break

        # Read variable header and payload
        if remaining_length > 0:
            payload = sock.recv(remaining_length)
            if len(payload) != remaining_length:
                return None
            return header + payload
        return header

    def connect(
        self,
        host: str,
        port: int = 1883,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: int = 60,
        timeout: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Connect to MQTT broker.

        Args:
            host: MQTT broker host
            port: MQTT broker port (default: 1883)
            client_id: Client ID (auto-generated if None)
            username: Optional username
            password: Optional password
            keepalive: Keep-alive interval in seconds
            timeout: Connection timeout

        Returns:
            Connection result dict

        Example:
            factory = MQTTFactory()
            result = factory.connect(host="mqtt.example.com", port=1883)
        """
        self.logger.debug(f"MQTT connect: {host}:{port}")

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((host, port))

            # Client ID
            if not client_id:
                client_id = f'mqtt-{random.randint(0, 10000)}'

            # Build CONNECT packet
            flags = 0x02  # Clean session
            if username:
                flags |= 0x80
                if password:
                    flags |= 0x40

            protocol = b'\x00\x06MQIsdp\x03'
            payload = self._encode_string(client_id)
            if username:
                payload += self._encode_string(username)
            if password:
                payload += self._encode_string(password)

            variable_header = protocol + bytes([flags]) + keepalive.to_bytes(2, 'big')
            remaining_length = len(variable_header) + len(payload)
            fixed_header = bytes([self.CONNECT]) + self._encode_length(remaining_length)

            packet = fixed_header + variable_header + payload
            self._socket.send(packet)

            # Receive CONNACK
            response = self._receive_packet(self._socket)
            if not response or response[0] != self.CONNACK:
                raise ConnectionError('MQTT connection failed')

            return_code = response[3]
            if return_code != 0x00:
                raise ConnectionError(f'MQTT connection refused: code {return_code}')

            self._connected = True
            return {"connected": True, "client_id": client_id}

        except Exception as e:
            self._connected = False
            raise ConnectionError(f'MQTT connection failed: {e}')

    def disconnect(self, **kwargs) -> Dict[str, Any]:
        """Disconnect from MQTT broker.

        Returns:
            Disconnect result dict

        Example:
            factory = MQTTFactory()
            factory.disconnect()
        """
        self.logger.debug("MQTT disconnect")

        if self._socket and self._connected:
            try:
                self._socket.send(bytes([self.DISCONNECT, 0x00]))
                self._socket.close()
            except Exception:
                pass

        self._connected = False
        self._socket = None
        self._subscriptions.clear()

        return {"disconnected": True}

    def publish(
        self,
        topic: str,
        payload: Union[str, bytes],
        host: str,
        port: int = 1883,
        qos: int = 0,
        retain: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Publish message to topic.

        Args:
            topic: Topic name
            payload: Message payload
            host: MQTT broker host
            port: MQTT broker port
            qos: Quality of service (0 or 1)
            retain: Retain flag

        Returns:
            Publish result dict

        Example:
            factory = MQTTFactory()
            factory.publish(
                topic="sensors/temperature",
                payload="22.5",
                host="mqtt.example.com"
            )
        """
        self.logger.debug(f"MQTT publish: {topic}")

        if not self._connected or not self._socket:
            # Auto-connect
            self.connect(host=host, port=port)

        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        flags = (qos << 1) | (1 if retain else 0)
        variable_header = self._encode_string(topic)

        if qos > 0:
            message_id = self._message_id
            self._message_id = (self._message_id + 1) % 65536
            variable_header += message_id.to_bytes(2, 'big')

        remaining_length = len(variable_header) + len(payload)
        fixed_header = bytes([self.PUBLISH | flags]) + self._encode_length(remaining_length)

        packet = fixed_header + variable_header + payload
        self._socket.send(packet)

        # QoS 1: Wait for PUBACK
        if qos == 1:
            response = self._receive_packet(self._socket)
            if not response or response[0] != self.PUBACK:
                raise ConnectionError('QoS 1 publish failed')

        return {"published": True, "topic": topic, "qos": qos}

    def subscribe(
        self,
        topic: str,
        host: str,
        port: int = 1883,
        qos: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Subscribe to topic.

        Args:
            topic: Topic filter
            host: MQTT broker host
            port: MQTT broker port
            qos: Maximum QoS level (0 or 1)

        Returns:
            Subscribe result dict with granted QoS

        Example:
            factory = MQTTFactory()
            result = factory.subscribe(
                topic="sensors/#",
                host="mqtt.example.com"
            )
        """
        self.logger.debug(f"MQTT subscribe: {topic}")

        if not self._connected or not self._socket:
            self.connect(host=host, port=port)

        message_id = self._message_id
        self._message_id = (self._message_id + 1) % 65536

        variable_header = message_id.to_bytes(2, 'big')
        payload = self._encode_string(topic) + bytes([qos])

        remaining_length = len(variable_header) + len(payload)
        fixed_header = bytes([self.SUBSCRIBE | 0x02]) + self._encode_length(remaining_length)

        packet = fixed_header + variable_header + payload
        self._socket.send(packet)

        # Wait for SUBACK
        response = self._receive_packet(self._socket)
        if not response or response[0] != self.SUBACK:
            raise ConnectionError('Subscribe failed')

        granted_qos = response[4]
        self._subscriptions[topic] = granted_qos

        return {"subscribed": True, "topic": topic, "qos": granted_qos}

    def unsubscribe(
        self,
        topic: str,
        host: str,
        port: int = 1883,
        **kwargs
    ) -> Dict[str, Any]:
        """Unsubscribe from topic.

        Args:
            topic: Topic filter
            host: MQTT broker host
            port: MQTT broker port

        Returns:
            Unsubscribe result dict

        Example:
            factory = MQTTFactory()
            factory.unsubscribe(topic="sensors/#", host="mqtt.example.com")
        """
        self.logger.debug(f"MQTT unsubscribe: {topic}")

        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to MQTT broker")

        message_id = self._message_id
        self._message_id = (self._message_id + 1) % 65536

        variable_header = message_id.to_bytes(2, 'big')
        payload = self._encode_string(topic)

        remaining_length = len(variable_header) + len(payload)
        fixed_header = bytes([self.UNSUBSCRIBE | 0x02]) + self._encode_length(remaining_length)

        packet = fixed_header + variable_header + payload
        self._socket.send(packet)

        # Wait for UNSUBACK
        response = self._receive_packet(self._socket)
        if not response or response[0] != self.UNSUBACK:
            raise ConnectionError('Unsubscribe failed')

        if topic in self._subscriptions:
            del self._subscriptions[topic]

        return {"unsubscribed": True, "topic": topic}

    def ping(self, **kwargs) -> Dict[str, Any]:
        """Send ping request to keep connection alive.

        Returns:
            Ping result dict

        Example:
            factory = MQTTFactory()
            factory.connect(host="mqtt.example.com")
            result = factory.ping()
        """
        self.logger.debug("MQTT ping")

        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to MQTT broker")

        self._socket.send(bytes([self.PINGREQ, 0x00]))
        response = self._receive_packet(self._socket)

        success = response is not None and response[0] == self.PINGRESP
        return {"ping": success}

    def get_subscriptions(self, **kwargs) -> Dict[str, int]:
        """Get active subscriptions.

        Returns:
            Dictionary mapping topics to QoS levels

        Example:
            factory = MQTTFactory()
            subs = factory.get_subscriptions()
        """
        return dict(self._subscriptions)


__all__ = [
    "MQTTFactory",
]
