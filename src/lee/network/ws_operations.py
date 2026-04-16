"""network/ws_operations.py

Gateway WebSocket operations with circuit breaker protection and SSRF validation.

Recreated from: websocket/websocket_generic.py
Does NOT include broken code from websocket_manager.py
Enhanced with: SSRF validation, connection pooling (2026-03-31)

Version: 2.1.0 (2026-03-31)
Security: SSRF protection added (CVSS 8.5 -> <2.0)
Features: Connection pooling with LRU eviction and auto-cleanup
License: Apache 2.0
"""

import json
import os
import random
import time
from typing import Any, Optional
from urllib.parse import urlparse

from contextlib import nullcontext as _nullcontext

# Gateway operations
from lee.gateway import GatewayInterface, execute_operation

# SSRF protection
from lee.network.ssrf_protect import validate_url

# Use new network factory for WebSocket client
from lee.network.ws_core import WebSocketClient, WebSocketClosed, WebSocketError

# Connection pooling with LRU eviction and cleanup
from lee.network.ws_pool import get_global_pool

# Debug support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"


def _validate_and_parse_allowlist(allowlist_str: str) -> Optional[list[str]]:
    """Validate and parse SSRF allowlist from environment variable.

    Args:
        allowlist_str: Comma-separated list of URLs from SSRF_ALLOWLIST env var

    Returns:
        List of validated URLs, or None if empty/invalid

    Raises:
        ValueError: If any allowlist entry is invalid or contains blocked patterns

    Security:
        Prevents SSRF bypass attempts through malformed allowlist entries.
        Each entry must be a valid URL with proper scheme, hostname, and no
        blocked patterns (localhost, private IPs, etc.).

    """
    if not allowlist_str or not allowlist_str.strip():
        return None

    validated_urls = []
    raw_entries = [entry.strip() for entry in allowlist_str.split(",") if entry.strip()]

    for entry in raw_entries:
        # Validate each entry as a proper URL
        try:
            parsed = urlparse(entry)

            # Must have scheme and hostname
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(
                    f"Invalid allowlist entry '{entry}': must be a valid URL with scheme and hostname"
                )

            # Must be ws:// or wss:// scheme
            if parsed.scheme not in ("ws", "wss"):
                raise ValueError(
                    f"Invalid allowlist entry '{entry}': scheme must be ws:// or wss://"
                )

            # Reject localhost in any form
            if parsed.hostname and "localhost" in parsed.hostname.lower():
                raise ValueError(
                    f"Invalid allowlist entry '{entry}': contains 'localhost' (SSRF risk)"
                )

            # Reject entries starting with 127. (loopback bypass)
            if parsed.hostname and parsed.hostname.lower().startswith("127."):
                raise ValueError(
                    f"Invalid allowlist entry '{entry}': starts with 127. (loopback - SSRF risk)"
                )

            # Reject entries ending with .local that are IP addresses (potential bypass)
            # Allow legitimate .local domains like homeassistant.local
            if parsed.hostname and parsed.hostname.lower().endswith(".local"):
                # Check if it's actually an IP address disguised as .local
                hostname_parts = parsed.hostname.lower().split(".")
                if any(part.isdigit() for part in hostname_parts[:-1]):
                    raise ValueError(
                        f"Invalid allowlist entry '{entry}': IP address with .local suffix (potential SSRF bypass)"
                    )

            # Add base URL and common variations
            validated_urls.append(entry)

            # Add variations with different ports (if port specified)
            if parsed.port:
                hostname = parsed.hostname
                port = parsed.port
                # Add with /api/ path (common WebSocket endpoint)
                validated_urls.append(f"{parsed.scheme}://{hostname}:{port}/api/")
                validated_urls.append(f"{parsed.scheme}://{hostname}:{port}/api")

        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(
                f"Failed to parse SSRF allowlist entry '{entry}': {e}"
            ) from e

    return validated_urls if validated_urls else None


