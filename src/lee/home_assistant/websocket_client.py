"""home_assistant/websocket_client.py

Home Assistant–specific WebSocket client built on network.ws_core.WebSocketClient.

Handles Home Assistant authentication flow and provides convenience methods
for subscribing to events and calling services.
"""

import json
from typing import Any, Optional

from lee.network.http_auth import bearer_token
from lee.network.ws_core import WebSocketClient, WebSocketError


class HomeAssistantWebSocket:  # pylint: disable=too-many-instance-attributes
    """Home Assistant WebSocket client with automatic authentication.

    Handles:
      - Building correct /api/websocket URL
      - Bearer token authentication
      - Initial auth handshake (auth_required/auth_ok)
      - JSON message convenience methods
      - Event subscription
      - Service calls via WebSocket

    Usage:
        ha_ws = HomeAssistantWebSocket(
            host="homeassistant.local",
            token="YOUR_LONG_LIVED_TOKEN"
        )
        ha_ws.connect_and_auth()
        ha_ws.send_json({"id": 1, "type": "get_config"})
        msg = ha_ws.recv_json()
        print(msg)
        ha_ws.close()
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        *,
        port: Optional[int] = None,
        token: str,
        use_ssl: bool = True,
        timeout: float = 10.0,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize Home Assistant WebSocket client.

        Args:
            host: Home Assistant hostname or IP
            port: Home Assistant port (default: 8123)
            token: Long-lived access token
            use_ssl: Use wss:// (default: True)
            timeout: Connection timeout in seconds
            proxy: Optional proxy URL
            verify_ssl: Verify SSL certificates
            extra_headers: Additional headers to include

        """
        self.host = host
        self.port = port or (8123 if use_ssl else 8123)
        self.token = token
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.extra_headers = extra_headers or {}

        self._client: Optional[WebSocketClient] = None
        self._message_id = 0

    @property
    def url(self) -> str:
        """Get WebSocket URL for Home Assistant."""
        scheme = "wss" if self.use_ssl else "ws"
        return f"{scheme}://{self.host}:{self.port}/api/websocket"

    def _build_client(self) -> WebSocketClient:
        """Build underlying WebSocketClient with auth."""
        auth_factory = bearer_token(self.token)
        return WebSocketClient(
            self.url,
            timeout=self.timeout,
            headers=self.extra_headers,
            subprotocols=[],
            verify_ssl=self.verify_ssl,
            proxy=self.proxy,
            auth_header_factory=auth_factory,
        )

    def connect_and_auth(self) -> None:
        """Connect and perform Home Assistant authentication handshake.

        Process:
            1. Connect to /api/websocket
            2. Receive auth_required message
            3. Send auth message with access_token
            4. Wait for auth_ok (or auth_invalid)

        Raises:
            WebSocketError: If authentication fails

        """
        client = self._build_client()
        client.connect()

        # Expect auth_required
        msg = client.recv(as_text=True)
        if msg is None:
            client.close()
            raise WebSocketError("Home Assistant closed before auth_required")

        try:
            data = json.loads(msg)
        except json.JSONDecodeError as e:
            client.close()
            raise WebSocketError(f"Invalid JSON from HA on connect: {e}") from e
        except Exception as e:
            client.close()
            raise WebSocketError(f"Unexpected error parsing JSON from HA on connect: {e}") from e

        if data.get("type") != "auth_required":
            client.close()
            raise WebSocketError(f"Expected auth_required, got: {data}")

        # Send auth message
        auth_msg = {
            "type": "auth",
            "access_token": self.token,
        }
        client.send_text(json.dumps(auth_msg))

        # Wait for auth_ok / auth_invalid
        msg2 = client.recv(as_text=True)
        if msg2 is None:
            client.close()
            raise WebSocketError("Home Assistant closed during auth")

        try:
            data2 = json.loads(msg2)
        except json.JSONDecodeError as e:
            client.close()
            raise WebSocketError(f"Invalid JSON from HA after auth: {e}") from e
        except Exception as e:
            client.close()
            raise WebSocketError(f"Unexpected error parsing JSON from HA after auth: {e}") from e

        if data2.get("type") != "auth_ok":
            client.close()
            raise WebSocketError(f"Home Assistant auth failed: {data2}")

        self._client = client

    @property
    def client(self) -> WebSocketClient:
        """Get underlying WebSocketClient, raise error if not connected."""
        if not self._client or not self._client.connected:
            raise WebSocketError("HomeAssistantWebSocket is not connected/authenticated")
        return self._client

    def send_json(self, payload: dict[str, Any]) -> None:
        """Send JSON payload to Home Assistant.

        Args:
            payload: Dictionary to send as JSON

        """
        self.client.send_text(json.dumps(payload))

    def recv_json(self, timeout: Optional[float] = None) -> Optional[dict[str, Any]]:
        """Receive JSON message from Home Assistant.

        Args:
            timeout: Receive timeout in seconds

        Returns:
            Parsed JSON message, or None if connection closed

        """
        msg = self.client.recv(as_text=True, timeout=timeout)
        if msg is None:
            return None
        return json.loads(msg)

    def _next_id(self) -> int:
        """Get next message ID."""
        self._message_id += 1
        return self._message_id

    def subscribe_events(self, event_type: Optional[str] = None):
        """Subscribe to Home Assistant events.

        Args:
            event_type: Event type to subscribe to, or None for all events

        Returns:
            Message ID for this subscription

        Example:
            msg_id = ha_ws.subscribe_events("state_changed")
            while True:
                msg = ha_ws.recv_json()
                if msg.get("id") == msg_id:
                    print("Event:", msg)

        """
        payload = {
            "id": self._next_id(),
            "type": "subscribe_events",
        }

        if event_type is not None:
            payload["event_type"] = event_type

        self.send_json(payload)
        return payload["id"]

    def call_service(self, domain: str, service: str, service_data: Optional[dict[str, Any]] = None):
        """Call Home Assistant service via WebSocket.

        Args:
            domain: Service domain (e.g., "light", "switch")
            service: Service name (e.g., "turn_on", "toggle")
            service_data: Service data (entity_id, etc.)

        Returns:
            Message ID for this call

        Example:
            ha_ws.call_service("light", "turn_on", {
                "entity_id": "light.bubs_bedroom_inside_light_switch_1",
                "brightness": 255
            })

        """
        payload = {
            "id": self._next_id(),
            "type": "call_service",
            "domain": domain,
            "service": service,
            "service_data": service_data or {},
        }
        self.send_json(payload)
        return payload["id"]

    def get_config(self):
        """Get Home Assistant configuration.

        Returns:
            Message ID for this request

        """
        payload = {
            "id": self._next_id(),
            "type": "get_config",
        }
        self.send_json(payload)
        return payload["id"]

    def get_states(self):
        """Get all states from Home Assistant.

        Returns:
            Message ID for this request

        """
        payload = {
            "id": self._next_id(),
            "type": "get_states",
        }
        self.send_json(payload)
        return payload["id"]

    def close(self) -> None:
        """Close WebSocket connection."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect_and_auth()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


__all__ = [
    "HomeAssistantWebSocket",
]
