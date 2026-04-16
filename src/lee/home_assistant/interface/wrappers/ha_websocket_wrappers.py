"""ha_websocket_wrappers.py
Version: 2025-12-22_1
Purpose: WebSocket interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the HA WebSocket router.
External modules MUST use gateway.execute_operation() instead of importing directly.
"""

from contextlib import nullcontext
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if WebSocket interface is available
# NOTE: We use gateway directly to avoid circular import with ha_websocket.py
_WEBSOCKET_AVAILABLE = True
_WEBSOCKET_IMPORT_ERROR = None


def establish_websocket_connection(ha_config: Optional[dict[str, Any]] = None,
                                   correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Establish WebSocket connection."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="establish_websocket_connection FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="establish_websocket_connection called")

    with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="establish_websocket_connection") as _:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                establish_websocket_connection as _establish_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['ha_config', 'correlation_id']}
            result = _establish_impl(ha_config=ha_config, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="establish_websocket_connection completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="establish_websocket_connection failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "ESTABLISH_WEBSOCKET_CONNECTION_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="establish_websocket_connection failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "ESTABLISH_WEBSOCKET_CONNECTION_FAILED",
            }


def close_websocket_connection(connection: Any,
                               correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Close WebSocket connection."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="close_websocket_connection FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="close_websocket_connection called")

    with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="close_websocket_connection") as _:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                close_websocket_connection as _close_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['connection', 'correlation_id']}
            result = _close_impl(connection=connection, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="close_websocket_connection completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="close_websocket_connection failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "CLOSE_WEBSOCKET_CONNECTION_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="close_websocket_connection failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "CLOSE_WEBSOCKET_CONNECTION_FAILED",
            }


def authenticate_websocket(connection: Any,
                          ha_config: Optional[dict[str, Any]] = None,
                          correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Authenticate WebSocket connection."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="authenticate_websocket FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="authenticate_websocket called")

    with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="authenticate_websocket") as _:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                authenticate_websocket as _auth_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['connection', 'ha_config', 'correlation_id']}
            result = _auth_impl(connection=connection, ha_config=ha_config, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="authenticate_websocket completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="authenticate_websocket failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "AUTHENTICATE_WEBSOCKET_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="authenticate_websocket failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "AUTHENTICATE_WEBSOCKET_FAILED",
            }


def send_websocket_message(connection: Any, message: dict[str, Any],
                          correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Send message through WebSocket connection."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="send_websocket_message FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="send_websocket_message called",
                     message_type=message.get("type"))

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="send_websocket_message")
    except (ImportError, TypeError):
        from contextlib import nullcontext
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                send_websocket_message as _send_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['connection', 'message', 'correlation_id']}
            result = _send_impl(connection=connection, message=message, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="send_websocket_message completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="send_websocket_message failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "SEND_WEBSOCKET_MESSAGE_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="send_websocket_message failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "SEND_WEBSOCKET_MESSAGE_FAILED",
            }


def receive_websocket_message(connection: Any, timeout: int = 10,
                             correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Receive message from WebSocket connection."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="receive_websocket_message FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="receive_websocket_message called",
                     timeout=timeout)

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="receive_websocket_message")
    except (ImportError, TypeError):
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                receive_websocket_message as _receive_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['connection', 'timeout', 'correlation_id']}
            result = _receive_impl(connection=connection, timeout=timeout, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="receive_websocket_message completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="receive_websocket_message failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "RECEIVE_WEBSOCKET_MESSAGE_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="receive_websocket_message failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "RECEIVE_WEBSOCKET_MESSAGE_FAILED",
            }


def websocket_request(connection: Any, message_type: str,
                     data: Optional[dict] = None, timeout: int = 10,
                     correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Send WebSocket request and wait for response."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="websocket_request FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="websocket_request called",
                     message_type=message_type)

    try:
        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="websocket_request")
    except (ImportError, TypeError):
        timing_ctx = nullcontext()

    with timing_ctx:
        try:
            from lee.home_assistant.ha_websocket.ha_websocket_core import (
                websocket_request as _request_impl,
            )
            core_kwargs = {k: v for k, v in kwargs.items() if k not in ['connection', 'message_type', 'data', 'timeout', 'correlation_id']}
            result = _request_impl(connection=connection, message_type=message_type, data=data, timeout=timeout, correlation_id=correlation_id, **core_kwargs)
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="websocket_request completed",
                            success=result.get("success", False))
            return result
        except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="websocket_request failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "WEBSOCKET_REQUEST_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="websocket_request failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "WEBSOCKET_REQUEST_FAILED",
            }


def get_websocket_status(correlation_id: str = None) -> dict[str, Any]:
    """Get WebSocket interface status."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("haws")

    if not _WEBSOCKET_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="HA_WEBSOCKET",
                        message="get_websocket_status FAILED - WebSocket interface unavailable",
                        error=_WEBSOCKET_IMPORT_ERROR)
        return {
            "success": False,
            "error": "WebSocket interface not available",
            "error_code": "INTERFACE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HA_WEBSOCKET",
                     message="get_websocket_status called")

    with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="get_websocket_status") as _:
        try:

            operations = [
                "establish_websocket_connection",
                "close_websocket_connection",
                "authenticate_websocket",
                "send_websocket_message",
                "receive_websocket_message",
                "websocket_request",
                "get_websocket_status",
            ]

            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="get_websocket_status completed",
                            enabled=True,
                            operation_count=len(operations))

            return {
                "success": True,
                "config": {"enabled": True},
                "operations": operations,
                "message": f"WebSocket interface operational with {len(operations)} operations",
            }
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="get_websocket_status failed",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_code": "GET_WEBSOCKET_STATUS_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="HA_WEBSOCKET",
                            message="get_websocket_status failed with unexpected error",
                            error_type=type(e).__name__, error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "GET_WEBSOCKET_STATUS_FAILED",
            }


# ===== EXPORTS =====

__all__ = [
    # Connection operations
    "establish_websocket_connection",
    "close_websocket_connection",
    "authenticate_websocket",
    # Message operations
    "send_websocket_message",
    "receive_websocket_message",
    "websocket_request",
    # Status/Configuration
    "get_websocket_status",
]

# EOF