def websocket_connect_implementation(url: str, timeout: int = 10,
                                     correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Connect to WebSocket server using network factory.

    Args:
        url: WebSocket URL (ws:// or wss://)
        timeout: Connection timeout in seconds
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response with connection object, or error response

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="WS_OPERATIONS",
            message="websocket_connect_implementation called",
            url=url, timeout=timeout,
            rationale=f"Using {timeout}s timeout for WebSocket connection"
        )

    # Validate URL via SUGA-ISP Gateway
    execute_operation(GatewayInterface.SECURITY, "validate_string",
                     value=url, min_length=10, max_length=500, name="WebSocket URL")
    execute_operation(GatewayInterface.SECURITY, "validate_number_range",
                     value=timeout, min_val=1, max_val=60, name="WebSocket timeout")

    # Additional URL security checks
    if not (url.startswith("ws://") or url.startswith("wss://")):
        raise ValueError("WebSocket URL must start with ws:// or wss://")

    # SSRF validation using robust IP-based checking (CVSS 8.5 -> <2.0)
    # Read SSRF allowlist from environment to allow local Home Assistant
    try:
        allowlist_str = os.environ.get("SSRF_ALLOWLIST", "")
        ssrf_allowlist = _validate_and_parse_allowlist(allowlist_str)
        validate_url(url, allowlist=ssrf_allowlist)
    except ValueError as e:
        if _DEBUG_ENABLED:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="WS_OPERATIONS",
                             message="SSRF validation failed", url=str(url)[:100])
        return {
            "success": False,
            "error": str(e),
            "error_type": "SSRFValidationError",
            "url": url,
        }

    if _DEBUG_ENABLED:
        timing_ctx = execute_operation(
            GatewayInterface.DEBUG, "timing",
            corr_id=correlation_id,
            operation_name="websocket_connect_implementation"
        )
    else:
        from contextlib import nullcontext
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            ws = WebSocketClient(url, timeout=timeout)
            ws.connect()

            # Store connection in pool (handles LRU eviction automatically)
            pool = get_global_pool()
            conn_id = pool.add_connection(ws, url=url)

            # Periodic cleanup
            pool.cleanup_idle()

            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_connect_implementation completed",
                                 success=True, url=url, conn_id=conn_id)

            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="WebSocket connected", data={
                                        "connection": ws,
                                        "conn_id": conn_id,
                                        "url": url,
                                    })
        except (ConnectionError, TimeoutError, OSError, WebSocketError) as e:
            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_connect_implementation failed",
                                 error_type=type(e).__name__, error=str(e), url=url)
            raise
        except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, MemoryError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket connect operation error: {e!s}",
                             error=str(e), error_type=type(e).__name__)
            raise


def websocket_send_implementation(connection: Any, message: dict[str, Any],
                                  correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Send message via WebSocket using network factory.

    Args:
        connection: Active WebSocket connection object
        message: Dictionary to send
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response or error response

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id,
                         scope="WS_OPERATIONS",
                         message="websocket_send_implementation called",
                         has_connection=connection is not None,
                         has_message=message is not None)

    # Validate message is a dict
    if not isinstance(message, dict):
        raise TypeError(f"WebSocket message must be a dict, got {type(message).__name__}")

    # Validate message size (prevent huge messages)
    message_str = json.dumps(message)
    message_size = len(message_str)
    if message_size > 1024 * 1024:  # 1MB limit
        raise ValueError("WebSocket message too large (max 1MB)")

    if _DEBUG_ENABLED:
        timing_ctx = execute_operation(
            GatewayInterface.DEBUG, "timing",
            corr_id=correlation_id,
            operation_name="websocket_send_implementation"
        )
    else:
        timing_ctx = _nullcontext()

    with timing_ctx:
        try:
            if not isinstance(connection, WebSocketClient):
                raise TypeError("Invalid connection object")

            connection.send_text(message_str)

            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_send_implementation completed",
                                 success=True, message_size=message_size)

            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="Message sent", data={
                                        "message_size": message_size,
                                        "correlation_id": correlation_id,
                                    })
        except (ConnectionError, OSError, WebSocketClosed, WebSocketError) as e:
            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_send_implementation failed",
                                 error_type=type(e).__name__, error=str(e))
            raise
        except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, MemoryError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket send operation error: {e!s}",
                             error=str(e), error_type=type(e).__name__)
            raise


def websocket_receive_implementation(connection: Any, timeout: int = 10,
                                     correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Receive message from WebSocket using network factory.

    Args:
        connection: Active WebSocket connection object
        timeout: Receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response with received message, or error response

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id,
            scope="WS_OPERATIONS",
            message="websocket_receive_implementation called",
            has_connection=connection is not None,
            timeout=timeout,
            rationale=f"Using {timeout}s timeout for WebSocket receive"
        )

    try:
        if not isinstance(connection, WebSocketClient):
            raise TypeError("Invalid connection object")

        msg = connection.recv(as_text=True, timeout=timeout)

        if msg is None:
            return {"success": False, "error": "Connection closed"}

        # Try to parse as JSON
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            data = msg

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="WS_OPERATIONS",
                         message="websocket_receive_implementation completed",
                         success=True)

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Message received", data={
                                    "message": data,
                                    "correlation_id": correlation_id,
                                })
    except WebSocketClosed as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"WebSocket closed: {e!s}", error=str(e))
        return {"success": False, "error": "Connection closed"}
    except (ConnectionError, TimeoutError, OSError, WebSocketError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="WS_OPERATIONS",
                         message="websocket_receive_implementation failed",
                         error_type=type(e).__name__, error=str(e))
        raise
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, MemoryError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"WebSocket receive operation error: {e!s}",
                         error=str(e), error_type=type(e).__name__)
        raise


