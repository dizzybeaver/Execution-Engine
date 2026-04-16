# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract HA API functions from ha_interconnect.py

"""ha_api.py - Home Assistant REST API Functions
Version: 2025-03-02_1
Purpose: Direct Home Assistant REST API calls

This module handles:
- Direct HA REST API calls
- Token and URL resolution
- HTTP method dispatch

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_interconnect.http_handlers import HTTP_METHOD_HANDLERS
from lee.home_assistant.ha_interconnect.utils import (
    generate_ha_correlation_id,
    log_debug,
    log_error,
    metrics_increment,
)
from lee.home_assistant.http_client import HomeAssistantHTTP


def devices_call_ha_api(endpoint: str, method: str = "GET", data: Any = None,
                       oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Call Home Assistant REST API endpoint directly.

    This function is used by ha_alexa_generic.py for discovery.

    Args:
        endpoint: API endpoint path (e.g., '/api/alexa/smart_home')
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body data
        oauth_token: LWA OAuth token for authentication
        **kwargs: Additional HTTP options (headers, timeout, etc.)

    Returns:
        {
            'success': bool,
            'data': Any,  # Response data if successful
            'error': str  # Error message if failed
        }
    """
    import os
    import time

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    api_start = None
    if os.environ.get("LEE_DEBUG", "false").lower() == "true":
        api_start = time.perf_counter()
        log_debug(f"devices_call_ha_api ENTRY - endpoint={endpoint} method={method}", corr_id=corr_id, scope="HA_API")

    try:
        log_debug(f"[{corr_id}] Calling HA API: {method} {endpoint}")

        # Get HA URL from config
        ha_url = None
        try:
            ha_url = execute_operation(GatewayInterface.CONFIG, "get", key="ha_url")
        except (KeyError, AttributeError, NameError, TypeError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_debug",
                           message=f"Config key 'ha_url' not found: {e}",
                           scope="ha_interconnect",
                           config_key="ha_url")
        except (RuntimeError, MemoryError) as e:
            # Runtime or memory errors during config access
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Runtime error accessing 'ha_url': {e}",
                           scope="ha_interconnect",
                           config_key="ha_url",
                           error=str(e))
            raise

        if not ha_url:
            try:
                ha_url = execute_operation(GatewayInterface.CONFIG, "get", key="HOME_ASSISTANT_URL")
            except (KeyError, AttributeError, NameError, TypeError) as e:
                execute_operation(GatewayInterface.LOGGING, "log_debug",
                               message=f"Config key 'HOME_ASSISTANT_URL' not found: {e}",
                               scope="ha_interconnect",
                               config_key="HOME_ASSISTANT_URL")
            except (RuntimeError, MemoryError) as e:
                # Runtime or memory errors during config access
                execute_operation(GatewayInterface.LOGGING, "log_error",
                               message=f"Runtime error accessing 'HOME_ASSISTANT_URL': {e}",
                               scope="ha_interconnect",
                               config_key="HOME_ASSISTANT_URL",
                               error=str(e))
                raise

        if not ha_url:
            return {
                "success": False,
                "error": "Home Assistant URL not configured",
            }

        # Priority order for Home Assistant authentication:
        # 1. HOME_ASSISTANT_API_KEY (long-lived token) - PRIMARY if set
        # 2. ha_token (config fallback)
        # 3. oauth_token parameter (LWA OAuth - only used if above not available)
        #
        # NOTE: oauth_token is from Alexa LWA and should NOT be used for HA auth
        # unless absolutely necessary (OAuth flow compatibility)

        token = None

        # Check 1: HOME_ASSISTANT_API_KEY (long-lived access token) - HIGHEST PRIORITY
        try:
            token = execute_operation(GatewayInterface.CONFIG, "get", key="HOME_ASSISTANT_API_KEY")
            if token:
                log_debug(f"[{corr_id}] Using HOME_ASSISTANT_API_KEY for authentication")
        except (KeyError, AttributeError, NameError, TypeError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_debug",
                           message=f"Config key 'HOME_ASSISTANT_API_KEY' not found: {e}",
                           scope="ha_interconnect",
                           config_key="HOME_ASSISTANT_API_KEY")
        except (ValueError, RuntimeError, MemoryError) as e:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Config error for 'HOME_ASSISTANT_API_KEY': {e}",
                           scope="ha_interconnect",
                           config_key="HOME_ASSISTANT_API_KEY",
                           error=str(e))

        # Check 2: ha_token (config fallback)
        if not token:
            try:
                token = execute_operation(GatewayInterface.CONFIG, "get", key="ha_token")
                if token:
                    log_debug(f"[{corr_id}] Using ha_token for authentication")
            except (KeyError, AttributeError, NameError, TypeError) as e:
                execute_operation(GatewayInterface.LOGGING, "log_debug",
                               message=f"Config key 'ha_token' not found: {e}",
                               scope="ha_interconnect",
                               config_key="ha_token")
            except (ValueError, RuntimeError, MemoryError) as e:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                               message=f"Config error for 'ha_token': {e}",
                               scope="ha_interconnect",
                               config_key="ha_token",
                               error=str(e))

        # Check 3: oauth_token parameter (LOWEST PRIORITY - only if nothing else available)
        # WARNING: This is the LWA OAuth token and should NOT be used for HA authentication
        if not token and oauth_token:
            log_debug(f"[{corr_id}] WARNING: Using oauth_token (LWA) for HA authentication - NOT RECOMMENDED")
            token = oauth_token

        if not token:
            return {
                "success": False,
                "error": "No authentication token available",
            }

        # Make HTTP request using dictionary dispatch (O(1) lookup)
        # Extract host from URL (format: https://hostname:port/path)
        from urllib.parse import urlparse
        parsed = urlparse(ha_url)
        host = parsed.hostname or parsed.netloc.split(':')[0]
        http = HomeAssistantHTTP(host=host, token=token, use_ssl=parsed.scheme == 'https', port=parsed.port)

        handler = HTTP_METHOD_HANDLERS.get(method.upper())
        if handler is None:
            return {
                "success": False,
                "error": f"Unsupported HTTP method: {method}",
            }

        response = handler(http, endpoint, data, **kwargs)

        metrics_increment("ha_api_call_success", endpoint=endpoint, method=method)
        log_debug(f"[{corr_id}] HA API call successful")

        if os.environ.get("LEE_DEBUG", "false").lower() == "true" and api_start is not None:
            api_duration_ms = (time.perf_counter() - api_start) * 1000
            log_debug(f"devices_call_ha_api EXIT - endpoint={endpoint} method={method} "
                  f"duration_ms={api_duration_ms:.2f} success=True corr_id={corr_id}")

        return {
            "success": True,
            "data": response,
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        log_error(f"[{corr_id}] Network error in HA API call: {e!s}")
        metrics_increment("ha_api_call_error", endpoint=endpoint, method=method)
        if os.environ.get("LEE_DEBUG", "false").lower() == "true" and api_start is not None:
            api_duration_ms = (time.perf_counter() - api_start) * 1000
            log_debug(f"devices_call_ha_api EXIT - endpoint={endpoint} method={method} "
                  f"duration_ms={api_duration_ms:.2f} error=Network:{type(e).__name__} corr_id={corr_id}")
        return {
            "success": False,
            "error": str(e),
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        log_error(f"[{corr_id}] Data error in HA API call: {e!s}")
        metrics_increment("ha_api_call_error", endpoint=endpoint, method=method)
        if os.environ.get("LEE_DEBUG", "false").lower() == "true" and api_start is not None:
            api_duration_ms = (time.perf_counter() - api_start) * 1000
            log_debug(f"devices_call_ha_api EXIT - endpoint={endpoint} method={method} "
                  f"duration_ms={api_duration_ms:.2f} error=Data:{type(e).__name__} corr_id={corr_id}")
        return {
            "success": False,
            "error": str(e),
        }
    except Exception as e:
        log_error(f"[{corr_id}] HA API call failed: {e!s}")
        metrics_increment("ha_api_call_error", endpoint=endpoint, method=method)

        if os.environ.get("LEE_DEBUG", "false").lower() == "true" and api_start is not None:
            api_duration_ms = (time.perf_counter() - api_start) * 1000
            log_debug(f"devices_call_ha_api EXIT - endpoint={endpoint} method={method} "
                  f"duration_ms={api_duration_ms:.2f} error=Unexpected:{type(e).__name__} corr_id={corr_id}")

        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "devices_call_ha_api",
]
