# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - API helper functions for HA devices

"""ha_devices_helpers.py - Helper functions for Home Assistant API calls

Provides utility functions for direct HA API interactions and
configuration retrieval.
"""

import threading
import time
from collections import defaultdict
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation

# ===== MODULE-LEVEL HTTP METHOD DISPATCH HANDLERS =====

def _method_get(ha_http, endpoint, _data):
    """Handler for GET requests."""
    return ha_http.get(endpoint)


def _method_post(ha_http, endpoint, data):
    """Handler for POST requests."""
    return ha_http.post(endpoint, json=data or {})


def _method_put(ha_http, endpoint, data):
    """Handler for PUT requests."""
    return ha_http.put(endpoint, json=data or {})


def _method_delete(ha_http, endpoint, data):
    """Handler for DELETE requests."""
    return ha_http.delete(endpoint)


# Dispatch dictionary for HTTP methods (O(1) lookup)
_METHOD_HANDLERS = {
    "GET": _method_get,
    "POST": _method_post,
    "PUT": _method_put,
    "DELETE": _method_delete,
}


def call_ha_api_impl(endpoint: str, method: str = "GET", data: Optional[dict] = None,
                    oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Call Home Assistant API directly.

    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body data
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status and response data
    """
    try:
        from lee.home_assistant.http_client import HomeAssistantHTTP

        ha_url = kwargs.get("ha_url", "homeassistant.local")
        ha_token = oauth_token or kwargs.get("ha_token")

        if ha_token is None or ha_token == "":
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN"
            }

        with HomeAssistantHTTP(host=ha_url, token=ha_token) as ha_http:
            # Dictionary dispatch for HTTP methods (O(1) lookup)
            handler = _METHOD_HANDLERS.get(method)
            if handler is None:
                return {
                    "success": False,
                    "error": f"Invalid HTTP method: {method}",
                    "error_code": "INVALID_METHOD"
                }

            response = handler(ha_http, endpoint, data)

            result_data = response.json() if response.content else {}

        return {
            "success": True,
            "data": result_data,
            "status_code": response.status_code
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"call_ha_api network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"call_ha_api validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"call_ha_api config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"call_ha_api failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "CALL_HA_API_ERROR"
        }


def get_ha_config_impl(force_reload: bool = False, **kwargs) -> dict[str, Any]:
    """Get Home Assistant configuration.

    Args:
        force_reload: Force reload from HA (ignore cache)
        **kwargs: Additional parameters

    Returns:
        Dict with success status and configuration data
    """
    try:
        oauth_token = kwargs.get("oauth_token")
        result = call_ha_api_impl("config", "GET", None, oauth_token, **kwargs)

        if result.get("success"):
            return {
                "success": True,
                "config": result.get("data"),
                "cached": not force_reload
            }
        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_ha_config network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_ha_config validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_ha_config config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_ha_config failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_HA_CONFIG_ERROR"
        }


# Rate limiting statistics
_rate_limit_stats = defaultdict(lambda: {
    "calls": [],
    "total_calls": 0,
    "last_call": None,
    "errors": 0
})
_stats_lock = threading.Lock()  # Thread safety for rate limit stats


def track_api_call(endpoint: str, success: bool = True, response_time: float = 0.0) -> None:
    """Track an API call for rate limit statistics.

    Args:
        endpoint: API endpoint called (e.g., "states", "services/light/turn_on")
        success: Whether the call was successful
        response_time: Response time in seconds

    Thread Safety: Uses lock to prevent concurrent modification of stats
    """
    try:
        now = time.time()

        with _stats_lock:
            # Keep only last 100 calls per endpoint for memory management
            if len(_rate_limit_stats[endpoint]["calls"]) >= 100:
                _rate_limit_stats[endpoint]["calls"].pop(0)

            _rate_limit_stats[endpoint]["calls"].append({
                "timestamp": now,
                "success": success,
                "response_time": response_time
            })
            _rate_limit_stats[endpoint]["total_calls"] += 1
            _rate_limit_stats[endpoint]["last_call"] = now

            if not success:
                _rate_limit_stats[endpoint]["errors"] += 1

    except (ValueError, TypeError, KeyError) as e:
        # Tracking failures should not break the application
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Failed to track API call (data error): {str(e)}")
    except Exception as e:
        # Tracking failures should not break the application
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Failed to track API call: {str(e)}")


def get_rate_limit_stats(window_seconds: int = 60) -> dict[str, Any]:
    """Get rate limiting statistics for Home Assistant API calls.

    Tracks API call frequency, success rates, and response times to monitor
    usage patterns and detect potential issues.

    Args:
        window_seconds: Time window for rate calculation (default: 60 seconds)

    Returns:
        Dict with rate limit statistics including:
        - total_calls: Total API calls tracked
        - endpoints: Stats per endpoint
        - calls_per_minute: Calculated rate
        - error_rate: Percentage of failed calls

    Thread Safety: Uses lock to prevent race conditions during stats read
    """
    try:
        now = time.time()
        window_start = now - window_seconds

        total_calls_all = 0
        calls_in_window = 0
        errors_in_window = 0
        endpoint_stats = {}

        with _stats_lock:
            for endpoint, stats in _rate_limit_stats.items():
                # Count calls in time window
                recent_calls = [
                    call for call in stats["calls"]
                    if call["timestamp"] >= window_start
                ]

                recent_errors = sum(1 for call in recent_calls if not call["success"])
                recent_success = len(recent_calls) - recent_errors

                # Calculate average response time for successful calls
                successful_calls = [call for call in recent_calls if call["success"]]
                avg_response_time = (
                    sum(call["response_time"] for call in successful_calls) / len(successful_calls)
                    if successful_calls else 0.0
                )

                total_calls_all += stats["total_calls"]
                calls_in_window += len(recent_calls)
                errors_in_window += recent_errors

                endpoint_stats[endpoint] = {
                    "total_calls": stats["total_calls"],
                    "calls_in_window": len(recent_calls),
                    "errors_in_window": recent_errors,
                    "success_rate": (
                        (recent_success / len(recent_calls) * 100)
                        if recent_calls else 100.0
                    ),
                    "avg_response_time": round(avg_response_time, 3),
                    "last_call": stats["last_call"],
                    "calls_per_minute": round(len(recent_calls) / (window_seconds / 60), 2)
                }

        # Calculate overall stats
        overall_error_rate = (
            (errors_in_window / calls_in_window * 100)
            if calls_in_window > 0 else 0.0
        )
        calls_per_minute = round(calls_in_window / (window_seconds / 60), 2)

        return {
            "success": True,
            "total_calls": total_calls_all,
            "calls_in_window": calls_in_window,
            "calls_per_minute": calls_per_minute,
            "error_rate": round(overall_error_rate, 2),
            "window_seconds": window_seconds,
            "endpoints": endpoint_stats,
            "timestamp": now
        }

    except (ValueError, TypeError, KeyError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_rate_limit_stats data error: {str(e)}")
        return {
            "success": False,
            "error": f"Data error: {e}",
            "error_code": "DATA_ERROR"
        }
    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"get_rate_limit_stats failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "STATS_ERROR"
        }


def reset_rate_limit_stats() -> dict[str, Any]:
    """Reset rate limit statistics.

    Clears all tracked API call statistics. Useful for testing or
    starting a new measurement period.

    Returns:
        Dict indicating success
    """
    try:
        _rate_limit_stats.clear()

        return {
            "success": True,
            "message": "Rate limit statistics reset"
        }

    except (ValueError, TypeError, KeyError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"reset_rate_limit_stats data error: {str(e)}")
        return {
            "success": False,
            "error": f"Data error: {e}",
            "error_code": "DATA_ERROR"
        }
    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"reset_rate_limit_stats failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "RESET_ERROR"
        }