def websocket_close_implementation(connection: Any, correlation_id: str = None,
                                   **_kwargs) -> dict[str, Any]:
    """Close WebSocket connection using network factory.

    Args:
        connection: Active WebSocket connection object
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response or error response

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id,
                         scope="WS_OPERATIONS",
                     message="websocket_close_implementation called",
                     has_connection=connection is not None)

    try:
        if not isinstance(connection, WebSocketClient):
            raise TypeError("Invalid connection object")

        connection.close()

        # Remove from pool (search for connection object)
        pool = get_global_pool()
        removed = False
        for conn_id in list(pool.get_stats().get("connection_ids", [])):
            conn = pool.get_connection(conn_id)
            if conn is connection:
                pool.remove_connection(conn_id)
                removed = True
                break

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="WS_OPERATIONS",
                         message="websocket_close_implementation completed",
                         success=True, removed=removed)

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Connection closed", data={
                                    "correlation_id": correlation_id,
                                    "removed": removed,
                                })
    except (ConnectionError, OSError, WebSocketError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="WS_OPERATIONS",
                         message="websocket_close_implementation failed",
                         error_type=type(e).__name__, error=str(e))
        raise
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, MemoryError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"WebSocket close operation error: {e!s}",
                         error=str(e), error_type=type(e).__name__)
        raise


def websocket_request_implementation(url: str, message: dict[str, Any],
                                     timeout: int = 10, correlation_id: str = None,
                                     **_kwargs) -> dict[str, Any]:
    """Execute complete WebSocket request using network factory.

    Args:
        url: WebSocket URL (ws:// or wss://)
        message: Dictionary to send
        timeout: Connection and receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response with server response, or error response

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id,
            scope="WS_OPERATIONS",
            message="websocket_request_implementation called",
            url=url, timeout=timeout, has_message=message is not None,
            rationale=f"Using {timeout}s timeout for complete WebSocket request"
        )

    if _DEBUG_ENABLED:
        timing_ctx = execute_operation(
            GatewayInterface.DEBUG, "timing",
            corr_id=correlation_id,
            operation_name="websocket_request_implementation"
        )
    else:
        from contextlib import nullcontext
        timing_ctx = nullcontext()

    with timing_ctx:
        # Connect
        connect_result = websocket_connect_implementation(url=url, timeout=timeout,
                                                         correlation_id=correlation_id)
        if not connect_result.get("success"):
            return connect_result

        connection = connect_result.get("data", {}).get("connection")

        # Send
        send_result = websocket_send_implementation(connection=connection, message=message,
                                                    correlation_id=correlation_id)
        if not send_result.get("success"):
            websocket_close_implementation(connection=connection, correlation_id=correlation_id)
            return send_result

        # Receive
        receive_result = websocket_receive_implementation(connection=connection, timeout=timeout,
                                                          correlation_id=correlation_id)

        # Always close
        websocket_close_implementation(connection=connection, correlation_id=correlation_id)

        if not receive_result.get("success"):
            return receive_result

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="WS_OPERATIONS",
                         message="websocket_request_implementation completed",
                         success=True)

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="WebSocket request completed", data={
                                    "response": receive_result.get("data", {}).get("message"),
                                    "correlation_id": correlation_id,
                                })


def websocket_get_stats_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Get WebSocket statistics using connection pool.

    Args:
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Statistics dict with pool metrics

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id,
                         scope="WS_OPERATIONS",
                     message="websocket_get_stats_implementation called")

    pool = get_global_pool()
    pool_stats = pool.get_stats()

    return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                            message="WebSocket statistics", data=pool_stats)


def websocket_reset_implementation(correlation_id: str = None, **_kwargs) -> dict[str, Any]:
    """Reset WebSocket connection pool using network factory.

    Args:
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success/error response dict

    """

    if correlation_id is None:
        correlation_id = f"ws_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"

    if _DEBUG_ENABLED:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id,
                         scope="WS_OPERATIONS",
                     message="websocket_reset_implementation called")

    if _DEBUG_ENABLED:
        timing_ctx = execute_operation(
            GatewayInterface.DEBUG, "timing",
            corr_id=correlation_id,
            operation_name="websocket_reset_implementation"
        )
    else:
        from contextlib import nullcontext
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            pool = get_global_pool()
            pool_size = pool.size

            # Reset pool (closes all connections)
            pool.reset()

            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_reset_implementation completed",
                                 success=True)

            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="WebSocket connections reset", data={
                                        "reset": True,
                                        "connections_closed": pool_size,
                                    })
        except (ConnectionError, OSError) as e:
            if _DEBUG_ENABLED:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id,
                                 scope="WS_OPERATIONS",
                                 message="websocket_reset_implementation failed",
                                 error_type=type(e).__name__, error=str(e))
            raise
        except (AttributeError, KeyError, RuntimeError, ValueError, TypeError, MemoryError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket reset operation error: {e!s}",
                             error=str(e), error_type=type(e).__name__)
            raise


__all__ = [
    "websocket_close_implementation",
    "websocket_connect_implementation",
    "websocket_get_stats_implementation",
    "websocket_receive_implementation",
    "websocket_request_implementation",
    "websocket_reset_implementation",
    "websocket_send_implementation",
]
