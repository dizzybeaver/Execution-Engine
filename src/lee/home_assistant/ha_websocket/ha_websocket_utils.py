"""ha_websocket_utils.py - WebSocket Utility Functions
Version: 3.0.1
Description: WebSocket utility functions and helpers

Split from ha_websocket.py (498 lines) to meet AWS Lambda 350-line limit.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.home_assistant.ha_websocket.ha_websocket_connection import (
    establish_websocket_connection,
    close_websocket_connection,
)

# Cache environment variable at module load time
# For AWS Lambda: Read from environment variable set by Lambda configuration
# For local testing: .env file should set this via environment variable
_WEBSOCKET_ENABLED = os.getenv("HA_WEBSOCKET_ENABLED", "false").lower() == "true"


def is_websocket_enabled() -> bool:
    """Check if WebSocket functionality is enabled (cached value)."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="is_websocket_enabled COMPLETE",
                         enabled=_WEBSOCKET_ENABLED)

        return _WEBSOCKET_ENABLED

    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         message="is_websocket_enabled FAILED", error=str(e))

        # Default to disabled on error
        return False


def get_websocket_timeout() -> int:
    """Get WebSocket timeout from environment."""
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_timeout START")

        # For AWS Lambda: Read from environment variable set by Lambda configuration
        # For local testing: .env file should set this via environment variable
        try:
            timeout = int(os.getenv("HA_WEBSOCKET_TIMEOUT", "10"))
        except ValueError:
            timeout = 10  # Fallback to default if invalid

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_timeout COMPLETE", timeout=timeout)

        return timeout

    except (ValueError, TypeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_timeout FAILED - Invalid timeout", error=str(e))

        # Default to 10 seconds on error
        return 10


def validate_websocket_url(url: str) -> dict[str, Any]:
    """Validate WebSocket URL format.
        url: WebSocket URL to validate

        Validation result with success status and normalized URL

    """
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="validate_websocket_url START", url=url[:50])

        if not url:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="validate_websocket_url FAILED - Empty URL")
            return {
                "success": False,
                "error": "WebSocket URL cannot be empty",
                "error_code": "EMPTY_URL",
            }

        # Check URL format
        if not (url.startswith("ws://") or url.startswith("wss://")):
            # Try to convert HTTP/HTTPS to WebSocket protocol
            if url.startswith("http://"):
                normalized_url = url.replace("http://", "ws://")
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="validate_websocket_url CONVERTED", original="http://", normalized="ws://")
            elif url.startswith("https://"):
                normalized_url = url.replace("https://", "wss://")
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="validate_websocket_url CONVERTED", original="https://", normalized="wss://")
            else:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="validate_websocket_url FAILED - Invalid protocol")
                return {
                    "success": False,
                    "error": "URL must start with ws://, wss://, http://, or https://",
                    "error_code": "INVALID_PROTOCOL",
                }
        else:
            normalized_url = url

        # Basic URL structure validation
        if "://" not in normalized_url:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="validate_websocket_url FAILED - Missing protocol")
            return {
                "success": False,
                "error": "URL must include protocol",
                "error_code": "MISSING_PROTOCOL",
            }

        # Check for required WebSocket endpoint
        if not normalized_url.endswith("/api/websocket"):
            if normalized_url.endswith("/"):
                normalized_url += "api/websocket"
            else:
                normalized_url += "/api/websocket"

            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="validate_websocket_url NORMALIZED", added_endpoint="/api/websocket")

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="validate_websocket_url SUCCESS", normalized_url=normalized_url)

        return {
            "success": True,
            "normalized_url": normalized_url,
            "original_url": url,
        }

    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="validate_websocket_url FAILED", error=str(e))

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket URL validation failed: {e!s}")
        except (AttributeError, RuntimeError):
            # Logging unavailable during error handling - main error already captured
            ...

        return {
            "success": False,
            "error": str(e),
            "error_code": "VALIDATION_EXCEPTION",
        }


