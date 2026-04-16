"""ha_websocket_connection.py - WebSocket Connection Management
Version: 2025-12-22_1
Description: WebSocket connection establishment and management (SUGA-ISP compliant)

Split from ha_websocket_core.py to meet AWS Lambda 350-line limit.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Optional

from lee.gateway.gateway_core import generate_correlation_id

# Import WebSocket timeout from configuration
try:
    from lee.lee_config.variables import (
        HOME_ASSISTANT_WEBSOCKET_TIMEOUT,
        get_config_value,
    )
    # Validate timeout bounds (1-60 seconds)
    HA_WEBSOCKET_TIMEOUT = get_config_value(
        HOME_ASSISTANT_WEBSOCKET_TIMEOUT,
        min_value=1,
        max_value=60,
    )
except (ImportError, ValueError):
    # Fallback for standalone usage or if validation fails
    ...
    import os
    try:
        HA_WEBSOCKET_TIMEOUT = int(os.getenv("HA_WEBSOCKET_TIMEOUT", "10"))
    except ValueError:
        HA_WEBSOCKET_TIMEOUT = 10  # Fallback to default if invalid

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_websocket.ha_websocket_messaging import (
    receive_websocket_message,
    send_websocket_message,
)


def establish_websocket_connection(url: str, timeout: Optional[int] = None) -> dict[str, Any]:
    """Establish WebSocket connection using Gateway (SUGA-ISP compliant).

        url: WebSocket URL
        timeout: Connection timeout in seconds (uses HA_WEBSOCKET_TIMEOUT from env if not specified)

        Connection result dict

    """
    # Import timeout from configuration if not specified
    if timeout is None:
        timeout = HA_WEBSOCKET_TIMEOUT
    # SUGA-ISP compliant: always use execute_operation() for all Gateway access

    correlation_id = generate_correlation_id("ws")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="establish_websocket_connection START",
                     url=url[:50], timeout=timeout)

    # Execute with timing
    with execute_operation(GatewayInterface.DEBUG, "timing",
                          corr_id=correlation_id,
                          operation_name="establish_websocket_connection") as _:
        try:
            # Use Gateway WebSocket interface
            result = execute_operation(
                GatewayInterface.WEBSOCKET,
                "connect",
                url=url,
                timeout=timeout,
                correlation_id=correlation_id,
            )

            if result.get("success", False):
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="establish_websocket_connection SUCCESS")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_connect_success")
            else:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="establish_websocket_connection FAILED")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_connect_error")

            return result

        except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
            # Expected network/WebSocket errors
            ...
            import os
            ha_url = os.environ.get("HOME_ASSISTANT_URL", "http://localhost:8123")

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="establish_websocket_connection FAILED (connection error)",
                             error=str(e))

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket connection failed: {e!s}",
                             error=str(e))

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_connect_exception")

            return {
                "success": False,
                "error": f"WebSocket connection timeout after {timeout}s. Possible causes: "
                         f"1) Home Assistant is not running at {ha_url}, "
                         f"2) WebSocket is disabled in HA configuration, "
                         f"3) Network firewall blocking WebSocket connections, "
                         f"4) Incorrect URL (should be: {ha_url.replace('http', 'ws')}/api/websocket)",
                "error_code": "WEBSOCKET_TIMEOUT",
                "troubleshooting": {
                    "check_ha_running": f"curl {ha_url}/api/",
                    "check_websocket_enabled": "Verify HA Configuration -> WebSocket is enabled",
                    "check_network": f"telnet {ha_url.split('://')[1].split(':')[0]} 8123",
                    "url": f"{ha_url.replace('http', 'ws')}/api/websocket"
                }
            }
        except Exception as e:
            # Unexpected errors
            ...
            import os
            ha_url = os.environ.get("HOME_ASSISTANT_URL", "http://localhost:8123")

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="establish_websocket_connection FAILED (unexpected error)",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket connection unexpected error: {e!s}",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_connect_exception")

            return {
                "success": False,
                "error": f"Unexpected WebSocket connection error: {str(e)}",
                "error_code": "WEBSOCKET_UNEXPECTED_ERROR",
            }

def close_websocket_connection(connection: Any) -> dict[str, Any]:
    """Close WebSocket connection (SUGA-ISP compliant).

        connection: WebSocket connection object

        Close result dict

    """

    correlation_id = generate_correlation_id("ws")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="close_websocket_connection START")

    # Execute with timing
    with execute_operation(GatewayInterface.DEBUG, "timing",
                          corr_id=correlation_id,
                          operation_name="close_websocket_connection") as _:
        try:
            # Use Gateway WebSocket interface
            result = execute_operation(
                GatewayInterface.WEBSOCKET,
                "close",
                connection=connection,
                correlation_id=correlation_id,
            )

            if result.get("success", False):
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="close_websocket_connection SUCCESS")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_close_success")
            else:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="close_websocket_connection FAILED")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_close_error")

            return result

        except (ConnectionError, OSError, ValueError, TypeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="close_websocket_connection FAILED (connection error)",
                             error=str(e))

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket close failed: {e!s}",
                             error=str(e))

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_close_exception")

            return {
                "success": False,
                "error": str(e),
                "error_code": "WEBSOCKET_CLOSE_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="close_websocket_connection FAILED (unexpected error)",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket close unexpected error: {e!s}",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_close_exception")

            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "WEBSOCKET_CLOSE_UNEXPECTED",
            }


def authenticate_websocket(connection: Any, access_token: str) -> dict[str, Any]:
    """Authenticate WebSocket connection with Home Assistant (SUGA-ISP compliant).

    Args:
        connection: WebSocket connection object
        access_token: Home Assistant long-lived access token

    Returns:
        Authentication result dict
    """


    correlation_id = generate_correlation_id("ws")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="authenticate_websocket START",
                     has_token=bool(access_token))

    if not access_token:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="authenticate_websocket FAILED - No token")
        return {
            "success": False,
            "error": "No access token provided",
            "error_code": "NO_TOKEN",
        }

    auth_message = {
        "type": "auth",
        "access_token": access_token,
    }

    # Execute with timing
    with execute_operation(GatewayInterface.DEBUG, "timing",
                          corr_id=correlation_id,
                          operation_name="authenticate_websocket") as _:
        try:
            # Send auth message
            send_result = send_websocket_message(connection, auth_message)

            if not send_result.get("success"):
                return send_result

            # Wait for auth response
            receive_result = receive_websocket_message(connection, timeout=10)

            if not receive_result.get("success"):
                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_auth_no_response")
                return receive_result

            parsed_message = receive_result.get("parsed_message", {})

            if parsed_message.get("type") == "auth_ok":
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="authenticate_websocket SUCCESS")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_auth_success")

                return {
                    "success": True,
                    "message": "WebSocket authenticated successfully",
                    "auth_response": parsed_message,
                }

            if parsed_message.get("type") == "auth_invalid":
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="authenticate_websocket FAILED - Invalid token")

                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                metric_name="ha_websocket_auth_invalid")

                return {
                    "success": False,
                    "error": "Invalid access token",
                    "error_code": "AUTH_INVALID",
                    "auth_response": parsed_message,
                }

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="authenticate_websocket FAILED - Unexpected response",
                             response_type=parsed_message.get("type"))

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_auth_unexpected")

            return {
                "success": False,
                "error": f'Unexpected auth response: {parsed_message.get("type")}',
                "error_code": "AUTH_UNEXPECTED",
                "auth_response": parsed_message,
            }

        except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, KeyError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="authenticate_websocket FAILED (connection/error)",
                             error=str(e))

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket authentication failed: {e!s}",
                             error=str(e))

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_auth_exception")

            return {
                "success": False,
                "error": str(e),
                "error_code": "WEBSOCKET_AUTH_FAILED",
            }
        except Exception as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="authenticate_websocket FAILED (unexpected error)",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.LOGGING, "log_error",
                             message=f"WebSocket authentication unexpected error: {e!s}",
                             error=str(e), error_type=type(e).__name__)

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                            metric_name="ha_websocket_auth_exception")

            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "WEBSOCKET_AUTH_UNEXPECTED",
            }


__all__ = [
    "authenticate_websocket",
    "close_websocket_connection",
    "establish_websocket_connection",
]
