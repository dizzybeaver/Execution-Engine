"""ha_websocket_core.py - WebSocket Core Implementation (HA-SUGA)
Version: 3.0.0
Date: 2026-03-25
Description: Core WebSocket operations with connection pooling

Architecture: home_assistant.ha_websocket.ha_websocket_core → websocket_pool → network/ws_operations

Performance Optimization:
- Connection pooling reduces 100-200ms overhead to 10-20ms
- Thread-safe pool with configurable limits
- Automatic cleanup of stale connections

Note: HA-SUGA imports ws_operations directly (not via LEE Gateway) to avoid circular routing.
External code should use LEE Gateway WEBSOCKET interface for WebSocket operations.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
import threading
from typing import Any, Protocol, Optional

# Connection pooling for performance
try:
    from lee.home_assistant.ha_websocket.websocket_pool import (
        DEFAULT_CONNECTION_TIMEOUT,
        DEFAULT_IDLE_TIMEOUT,
        DEFAULT_POOL_SIZE,
        get_websocket_pool,
    )
    CONNECTION_POOLING_AVAILABLE = True
except ImportError:
    CONNECTION_POOLING_AVAILABLE = False

# Direct import from network module (HA-SUGA internal use)
try:
    from lee.network import ws_operations

    # SECURITY: Add SSRF protection for WebSocket connections
    from lee.network.ssrf_protect import validate_url
    from lee.network.ws_core import WebSocketClient
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    ws_operations = None
    WebSocketClient = None
    validate_url = None


# ===== PROTOCOL DEFINITIONS =====

class Closable(Protocol):
    """Protocol for objects that can be closed."""
    def close(self) -> None: ...


class Sendable(Protocol):
    """Protocol for objects that can send data."""
    def send(self, data: bytes | str) -> None: ...


class TextSendable(Protocol):
    """Protocol for objects that can send text data."""
    def send_text(self, text: str) -> None: ...


class Recvable(Protocol):
    """Protocol for objects that can receive data."""
    def recv(self, bufsize: Optional[int] = None, timeout: Optional[int] = None) -> str | bytes: ...


# ===== CONFIGURATION =====

HA_WEBSOCKET_ENABLED = WEBSOCKETS_AVAILABLE
HA_WEBSOCKET_TIMEOUT = int(os.environ.get("HOME_ASSISTANT_WEBSOCKET_TIMEOUT", str(DEFAULT_CONNECTION_TIMEOUT)))

# Connection pooling settings
USE_CONNECTION_POOL = os.environ.get("USE_CONNECTION_POOL", "true").lower() == "true"
POOL_SIZE = int(os.environ.get("WEBSOCKET_POOL_SIZE", str(DEFAULT_POOL_SIZE)))
IDLE_TIMEOUT = int(os.environ.get("WEBSOCKET_IDLE_TIMEOUT", str(DEFAULT_IDLE_TIMEOUT)))


# ===== CONNECTION MANAGEMENT =====

class GlobalWebSocketManager:
    """Thread-safe singleton for global WebSocket connection."""

    _websocket: Optional[WebSocketClient] = None
    _url: Optional[str] = None
    _token: Optional[str] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_connection(cls) -> tuple[Optional[WebSocketClient], Optional[str], Optional[str]]:
        """Get current connection details."""
        with cls._lock:
            return cls._websocket, cls._url, cls._token

    @classmethod
    def set_connection(cls, websocket: Optional[WebSocketClient],
                      url: Optional[str] = None, token: Optional[str] = None):
        """Set connection details."""
        with cls._lock:
            cls._websocket = websocket
            cls._url = url
            cls._token = token

    @classmethod
    def clear(cls):
        """Clear connection."""
        with cls._lock:
            cls._websocket = None
            cls._url = None
            cls._token = None


# Global WebSocket connection state (synchronized with thread-safe singleton)
# These globals are used throughout the module for direct access performance
_global_websocket: Optional[WebSocketClient] = None
_global_url: Optional[str] = None
_global_token: Optional[str] = None
_global_websocket_manager = GlobalWebSocketManager()


def establish_websocket_connection(
    ha_config: Optional[dict[str, Any]] = None,
    **kwargs
) -> dict[str, Any]:
    """Establish WebSocket connection to Home Assistant using connection pool.

    Performance:
    - With pooling: 10-20ms (connection reuse)
    - Without pooling: 100-200ms (new connection)
    - Improvement: 80-90% latency reduction

    Args:
        ha_config: Configuration dict with url and token
        **kwargs: Additional parameters (timeout, correlation_id, etc.)

    Returns:
        Dict with success status and connection details

    """
    global _global_websocket, _global_url, _global_token

    if not WEBSOCKETS_AVAILABLE:
        return {
            "success": False,
            "error": "WebSocket operations not available",
            "error_code": "WEBSOCKETS_UNAVAILABLE",
        }

    try:
        # Extract configuration (using thread-safe singleton)
        if ha_config:
            url = ha_config.get("url")
            token = ha_config.get("token")
            _global_websocket_manager.set_connection(None, url, token)

            # Update legacy globals for backwards compatibility
            _global_url = url
            _global_token = token

        if not _global_url or not _global_token:
            return {
                "success": False,
                "error": "Missing url or token in configuration",
                "error_code": "INVALID_CONFIG",
            }

        # SECURITY: Validate URL for SSRF attacks before connecting
        if validate_url:
            try:
                # Build allowlist from HOME_ASSISTANT_URL environment variable
                # Same logic as http_client.py for consistency
                allowlist = []
                import os
                from urllib.parse import urlparse

                env_url = os.getenv("HOME_ASSISTANT_URL")
                if env_url:
                    # Allow the exact URL from .env file
                    allowlist.append(env_url)
                    # Also allow variations (different ports, protocols)
                    parsed = urlparse(env_url)
                    if parsed.hostname:
                        # Allow http/https with same hostname
                        allowlist.append(f"http://{parsed.hostname}:{parsed.port}")
                        allowlist.append(f"https://{parsed.hostname}:{parsed.port}")
                        # Allow without port
                        allowlist.append(f"http://{parsed.hostname}")
                        allowlist.append(f"https://{parsed.hostname}")
                        # Allow with /api/ path (used by base_url)
                        allowlist.append(f"http://{parsed.hostname}:{parsed.port}/api/")
                        allowlist.append(f"https://{parsed.hostname}:{parsed.port}/api/")
                        # Allow with /api path (without trailing slash)
                        allowlist.append(f"http://{parsed.hostname}:{parsed.port}/api")
                        allowlist.append(f"https://{parsed.hostname}:{parsed.port}/api")

                is_safe = validate_url(_global_url, allowlist=allowlist)
                if not is_safe:
                    return {
                        "success": False,
                        "error": f"URL failed SSRF validation: {_global_url}",
                        "error_code": "SSRF_VALIDATION_FAILED",
                    }
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"URL validation error: {str(e)}",
                    "error_code": "SSRF_VALIDATION_ERROR",
                }

        # Use connection pool if available and enabled
        if CONNECTION_POOLING_AVAILABLE and USE_CONNECTION_POOL:
            pool = get_websocket_pool(
                pool_size=POOL_SIZE,
                idle_timeout=IDLE_TIMEOUT,
                connection_timeout=HA_WEBSOCKET_TIMEOUT
            )

            # Acquire connection from pool
            result = pool.acquire(_global_url, **kwargs)

            if result.get("success"):
                _global_websocket = result.get("connection")
                return {
                    "success": True,
                    "connection": _global_websocket,
                    "url": _global_url,
                    "from_pool": result.get("from_pool", False),
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Connection failed"),
                    "error_code": result.get("error_code", "CONNECTION_FAILED"),
                }
        else:
            # Fallback to non-pooled connection
            timeout = kwargs.get("timeout", HA_WEBSOCKET_TIMEOUT)

            # Call ws_operations directly (HA-SUGA internal use)
            # External code should use LEE Gateway WEBSOCKET interface instead
            result = ws_operations.websocket_connect_implementation(
                url=_global_url,
                timeout=timeout
            )

            if result.get("success"):
                _global_websocket = result.get("connection")
                return {
                    "success": True,
                    "connection": _global_websocket,
                    "url": _global_url,
                    "from_pool": False,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "error_code": result.get("error_type", "CONNECTION_FAILED"),
                }

    except (ConnectionError, TimeoutError, OSError) as e:
        # Expected WebSocket connection errors
        error_msg = str(e) if str(e) else repr(e)
        error_type = type(e).__name__
        return {
            "success": False,
            "error": f"{error_type}: {error_msg}",
            "error_code": "CONNECTION_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        error_msg = str(e) if str(e) else repr(e)
        error_type = type(e).__name__
        return {
            "success": False,
            "error": f"{error_type}: {error_msg}",
            "error_code": "CONNECTION_FAILED",
        }


def close_websocket_connection(connection: Any = None, **kwargs) -> dict[str, Any]:
    """Close WebSocket connection and return to pool if applicable.

    Args:
        connection: WebSocket connection to close (uses global if None)
        **kwargs: Additional parameters

    Returns:
        Dict with success status

    """
    global _global_websocket

    try:
        ws = connection or _global_websocket
        if not ws:
            return {"success": True}

        # Use connection pool if available
        if CONNECTION_POOLING_AVAILABLE and USE_CONNECTION_POOL:
            pool = get_websocket_pool()

            # Get URL for pool release
            url = kwargs.get("url", _global_url)

            # Release back to pool or close
            if kwargs.get("close_pooled", False):
                # Force close the connection
                return pool.close(url, ws)
            else:
                # Release back to pool for reuse
                pool.release(url, ws)
                if connection is None:
                    _global_websocket = None
                return {"success": True}
        else:
            # Non-pooled close
            try:
                # Call ws_operations directly (HA-SUGA internal use)
                ws_operations.websocket_close_implementation(connection=ws)
            except AttributeError:
                # Connection doesn't support close - continue cleanup
                pass

            if connection is None:
                _global_websocket = None

            return {"success": True}

    except (ConnectionError, OSError) as e:
        # Expected connection cleanup errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "CLOSE_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "CLOSE_FAILED",
        }


def authenticate_websocket(connection: Any, ha_config: Optional[dict[str, Any]] = None, **kwargs) -> dict[str, Any]:
    """Authenticate WebSocket connection with Home Assistant.

    Args:
        connection: WebSocket connection
        ha_config: Configuration dict with token
        **kwargs: Additional parameters

    Returns:
        Dict with authentication result

    """
    global _global_token

    try:
        if not connection:
            return {
                "success": False,
                "error": "No connection provided",
                "error_code": "NO_CONNECTION",
            }

        # Get token from config or global
        token = ha_config.get("token") if ha_config else _global_token
        if not token:
            return {
                "success": False,
                "error": "No token available",
                "error_code": "NO_TOKEN",
            }

        # Send authentication message
        auth_message = {
            "type": "auth",
            "access_token": token
        }

        # Send using LEE WebSocket client
        try:
            connection.send(json.dumps(auth_message))
        except AttributeError:
            return {
                "success": False,
                "error": "Connection does not support send",
                "error_code": "UNSUPPORTED_OPERATION",
            }

        # Wait for authentication response
        try:
            response = connection.recv(timeout=5)  # 5 second timeout for auth response
            try:
                response_data = json.loads(response)
            except (json.JSONDecodeError, ValueError) as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {str(e)}",
                    "error_code": "INVALID_JSON",
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse response: {str(e)}",
                    "error_code": "PARSE_ERROR",
                }

            if response_data.get("type") == "auth_ok":
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Authentication failed"),
                    "error_code": "AUTH_FAILED",
                }

        except AttributeError:
            return {
                "success": False,
                "error": "Connection does not support recv",
                "error_code": "UNSUPPORTED_OPERATION",
            }

    except (ConnectionError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as e:
        # Expected authentication errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "AUTH_ERROR",
        }
    except Exception as e:
        # Unexpected errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "AUTH_ERROR",
        }


def send_websocket_message(connection: Any, message: dict[str, Any], **kwargs) -> dict[str, Any]:
    """Send message through WebSocket connection.

    Args:
        connection: WebSocket connection
        message: Message dict to send
        **kwargs: Additional parameters

    Returns:
        Dict with send result

    """
    try:
        if not connection:
            return {
                "success": False,
                "error": "No connection provided",
                "error_code": "NO_CONNECTION",
            }

        # Try to use send_text first, fall back to send if not available
        try:
            connection.send_text(json.dumps(message))
        except AttributeError:
            # Connection doesn't support send_text, try send
            try:
                connection.send(json.dumps(message))
            except AttributeError:
                return {
                    "success": False,
                    "error": "Connection does not support send_text or send",
                    "error_code": "UNSUPPORTED_OPERATION",
                }

        return {"success": True, "id": message.get("id")}

    except (ConnectionError, TimeoutError, OSError, ValueError) as e:
        # Expected send errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEND_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEND_FAILED",
        }


def receive_websocket_message(connection: Any, timeout: int = 10, **kwargs) -> dict[str, Any]:
    """Receive message from WebSocket connection.

    Args:
        connection: WebSocket connection
        timeout: Receive timeout in seconds
        **kwargs: Additional parameters

    Returns:
        Dict with receive result and message data

    """
    try:
        if not connection:
            return {
                "success": False,
                "error": "No connection provided",
                "error_code": "NO_CONNECTION",
            }

        # Try to receive message
        try:
            message = connection.recv(timeout=timeout)
        except AttributeError:
            return {
                "success": False,
                "error": "Connection does not support recv",
                "error_code": "UNSUPPORTED_OPERATION",
            }
        try:
            message_data = json.loads(message)
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "success": False,
                "error": f"Invalid JSON message: {str(e)}",
                "error_code": "INVALID_JSON",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse message: {str(e)}",
                "error_code": "PARSE_ERROR",
            }

        return {
            "success": True,
            "message": message_data,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        # Expected receive errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "RECEIVE_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "RECEIVE_FAILED",
        }


def websocket_request(connection: Any, message_type: str, data: Optional[dict] = None, timeout: int = 10, **kwargs) -> dict[str, Any]:
    """Send WebSocket request and wait for response.

    Args:
        connection: WebSocket connection
        message_type: Type of message to send
        data: Optional data payload
        timeout: Request timeout in seconds
        **kwargs: Additional parameters

    Returns:
        Dict with request result

    """
    try:
        # Send message
        message = {"type": message_type, "id": kwargs.get("id", 1)}
        if data:
            message.update(data)

        send_result = send_websocket_message(connection, message)
        if not send_result.get("success"):
            return send_result

        # Wait for response
        receive_result = receive_websocket_message(connection, timeout=timeout)
        if not receive_result.get("success"):
            return receive_result

        return {
            "success": True,
            "response": receive_result.get("message"),
        }

    except (ConnectionError, TimeoutError, OSError, ValueError) as e:
        # Expected request errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        return {
            "success": False,
            "error": str(e),
            "error_code": "REQUEST_FAILED",
        }


__all__ = [
    "HA_WEBSOCKET_ENABLED",
    "HA_WEBSOCKET_TIMEOUT",
    "WEBSOCKETS_AVAILABLE",
    "CONNECTION_POOLING_AVAILABLE",
    "USE_CONNECTION_POOL",
    "POOL_SIZE",
    "IDLE_TIMEOUT",
    "establish_websocket_connection",
    "close_websocket_connection",
    "authenticate_websocket",
    "send_websocket_message",
    "receive_websocket_message",
    "websocket_request",
]