def get_websocket_connection_info(ha_config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Get WebSocket connection information from HA configuration.

        ha_config: Optional HA configuration (loaded if not provided)

        WebSocket connection info with URL and parameters

    """
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_connection_info START")

        # FIXED: Removed direct imports - use execute_operation instead
        if ha_config is None:
            ha_config = execute_operation(GatewayInterface.CONFIG, 'get_ha_config')

        base_url = ha_config.get("base_url", "")
        access_token = ha_config.get("access_token", "")
        timeout = ha_config.get("timeout", 10)

        if not base_url:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_websocket_connection_info FAILED - No base URL")
            return {
                "success": False,
                "error": "Home Assistant base URL not configured",
                "error_code": "NO_BASE_URL",
            }

        # Convert to WebSocket URL
        ws_result = validate_websocket_url(base_url)

        if not ws_result.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_websocket_connection_info FAILED - Invalid URL")
            return ws_result

        ws_url = ws_result.get("normalized_url")

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_connection_info SUCCESS",
                         ws_url=ws_url[:50], has_token=bool(access_token))

        return {
            "success": True,
            "ws_url": ws_url,
            "access_token": access_token,
            "timeout": timeout,
            "has_access_token": bool(access_token),
        }

    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_websocket_connection_info FAILED", error=str(e))

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] Get WebSocket connection info failed: {e!s}")
        except Exception as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'Exception occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

        return {
            "success": False,
            "error": str(e),
            "error_code": "CONNECTION_INFO_EXCEPTION",
        }


def check_websocket_availability(ha_config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Check if WebSocket endpoint is available.


        Availability check result

    """
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_websocket_availability START")

        # FIXED: Removed direct imports - use execute_operation instead
        # Get connection info via gateway
        conn_info_result = get_websocket_connection_info(ha_config)

        if not conn_info_result.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="check_websocket_availability FAILED - Connection info")
            return conn_info_result

        ws_url = conn_info_result.get("ws_url")
        timeout = conn_info_result.get("timeout", 10)

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_websocket_availability TESTING", ws_url=ws_url[:50])

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=correlation_id,
                                         operation_name="check_websocket_availability")
        except ImportError:
            from contextlib import nullcontext
            timing_ctx = nullcontext()

        with timing_ctx:
            # Try to establish connection (without auth)
            conn_result = establish_websocket_connection(ws_url, timeout=timeout)

        if conn_result.get("success"):
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="check_websocket_availability SUCCESS")

            try:
                execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                                 metric_name="ha_websocket_availability_success")
                execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                                 operation_name="ha_websocket_availability_check_duration_ms",
                                 duration_ms=conn_result.get("duration_ms", 0))
            except ImportError as e:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_warning',
                        message=f'Module import failed: {e}',
                        corr_id=None
                    )
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Gateway not available

            # Close the test connection
            try:
                close_websocket_connection(conn_result.get("connection"))
            except Exception as e:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     message="WebSocket close error during availability check",
                                     error=str(e))
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Debug not available

            return {
                "success": True,
                "message": "WebSocket endpoint is available",
                "ws_url": ws_url,
                "connection_time_ms": conn_result.get("duration_ms", 0),
            }
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_websocket_availability FAILED")

        try:
            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_availability_failed")
            execute_operation(GatewayInterface.OBSERVABILITY, "timing",
                             operation_name="ha_websocket_availability_check_error_duration_ms",
                             duration_ms=conn_result.get("duration_ms", 0))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        return {
            "success": False,
            "error": "WebSocket endpoint not available",
            "error_code": "WEBSOCKET_UNAVAILABLE",
            "ws_url": ws_url,
            "connection_result": conn_result,
        }

    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="check_websocket_availability FAILED", error=str(e))

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] WebSocket availability check failed: {e!s}")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                             metric_name="ha_websocket_availability_exception")
        except ImportError as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_warning',
                    message=f'Module import failed: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available

        return {
            "success": False,
            "error": str(e),
            "error_code": "AVAILABILITY_CHECK_EXCEPTION",
        }


__all__ = [
    "check_websocket_availability",
    "get_websocket_connection_info",
    "get_websocket_timeout",
    "is_websocket_enabled",
    "validate_websocket_url",
]

# EOF
