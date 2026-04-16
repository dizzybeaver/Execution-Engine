"""ha_websocket_messaging.py - WebSocket Message Operations
Version: 3.0.1
Description: WebSocket message sending and receiving operations

Split from ha_websocket_core.py to meet AWS Lambda 350-line limit.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import time
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def send_websocket_message(connection: Any, message: dict[str, Any]) -> dict[str, Any]:


    """Send message through WebSocket connection."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_websocket_message START", message_type=message.get("type"))

        message_str = json.dumps(message)

        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="send_websocket_message")

        with timing_ctx:
            result = execute_operation(
                GatewayInterface.WEBSOCKET,
                "send",
                connection=connection,
                message=message_str,
                correlation_id=correlation_id,
            )

        if result.get("success", False):
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="send_websocket_message SUCCESS")

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_send_success")
            execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                             operation_name="ha_websocket_send_duration_ms",
                             duration_ms=result.get("duration_ms", 0))
        else:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="send_websocket_message FAILED")

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_send_error")
            execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                             operation_name="ha_websocket_send_error_duration_ms",
                             duration_ms=result.get("duration_ms", 0))

        return result

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        # Expected send errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_websocket_message FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket send failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_send_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_SEND_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_websocket_message FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket send failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_send_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_SEND_FAILED",
        }


def receive_websocket_message(connection: Any, timeout: int = 10) -> dict[str, Any]:
    """Receive message from WebSocket connection."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="receive_websocket_message START", timeout=timeout)

        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="receive_websocket_message")

        with timing_ctx:
            result = execute_operation(
                GatewayInterface.WEBSOCKET,
                "receive",
                connection=connection,
                timeout=timeout,
                correlation_id=correlation_id,
            )

        if result.get("success", False):
            message_data = result.get("data", {})
            message_str = message_data.get("message", "")

            try:
                parsed_message = json.loads(message_str) if message_str else {}

                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="receive_websocket_message SUCCESS",
                                 message_type=parsed_message.get("type"))

                result["parsed_message"] = parsed_message
            except json.JSONDecodeError as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="receive_websocket_message PARSE_FAILED", error=str(e))
                result["parsed_message"] = None
                result["parse_error"] = str(e)

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_receive_success")
            execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                             operation_name="ha_websocket_receive_duration_ms",
                             duration_ms=result.get("duration_ms", 0))
        else:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="receive_websocket_message FAILED")

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_receive_error")
            execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                             operation_name="ha_websocket_receive_error_duration_ms",
                             duration_ms=result.get("duration_ms", 0))

        return result

    except (ConnectionError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as e:
        # Expected receive errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="receive_websocket_message FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket receive failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_receive_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_RECEIVE_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="receive_websocket_message FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket receive failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_receive_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_RECEIVE_FAILED",
        }

def websocket_request(connection: Any, message_type: str,
                     data: Optional[dict] = None, timeout: int = 10) -> dict[str, Any]:
    """Send WebSocket request and wait for response."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="websocket_request START", message_type=message_type)

        message = {
            "type": message_type,
            "id": correlation_id,
        }

        if data:
            message.update(data)

        timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                     corr_id=correlation_id,
                                     operation_name="websocket_request")

        with timing_ctx:
            # Send request
            send_result = send_websocket_message(connection, message)

            if not send_result.get("success"):
                return send_result

            # Wait for response with matching ID
            start_time = time.time()
            while time.time() - start_time < timeout:
                receive_result = receive_websocket_message(connection, timeout=1)

                if receive_result.get("success"):
                    parsed_message = receive_result.get("parsed_message", {})

                    # Check if this is our response
                    if parsed_message.get("id") == correlation_id:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                                         message="websocket_request SUCCESS")

                        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                         metric_name="ha_websocket_request_success")
                        execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                                         operation_name="ha_websocket_request_duration_ms",
                                         duration_ms=int((time.time() - start_time) * 1000))

                        return {
                            "success": True,
                            "message": f"WebSocket request completed: {message_type}",
                            "response": parsed_message,
                        }
                    if parsed_message.get("type") == "error":
                        execute_operation(GatewayInterface.DEBUG, "log",
                                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                                         message="websocket_request FAILED - Error response")

                        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                         metric_name="ha_websocket_request_error")

                        return {
                            "success": False,
                            "error": parsed_message.get("error", "Unknown WebSocket error"),
                            "error_code": "WEBSOCKET_ERROR_RESPONSE",
                            "response": parsed_message,
                        }

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="websocket_request FAILED - Timeout")

            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_request_timeout")

            return {
                "success": False,
                "error": f"WebSocket request timeout after {timeout}s",
                "error_code": "WEBSOCKET_TIMEOUT",
            }

    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError, json.JSONDecodeError) as e:
        # Expected request errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="websocket_request FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket request failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_request_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_REQUEST_FAILED",
        }
    except Exception as e:
        # Unexpected errors
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="websocket_request FAILED", error=str(e))

        execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket request failed: {e!s}")
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                         metric_name="ha_websocket_request_exception")

        return {
            "success": False,
            "error": str(e),
            "error_code": "WEBSOCKET_REQUEST_FAILED",
        }


__all__ = [
    "receive_websocket_message",
    "send_websocket_message",
    "websocket_request",
]

# EOF
